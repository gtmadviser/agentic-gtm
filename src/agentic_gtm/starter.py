"""Inspect generated assets and propose upgrades without overwriting client edits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def managed(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Generated manifest contains a path outside its workspace")
    return path


def health(root: Path) -> dict:
    manifest_path = root / ".generated.json"
    if not manifest_path.exists():
        return {"managed": False, "reason": "No generated starter manifest", "files": []}
    manifest = json.loads(manifest_path.read_text())
    changes = []
    for relative, expected in manifest["files"].items():
        actual = digest(managed(root, relative))
        if actual != expected:
            changes.append(
                {"path": relative, "status": "missing" if actual is None else "locally_modified"}
            )
    return {
        "managed": True,
        "source_version": manifest["source_version"],
        "files": changes,
        "note": "Local edits can be intentional; this report does not overwrite them.",
    }


def upgrade_plan(root: Path, candidate: Path) -> dict:
    old = json.loads((root / ".generated.json").read_text())
    new = json.loads((candidate / ".generated.json").read_text())
    changes = []
    for relative in sorted(set(old["files"]) | set(new["files"])):
        before = old["files"].get(relative)
        desired = new["files"].get(relative)
        actual = digest(managed(root, relative))
        if desired and digest(managed(candidate, relative)) != desired:
            raise ValueError("Candidate starter differs from its generated manifest")
        if actual == desired:
            continue
        status = (
            "review_removal"
            if desired is None
            else "add"
            if actual is None and before is None
            else "update"
            if actual == before
            else "conflict"
        )
        changes.append(
            {
                "path": relative,
                "status": status,
                "current_hash": actual,
                "generated_hash": before,
                "candidate_hash": desired,
            }
        )
    return {
        "from_version": old["source_version"],
        "to_version": new["source_version"],
        "changes": changes,
        "applied": False,
    }
