"""CI-only YAML parsing; does not execute any imported skill or tool."""
import json
from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[2]
names = []
for path in sorted((root / "skills").glob("*/SKILL.md")):
    text = path.read_text(encoding="utf-8-sig")
    header, body = text.split("---", 2)[1:]
    metadata = yaml.safe_load(header)
    assert isinstance(metadata, dict), path
    assert metadata["name"] == path.parent.name, path
    assert isinstance(metadata["description"], str) and metadata["description"].strip(), path
    assert len(metadata["description"]) <= 1024 and body.strip(), path
    names.append(metadata["name"])
catalog = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
expected = catalog["local_skills"] + [name for source in catalog["sources"] for name in source["skills"]]
assert sorted(names) == sorted(expected) and len(set(names)) == len(expected)
for path in (root / "skills").glob("*/agents/openai.yaml"):
    assert isinstance(yaml.safe_load(path.read_text(encoding="utf-8")), dict), path
print(json.dumps({"yaml_parsed_packages": len(names), "unique_identities": len(set(names))}))
