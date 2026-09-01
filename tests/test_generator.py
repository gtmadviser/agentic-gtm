import json
from pathlib import Path

from scripts.generate_starter import ROOT, generate


def test_generator_copies_canonical_skills_byte_for_byte(tmp_path: Path) -> None:
    target = tmp_path / "starter"
    manifest = generate(target, "0.1.0")
    assert manifest["source_version"] == "0.1.0"
    for skill in (ROOT / "skills").iterdir():
        if not skill.is_dir():
            continue
        canonical = (skill / "SKILL.md").read_bytes()
        assert (target / ".agents" / "skills" / skill.name / "SKILL.md").read_bytes() == canonical
        assert (target / ".claude" / "skills" / skill.name / "SKILL.md").read_bytes() == canonical
    saved = json.loads((target / ".generated.json").read_text())
    assert saved["files"] == manifest["files"]
