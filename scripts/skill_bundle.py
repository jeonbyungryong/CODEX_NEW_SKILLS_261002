"""Stdlib-only skill packaging. Never executes upstream code or configures MCP."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tempfile
from urllib.parse import quote, unquote
from urllib.request import Request, urlopen

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
LOCK = "third_party/upstream-lock.json"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def safe_path(root, relative):
    part = PurePosixPath(relative)
    if not relative or part.is_absolute() or ".." in part.parts or "\\" in relative or ":" in relative:
        raise ValueError(f"Unsafe package path: {relative}")
    result = root.joinpath(*part.parts)
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes root: {relative}")
    return result


def reject_links(path):
    # Check original components before resolve(), which otherwise hides links.
    for item in (path, *path.parents):
        if item.is_symlink() or getattr(item, "is_junction", lambda: False)():
            raise ValueError(f"Linked paths are not supported: {item}")


def package_files(path):
    reject_links(path)
    result = {}
    for item in sorted(path.rglob("*")):
        reject_links(item)
        if item.is_file():
            result[item.relative_to(path).as_posix()] = hashlib.sha256(item.read_bytes()).hexdigest()
    return result


def skill_name(path):
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        raise ValueError(f"Missing frontmatter: {path}")
    header = text.split("---", 2)[1]
    match = re.search(r"(?m)^name:\s*([^\r\n]+)", header)
    if not match or not re.search(r"(?m)^description:\s*\S", header):
        raise ValueError(f"Missing name/description: {path}")
    return match[1].strip().strip("\"'")


def catalog(root):
    config = read_json(root / "bundle.json")
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported bundle schema")
    names = list(config["local_skills"])
    for source in config["sources"]:
        names.extend(source["skills"])
    if len(set(x.casefold() for x in names)) != len(names):
        raise ValueError("Duplicate skill identity")
    if any(not NAME.fullmatch(x) or len(x) >= 64 for x in names):
        raise ValueError("Invalid skill name")
    source_ids = [x["id"] for x in config["sources"]]
    if len(set(source_ids)) != len(source_ids) or any(not NAME.fullmatch(x) for x in source_ids):
        raise ValueError("Invalid/duplicate source ID")
    return names


def check_lock(root):
    if not (root / LOCK).exists():
        return
    lock = read_json(root / LOCK)
    config = read_json(root / "bundle.json")
    owned_prefixes = [f"skills/{name}/" for source in config["sources"] for name in source["skills"]]
    owned_prefixes += [f"third_party/{source['id']}/" for source in config["sources"]]
    for relative, expected in lock["files"].items():
        if not any(relative.startswith(prefix) for prefix in owned_prefixes):
            raise ValueError(f"Lock claims an unowned file: {relative}")
        path = safe_path(root, relative)
        reject_links(path)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Upstream hash mismatch: {relative}")
    for source in read_json(root / "bundle.json")["sources"]:
        if source["id"] not in lock["sources"]:
            raise ValueError(f"Missing provenance: {source['id']}")
        for name in source["skills"]:
            prefix = f"skills/{name}/"
            expected = {x[len(prefix):]: h for x, h in lock["files"].items() if x.startswith(prefix)}
            if not expected or package_files(root / "skills" / name) != expected:
                raise ValueError(f"Unexpected or missing upstream files: {name}")


def validate(root):
    root = Path(root).resolve()
    names = catalog(root)
    discovered = sorted(x.parent.name for x in (root / "skills").glob("*/SKILL.md"))
    if discovered != sorted(names):
        raise ValueError("Install catalog and discovered skill packages disagree")
    for name in names:
        package = root / "skills" / name
        package_files(package)
        if skill_name(package / "SKILL.md") != name:
            raise ValueError(f"Folder and frontmatter name disagree: {name}")
        text = (package / "SKILL.md").read_text(encoding="utf-8-sig")
        for target in re.findall(r"\]\(([^\s)]+)\)", text):
            target = unquote(target.split("#", 1)[0])
            if not target or "://" in target or target.startswith(("mailto:", "/")):
                continue
            reference = (package / target).resolve()
            if not reference.is_relative_to(root) or not reference.exists():
                raise ValueError(f"Missing local skill reference: {name}: {target}")
    if read_json(root / "bundle.json")["sources"] and not (root / LOCK).exists():
        raise ValueError("Upstream provenance lock is missing")
    check_lock(root)
    return names


def install(root, dest, apply=False):
    root, dest = Path(root).resolve(), Path(dest).absolute()
    names = validate(root)
    reject_links(dest)
    dest = dest.resolve()
    if dest.is_relative_to(root) or root.is_relative_to(dest):
        raise ValueError("Installation destination must not overlap the source repository")
    identities = {}
    for entry in dest.glob("*/SKILL.md"):
        reject_links(entry)
        try:
            identity = skill_name(entry).casefold()
        except ValueError:
            continue  # An occupied target folder is still a conflict below.
        identities.setdefault(identity, []).append(entry.parent)
    rows = []
    for name in names:
        target = dest / name
        reject_links(target)
        foreign = [x for x in identities.get(name.casefold(), []) if x != target]
        if foreign:
            status = "conflict"
        elif target.exists():
            status = "identical" if target.is_dir() and package_files(target) == package_files(root / "skills" / name) else "conflict"
        else:
            status = "missing"
        rows.append({"name": name, "status": status})
    if any(x["status"] == "conflict" for x in rows):
        return {"status": "conflict", "skills": rows, "written": []}
    written = []
    if apply:
        dest.mkdir(parents=True, exist_ok=True)
        for row in rows:
            if row["status"] == "missing":
                # copytree reserves the new folder and refuses even an empty existing one.
                shutil.copytree(root / "skills" / row["name"], dest / row["name"])
                written.append(row["name"])
    return {"status": "installed" if apply else "planned", "skills": rows, "written": written}


def download(url, api=False):
    headers = {"User-Agent": "CODEX_NEW_SKILLS_261002-updater"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if api and token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=45) as response:
        data = response.read(16 * 1024 * 1024 + 1)
    if len(data) > 16 * 1024 * 1024:
        raise ValueError("Upstream response exceeds download limit")
    return json.loads(data) if api else data


def api(repo, endpoint):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid upstream repository")
    return download(f"https://api.github.com/repos/{repo}/{endpoint}", api=True)


def upstream_skill_mappings(source, inventory):
    if source.get("layout") == "repository-root":
        if len(source["skills"]) != 1 or source["root"] != ".":
            raise ValueError("Repository-root layout requires one skill and root '.'")
        if "SKILL.md" not in inventory:
            raise ValueError("Upstream skill removed/renamed: repository root")
        name = source["skills"][0]
        return {f"skills/{name}/{path}": path for path in inventory}, [name]
    if source.get("layout", "skill-directories") != "skill-directories":
        raise ValueError("Unsupported upstream skill layout")
    mappings = {}
    prefix = source["root"].rstrip("/") + "/"
    available = sorted(p[len(prefix):].split("/")[0] for p in inventory
                       if p.startswith(prefix) and p.count("/") == prefix.count("/") + 1 and p.endswith("/SKILL.md"))
    for name in source["skills"]:
        directory = prefix + name + "/"
        if directory + "SKILL.md" not in inventory:
            raise ValueError(f"Upstream skill removed/renamed: {name}")
        for path in inventory:
            if path.startswith(directory):
                mappings[f"skills/{name}/{path[len(directory):]}"] = path
        mappings.setdefault(f"skills/{name}/LICENSE", "LICENSE")
    return mappings, available


def sync(root, bootstrap=False):
    root = Path(root).resolve()
    config = read_json(root / "bundle.json")
    catalog(root)
    old = read_json(root / LOCK) if (root / LOCK).exists() else None
    if old:
        validate(root)  # Never replace locally edited upstream packages silently.
    elif not bootstrap:
        raise ValueError("First import requires reviewed sources and --bootstrap")
    commits = {}
    for source in config["sources"]:
        sha = api(source["repo"], f"commits/{quote(source['ref'], safe='')}")["sha"]
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("Unexpected upstream commit identity")
        commits[source["id"]] = sha
    if old and all(old["sources"][key]["commit"] == sha for key, sha in commits.items()):
        return {"changed": False, "commits": commits}

    blobs, origins, provenance = {}, {}, {}
    for source in config["sources"]:
        repo, sid = source["repo"], source["id"]
        sha = commits[sid]
        tree = api(repo, f"git/trees/{sha}?recursive=1")
        if tree.get("truncated"):
            raise ValueError(f"Incomplete upstream inventory: {repo}")
        inventory = {x["path"]: x for x in tree["tree"] if x["type"] == "blob"}
        mappings, available = upstream_skill_mappings(source, inventory)
        mappings.update(source.get("extra_files", {}))
        mappings[f"third_party/{sid}/LICENSE"] = "LICENSE"
        mappings[f"third_party/{sid}/README.md"] = "README.md"

        def fetch(pair):
            local, upstream = pair
            safe_path(root, local)
            if not (local.startswith(f"third_party/{sid}/") or any(local.startswith(f"skills/{n}/") for n in source["skills"])):
                raise ValueError("Upstream mapping is outside its owned scope")
            item = inventory.get(upstream)
            if not item or item["mode"] not in ("100644", "100755"):
                raise ValueError(f"Missing file or unsupported Git mode: {upstream}")
            data = download(f"https://raw.githubusercontent.com/{repo}/{sha}/{quote(upstream, safe='/')}")
            actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if actual != item["sha"]:
                raise ValueError(f"Git blob identity mismatch: {upstream}")
            return local, upstream, data

        with ThreadPoolExecutor(max_workers=8) as pool:
            for local, upstream, data in pool.map(fetch, mappings.items()):
                if local in blobs:
                    raise ValueError(f"Overlapping upstream ownership: {local}")
                blobs[local] = data
                origins[local] = {"source": sid, "path": upstream}
        license_data = blobs[f"third_party/{sid}/LICENSE"]
        license_hash = hashlib.sha256(license_data).hexdigest()
        if b"MIT License" not in license_data:
            raise ValueError(f"License requires review: {repo}")
        if old and old["sources"][sid]["license_sha256"] != license_hash:
            raise ValueError(f"License changed; review required: {repo}")
        provenance[sid] = {"repo": repo, "ref": source["ref"], "commit": sha,
                           "license": "MIT", "license_sha256": license_hash,
                           "selected_skills": source["skills"], "unselected_skills": sorted(set(available) - set(source["skills"]))}

    lock = {"schema_version": 1, "sources": provenance,
            "files": {p: hashlib.sha256(data).hexdigest() for p, data in sorted(blobs.items())},
            "origins": dict(sorted(origins.items()))}
    # Validate a complete candidate BEFORE changing any repository package.
    with tempfile.TemporaryDirectory(prefix="skill-sync-") as scratch:
        stage = Path(scratch)
        write_json(stage / "bundle.json", config)
        for name in config["local_skills"]:
            shutil.copytree(root / "skills" / name, stage / "skills" / name)
        for relative, data in blobs.items():
            path = safe_path(stage, relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        write_json(stage / LOCK, lock)
        validate(stage)
    if not old:
        for source in config["sources"]:
            for name in source["skills"]:
                if (root / "skills" / name).exists():
                    raise ValueError(f"Bootstrap refuses an existing package: {name}")
    for relative, data in blobs.items():
        path = safe_path(root, relative)
        reject_links(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if old:
        for relative in old["files"].keys() - blobs.keys():
            path = safe_path(root, relative)
            reject_links(path)
            path.unlink()  # Only exact, hash-verified previously imported files.
    write_json(root / LOCK, lock)
    return {"changed": True, "commits": commits, "imported_files": len(blobs)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "install", "sync"])
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--dest", type=Path)
    parser.add_argument("--apply", action="store_true", help="Install missing packages; never overwrite")
    parser.add_argument("--bootstrap", action="store_true", help="Reviewed first import only")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            names = validate(args.root)
            result = {"status": "valid", "count": len(names), "skills": names}
        elif args.command == "sync":
            result = sync(args.root, bootstrap=args.bootstrap)
        else:
            if args.dest is None:
                parser.error("install requires an explicit --dest")
            result = install(args.root, args.dest, apply=args.apply)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 2 if result.get("status") == "conflict" else 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
