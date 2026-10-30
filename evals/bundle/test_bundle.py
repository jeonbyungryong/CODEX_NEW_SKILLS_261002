"""Package/install invariants; only disposable directories are written."""
import importlib.util
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "skill_bundle.py"
spec = importlib.util.spec_from_file_location("skill_bundle", SCRIPT)
bundle = None
if SCRIPT.exists():
    bundle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bundle)


class BundleTests(unittest.TestCase):
    def test_repository_root_skill_keeps_all_support_files(self):
        source = {"layout": "repository-root", "root": ".", "skills": ["anatomy"]}
        inventory = {name: {} for name in ["SKILL.md", "LICENSE", "kit/iso.mjs", "examples/dial/build.mjs", "agents/openai.yaml"]}
        mappings, available = bundle.upstream_skill_mappings(source, inventory)
        self.assertEqual(available, ["anatomy"])
        self.assertEqual(mappings, {"skills/anatomy/" + p: p for p in inventory})

    def test_repository_root_layout_rejects_multiple_skills(self):
        with self.assertRaisesRegex(ValueError, "one skill"):
            bundle.upstream_skill_mappings({"layout": "repository-root", "root": ".", "skills": ["alpha", "beta"]}, {"SKILL.md": {}})

    def test_repository_root_layout_rejects_missing_entrypoint(self):
        with self.assertRaisesRegex(ValueError, "removed/renamed"):
            bundle.upstream_skill_mappings({"layout": "repository-root", "root": ".", "skills": ["anatomy"]}, {"kit/iso.mjs": {}})

    def test_repository_root_sync_imports_nested_support_without_changing_local_skill(self):
        upstream = self.prepare_upstream_update()
        config = json.loads((self.repo / "bundle.json").read_text(encoding="utf-8"))
        config["sources"][0].update(layout="repository-root", root=".")
        (self.repo / "bundle.json").write_text(json.dumps(config), encoding="utf-8")
        root_files = {p.removeprefix("skills/alpha/"): data for p, data in upstream.items()}
        root_files["kit/iso.mjs"] = b"export const version = 1;\n"
        root_files["examples/dial/build.mjs"] = b"// complete upstream example\n"
        before = (self.repo / "skills/beta/SKILL.md").read_bytes()
        self.assertTrue(self.run_fake_update(root_files)["changed"])
        self.assertEqual((self.repo / "skills/alpha/kit/iso.mjs").read_bytes(), root_files["kit/iso.mjs"])
        self.assertTrue((self.repo / "skills/alpha/examples/dial/build.mjs").is_file())
        self.assertEqual((self.repo / "skills/beta/SKILL.md").read_bytes(), before)
        self.assertEqual(bundle.validate(self.repo), ["beta", "alpha"])

    def setUp(self):
        self.assertIsNotNone(bundle, "Bundle implementation is not present yet")
        self.temp = tempfile.TemporaryDirectory(prefix="skill bundle 한글 ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repository"
        self.repo.mkdir()
        (self.repo / "bundle.json").write_text(json.dumps({
            "schema_version": 1, "local_skills": ["alpha", "beta"], "sources": []
        }), encoding="utf-8")
        for name in ["alpha", "beta"]:
            package = self.repo / "skills" / name
            (package / "references").mkdir(parents=True)
            (package / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: Use when testing {name}.\n---\n"
                "[Contract](references/contract.md)\n", encoding="utf-8")
            (package / "references" / "contract.md").write_text("계약\n", encoding="utf-8")

    def test_plan_does_not_create_installation_directory(self):
        dest = self.base / "new destination"
        report = bundle.install(self.repo, dest)
        self.assertEqual([x["status"] for x in report["skills"]], ["missing", "missing"])
        self.assertFalse(dest.exists())

    def test_install_copies_support_files_and_second_run_skips(self):
        dest = self.base / "설치 대상"
        first = bundle.install(self.repo, dest, apply=True)
        self.assertEqual(first["status"], "installed")
        self.assertEqual((dest / "alpha/references/contract.md").read_text(encoding="utf-8"), "계약\n")
        before = (dest / "alpha/SKILL.md").read_bytes()
        second = bundle.install(self.repo, dest, apply=True)
        self.assertEqual([x["status"] for x in second["skills"]], ["identical", "identical"])
        self.assertEqual((dest / "alpha/SKILL.md").read_bytes(), before)

    def test_conflict_prevents_all_installation_writes(self):
        dest = self.base / "skills"
        (dest / "alpha").mkdir(parents=True)
        old = b"user-owned customization"
        (dest / "alpha/SKILL.md").write_bytes(old)
        report = bundle.install(self.repo, dest, apply=True)
        self.assertEqual(report["status"], "conflict")
        self.assertEqual((dest / "alpha/SKILL.md").read_bytes(), old)
        self.assertFalse((dest / "beta").exists())

    def test_same_frontmatter_name_in_another_folder_is_conflict(self):
        dest = self.base / "skills"
        (dest / "renamed").mkdir(parents=True)
        (dest / "renamed/SKILL.md").write_text(
            "---\nname: alpha\ndescription: existing copy\n---\n", encoding="utf-8")
        self.assertEqual(bundle.install(self.repo, dest, apply=True)["status"], "conflict")
        self.assertFalse((dest / "alpha").exists())

    def test_duplicate_casefolded_names_rejected(self):
        config = {"schema_version": 1, "local_skills": ["alpha", "alpha"], "sources": []}
        (self.repo / "bundle.json").write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaises(ValueError):
            bundle.validate(self.repo)

    def test_missing_reference_and_wrong_identity_rejected(self):
        (self.repo / "skills/alpha/references/contract.md").unlink()
        with self.assertRaises(ValueError):
            bundle.validate(self.repo)
        (self.repo / "skills/alpha/references/contract.md").write_text("restored", encoding="utf-8")
        (self.repo / "skills/alpha/SKILL.md").write_text(
            "---\nname: beta\ndescription: wrong identity\n---\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            bundle.validate(self.repo)

    def test_path_escape_and_install_over_source_rejected(self):
        with self.assertRaises(ValueError):
            bundle.install(self.repo, self.repo / "skills", apply=True)
        config = {"schema_version": 1, "local_skills": ["../outside"], "sources": []}
        (self.repo / "bundle.json").write_text(json.dumps(config), encoding="utf-8")
        with self.assertRaises(ValueError):
            bundle.validate(self.repo)

    def test_locked_upstream_file_change_is_detected(self):
        lock = {"files": {"skills/alpha/SKILL.md": "0" * 64}, "sources": {}}
        (self.repo / "third_party").mkdir()
        (self.repo / "third_party/upstream-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        with self.assertRaises(ValueError):
            bundle.validate(self.repo)

    def test_lock_cannot_claim_files_outside_imported_packages(self):
        owned = self.repo / "bundle.json"
        lock = {"files": {"bundle.json": hashlib.sha256(owned.read_bytes()).hexdigest()}, "sources": {}}
        (self.repo / "third_party").mkdir()
        (self.repo / "third_party/upstream-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        with self.assertRaises(ValueError):
            bundle.validate(self.repo)

    def test_unchanged_upstream_commits_do_not_rewrite_lock(self):
        lock_path = ROOT / "third_party/upstream-lock.json"
        before = lock_path.read_bytes()
        before_time = lock_path.stat().st_mtime_ns
        commits = {x["repo"]: x["commit"] for x in json.loads(before)["sources"].values()}
        with patch.object(bundle, "api", side_effect=lambda repo, endpoint: {"sha": commits[repo]}):
            result = bundle.sync(ROOT)
        self.assertFalse(result["changed"])
        self.assertEqual(lock_path.read_bytes(), before)
        self.assertEqual(lock_path.stat().st_mtime_ns, before_time)

    def prepare_upstream_update(self):
        config = {"schema_version": 1, "local_skills": ["beta"], "sources": [{
            "id": "sample", "repo": "example/project", "ref": "main", "root": "skills", "skills": ["alpha"]}]}
        (self.repo / "bundle.json").write_text(json.dumps(config), encoding="utf-8")
        license_data = b"MIT License\nCopyright old owner\n"
        (self.repo / "skills/alpha/LICENSE").write_bytes(license_data)
        upstream = {"skills/alpha/" + path.relative_to(self.repo / "skills/alpha").as_posix(): path.read_bytes()
                    for path in (self.repo / "skills/alpha").rglob("*") if path.is_file()}
        upstream.update({"LICENSE": license_data, "README.md": b"source readme\n"})
        (self.repo / "third_party/sample").mkdir(parents=True)
        (self.repo / "third_party/sample/LICENSE").write_bytes(license_data)
        (self.repo / "third_party/sample/README.md").write_bytes(upstream["README.md"])
        files = {path.relative_to(self.repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in self.repo.rglob("*") if path.is_file() and ("/alpha/" in path.as_posix() or "/sample/" in path.as_posix())}
        lock = {"sources": {"sample": {"commit": "a" * 40, "license_sha256": hashlib.sha256(license_data).hexdigest()}}, "files": files}
        (self.repo / "third_party/upstream-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        return upstream

    def run_fake_update(self, upstream):
        sha = "b" * 40
        tree = {"truncated": False, "tree": [{"path": path, "type": "blob", "mode": "100644",
                "sha": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()}
                for path, data in upstream.items()]}
        def response(repo, endpoint):
            return {"sha": sha} if endpoint.startswith("commits/") else tree
        with patch.object(bundle, "api", side_effect=response), patch.object(
                bundle, "download", side_effect=lambda url: upstream[url.split("/" + sha + "/", 1)[1]]):
            return bundle.sync(self.repo)

    def test_license_change_stops_before_repository_writes(self):
        upstream = self.prepare_upstream_update()
        before = {p.relative_to(self.repo): p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}
        upstream["LICENSE"] = b"MIT License\nCopyright new terms need review\n"
        with self.assertRaisesRegex(ValueError, "License changed"):
            self.run_fake_update(upstream)
        self.assertEqual({p.relative_to(self.repo): p.read_bytes() for p in self.repo.rglob("*") if p.is_file()}, before)

    def test_missing_new_reference_stops_before_repository_writes(self):
        upstream = self.prepare_upstream_update()
        old_skill = (self.repo / "skills/alpha/SKILL.md").read_bytes()
        upstream.pop("skills/alpha/references/contract.md")
        with self.assertRaisesRegex(ValueError, "Missing local skill reference"):
            self.run_fake_update(upstream)
        self.assertEqual((self.repo / "skills/alpha/SKILL.md").read_bytes(), old_skill)
        self.assertTrue((self.repo / "skills/alpha/references/contract.md").exists())

    def test_valid_update_preserves_local_skill_and_imports_complete_package(self):
        upstream = self.prepare_upstream_update()
        local_before = (self.repo / "skills/beta/SKILL.md").read_bytes()
        upstream["skills/alpha/references/contract.md"] = b"updated upstream reference\n"
        self.assertTrue(self.run_fake_update(upstream)["changed"])
        self.assertEqual((self.repo / "skills/alpha/references/contract.md").read_bytes(), b"updated upstream reference\n")
        self.assertEqual((self.repo / "skills/beta/SKILL.md").read_bytes(), local_before)
        self.assertEqual(bundle.validate(self.repo), ["beta", "alpha"])

    def test_real_catalog_complete_and_installable(self):
        names = bundle.validate(ROOT)
        self.assertEqual(len(names), 27)
        self.assertEqual(len(set(names)), 27)
        self.assertIn("image-to-cad", names)
        self.assertIn("solidworks-dwg-to-native", names)
        self.assertIn("cad", names)
        self.assertIn("reverse-engineer-anything", names)
        self.assertIn("anatomy", names)
        dest = self.base / "actual 27 packages"
        self.assertEqual(bundle.install(ROOT, dest, apply=True)["status"], "installed")
        self.assertEqual(len(list(dest.glob("*/SKILL.md"))), 27)
        for relative in ["image-to-cad/scripts/reconstruct_geometry.py",
                         "image-to-cad/scripts/pdf_semantics.py",
                         "solidworks-dwg-to-native/references/solidworks-native.md",
                         "solidworks-dwg-to-native/references/environment-setup.md"]:
            self.assertEqual((dest / relative).read_bytes(), (ROOT / "skills" / relative).read_bytes())
        self.assertEqual((dest / "cad/references/step-generation.md").read_bytes(),
                         (ROOT / "skills/cad/references/step-generation.md").read_bytes())
        self.assertTrue(all(x["status"] == "identical" for x in bundle.install(ROOT, dest)["skills"]))

    def test_cli_validation_and_conflict_exit_code(self):
        valid = subprocess.run([sys.executable, "-B", str(SCRIPT), "validate", "--root", str(ROOT)], capture_output=True)
        self.assertEqual(valid.returncode, 0, valid.stderr)
        dest = self.base / "cli skills"
        (dest / "alpha").mkdir(parents=True)
        (dest / "alpha/custom.txt").write_text("retain", encoding="utf-8")
        conflict = subprocess.run([sys.executable, "-B", str(SCRIPT), "install", "--root", str(self.repo),
                                   "--dest", str(dest), "--apply"], capture_output=True)
        self.assertEqual(conflict.returncode, 2, conflict.stderr)
        self.assertFalse((dest / "beta").exists())


if __name__ == "__main__":
    unittest.main()
