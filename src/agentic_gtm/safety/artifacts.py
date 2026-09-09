"""Keep local artifacts out of Git without replacing the workspace's ignore rules."""

from pathlib import Path


def ignore_artifacts(*paths: Path) -> None:
    for path in paths:
        if any(character in path.name for character in "\n\r"):
            raise ValueError("Artifact names cannot contain line breaks")
        path.parent.mkdir(parents=True, exist_ok=True)
        escaped = "".join("\\" + char if char in "\\[]*?!# " else char for char in path.name)
        pattern = "/" + escaped
        ignore = path.parent / ".gitignore"
        existing = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
        if pattern not in existing.splitlines():
            with ignore.open("a", encoding="utf-8") as handle:
                handle.write(("\n" if existing and not existing.endswith("\n") else "") + pattern + "\n")


def private_run_directory(path: Path) -> None:
    if (path / ".git").exists():
        raise ValueError("Use a dedicated collection directory, not the Git workspace root")
    path.mkdir(parents=True, exist_ok=True)
    ignore = path / ".gitignore"
    existing = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    if existing.splitlines()[-1:] != ["*"]:
        with ignore.open("a", encoding="utf-8") as handle:
            handle.write(("\n" if existing and not existing.endswith("\n") else "") + "*\n")
