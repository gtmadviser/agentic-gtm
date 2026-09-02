#!/usr/bin/env python3
"""Validate repository-owned plugin and skill structure in CI."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def main() -> None:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    if manifest.get("name") != ROOT.name:
        raise SystemExit("Plugin name must match the repository directory")
    if manifest.get("skills") != "./skills/":
        raise SystemExit("Codex manifest must point at the canonical skills directory")
    claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    if claude.get("name") != manifest["name"] or claude.get("version") != manifest["version"]:
        raise SystemExit("Claude and Codex manifests must share name and version")
    skills = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    if len(skills) < 12:
        raise SystemExit(f"Expected at least 12 skills, found {len(skills)}")
    for skill in skills:
        if not NAME.fullmatch(skill.name):
            raise SystemExit(f"Invalid skill directory name: {skill.name}")
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            raise SystemExit(f"Missing YAML frontmatter: {skill.name}")
        frontmatter = text.split("---", 2)[1]
        data = yaml.safe_load(frontmatter)
        if data.get("name") != skill.name or not data.get("description"):
            raise SystemExit(f"Invalid skill metadata: {skill.name}")
        if "\u2014" in text:
            raise SystemExit(f"Em dash in skill (the copy rules forbid them): {skill.name}")
        if text.count("\n") < 60:
            raise SystemExit(f"Skill is too thin (<60 lines): {skill.name}")
        if not (skill / "references").is_dir():
            raise SystemExit(f"Skill has no references directory: {skill.name}")
        for match in re.finditer(r"\]\((?:\./)?(references/[^)#]+)", text):
            if not (skill / match.group(1)).exists():
                raise SystemExit(f"Broken reference link in {skill.name}: {match.group(1)}")
    print(f"Validated both manifests and {len(skills)} skills")


if __name__ == "__main__":
    main()
