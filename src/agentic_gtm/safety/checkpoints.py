"""Content-bound review records for local sample artifacts and recipe revisions."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from ..enrichment import fingerprint
from .artifacts import ignore_artifacts


def snapshot(root: Path, paths: list[str]) -> dict[str, str]:
    root = root.resolve()
    result = {}
    for relative in paths:
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("Checkpoint artifacts must be existing files within the workspace")
        result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    if not result:
        raise ValueError("Review at least one concrete artifact")
    return result


def review_record(root: Path, paths: list[str], recipe_version: str, reviewer: str) -> dict:
    if not recipe_version.strip() or not reviewer.strip():
        raise ValueError("Record the reviewed recipe version and reviewer")
    payload = {
        "files": snapshot(root, paths),
        "recipe_version": recipe_version,
        "reviewer": reviewer,
        "reviewed_at": datetime.now(UTC).isoformat(),
    }
    return {"payload": payload, "sha256": fingerprint(payload)}


def verify_review(root: Path, record: dict, accepted_hash: str, recipe_version: str) -> None:
    payload = record["payload"]
    if accepted_hash != record["sha256"] or fingerprint(payload) != accepted_hash:
        raise ValueError("Review hash does not match the accepted checkpoint")
    if (
        payload["recipe_version"] != recipe_version
        or snapshot(root, list(payload["files"])) != payload["files"]
    ):
        raise ValueError("Reviewed artifacts or recipe changed; review the current result")


def write_review(path: Path, record: dict) -> None:
    ignore_artifacts(path)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2)
