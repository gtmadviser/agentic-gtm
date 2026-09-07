#!/usr/bin/env python3
"""Generate agentic-gtm-starter from one canonical runtime release."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from agentic_gtm.workspace import initialize_workspace

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_skills(target: Path) -> list[str]:
    generated = []
    for destination_root in (target / ".agents" / "skills", target / ".claude" / "skills"):
        destination_root.mkdir(parents=True, exist_ok=True)
        for source in sorted((ROOT / "skills").iterdir()):
            destination = destination_root / source.name
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("* 2.*", "__pycache__", "*.pyc"))
            generated.extend(
                str(path.relative_to(target)) for path in destination.rglob("*") if path.is_file()
            )
    return generated


def generate(target: Path, version: str) -> dict[str, object]:
    target.mkdir(parents=True, exist_ok=True)
    created = initialize_workspace(target, overwrite=True)
    created.extend(copy_skills(target))

    for source in sorted((ROOT / "src" / "agentic_gtm" / "sql").glob("*.sql")):
        migration = target / "supabase" / "migrations" / source.name
        shutil.copy2(source, migration)
        created.append(str(migration.relative_to(target)))

    runtime_pin = f"v{version}"
    pyproject = f"""[project]
name = "company-agentic-gtm-workspace"
version = "0.0.0"
requires-python = ">=3.11"
dependencies = [
  "gtmadviser-agentic-gtm @ git+https://github.com/gtmadviser/agentic-gtm.git@{runtime_pin}",
]

[tool.uv]
package = false
"""
    (target / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    (target / ".agentic-gtm-version").write_text(f"{version}\n", encoding="utf-8")
    created.extend(["pyproject.toml", ".agentic-gtm-version"])

    readme = f"""# Agentic GTM starter

Generated from [`gtmadviser/agentic-gtm` {runtime_pin}](https://github.com/gtmadviser/agentic-gtm/releases/tag/{runtime_pin}). Do not edit `.agents/skills/`, `.claude/skills/`, the pinned runtime, or copied migrations manually; regenerate them from the canonical release.

```bash
cp .env.example .env
uv sync
uv run gtm doctor
```

Git stores company context, decisions, experiment definitions, approved aggregates, and playbooks. Your Supabase project stores contacts, opportunities, activities, raw provider data, cursors, IDs, and approval records. `.gtm/` is ignored local cache.

- Want this adapted to your company? [GTM Adviser](https://gtmadviser.com)
- Want someone to operate it for you? [gtmengine.io](https://gtmengine.io)

Code and schemas are MIT licensed. Generated skills and written frameworks are CC BY 4.0.
"""
    (target / "README.md").write_text(readme, encoding="utf-8")
    (target / "LICENSE").write_text(
        (ROOT / "LICENSE").read_text(encoding="utf-8"), encoding="utf-8"
    )
    created.extend(["README.md", "LICENSE"])

    tracked = sorted({item for item in created if (target / item).is_file()})
    manifest = {
        "generator": "gtmadviser/agentic-gtm:scripts/generate_starter.py",
        "source_version": version,
        "files": {item: digest(target / item) for item in tracked},
    }
    (target / ".generated.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    result = generate(args.target.resolve(), args.version)
    print(
        json.dumps({"target": str(args.target.resolve()), "files": len(result["files"])}, indent=2)
    )


if __name__ == "__main__":
    main()
