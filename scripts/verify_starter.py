#!/usr/bin/env python3
"""Verify that a generated starter has not drifted."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("starter", type=Path)
    args = parser.parse_args()
    manifest_path = args.starter / ".generated.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    changed = []
    for relative, expected in manifest["files"].items():
        path = args.starter / relative
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "missing"
        if actual != expected:
            changed.append(relative)
    if changed:
        raise SystemExit("Generated starter drift: " + ", ".join(changed))
    print(f"Verified {len(manifest['files'])} generated files from {manifest['source_version']}")


if __name__ == "__main__":
    main()
