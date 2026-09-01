#!/usr/bin/env python3
"""Conservative tree scanner for secrets, private keys, and non-synthetic fixtures."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

TEXT_SUFFIXES = {
    "",
    ".json",
    ".md",
    ".py",
    ".sql",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP = {".git", ".venv", "dist", "build", "__pycache__", ".pytest_cache", ".ruff_cache"}
PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}"),
    "Slack token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "nonempty secret assignment": re.compile(
        r"(?im)^(?:[A-Z0-9_]*(?:TOKEN|SECRET|PASSWORD|API_KEY|SERVICE_ROLE_KEY))=['\"]?[^\s#'\"]{12,}"
    ),
}
TOKEN = re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9_+/=-]{40,}(?![A-Za-z0-9])")


def entropy(value: str) -> float:
    counts = {character: value.count(character) for character in set(value)}
    return -sum((count / len(value)) * math.log2(count / len(value)) for count in counts.values())


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size < 2_000_000:
            yield path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", type=Path, default=Path("."))
    parser.add_argument("--deny-file", type=Path)
    args = parser.parse_args()
    denied = []
    if args.deny_file:
        denied = [
            line.strip().lower() for line in args.deny_file.read_text().splitlines() if line.strip()
        ]
    findings = []
    for path in iter_files(args.root.resolve()):
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative = path.relative_to(args.root.resolve())
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{relative}: {label}")
        for term in denied:
            if term in text.lower():
                findings.append(f"{relative}: prohibited term")
        if "fixtures" in path.parts:
            for token in TOKEN.findall(text):
                if len(set(token)) > 12 and entropy(token) >= 4.3:
                    findings.append(f"{relative}: high-entropy fixture value")
                    break
            domains = re.findall(r"\b(?:https?://)?([a-z0-9-]+(?:\.[a-z0-9-]+)+)\b", text, re.I)
            allowed = (".example", "json-schema.org", "github.com")
            if any(not domain.lower().endswith(allowed) for domain in domains):
                findings.append(f"{relative}: real-looking domain in fixture")
    if findings:
        raise SystemExit("Public release scan failed:\n" + "\n".join(sorted(set(findings))))
    print("Public release scan passed")


if __name__ == "__main__":
    main()
