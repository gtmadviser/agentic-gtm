"""Deterministic identity keys and record deduplication."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import TypeVar
from urllib.parse import urlparse

T = TypeVar("T")


def normalized_domain(value: str | None) -> str:
    if not value:
        return ""
    candidate = value if "://" in value else f"https://{value}"
    host = (urlparse(candidate).hostname or "").lower().removeprefix("www.")
    return host.rstrip(".")


def normalized_email(value: str | None) -> str:
    return (value or "").strip().lower()


def normalized_linkedin(value: str | None) -> str:
    if not value:
        return ""
    candidate = value if "://" in value else f"https://{value}"
    parsed = urlparse(candidate)
    path = re.sub(r"/+", "/", parsed.path).rstrip("/").lower()
    host = (parsed.hostname or "").lower()
    return f"linkedin.com{path}" if host == "linkedin.com" or host.endswith(".linkedin.com") else ""


def deduplicate(records: Iterable[T], key: Callable[[T], str]) -> list[T]:
    seen: set[str] = set()
    result: list[T] = []
    for record in records:
        identity = key(record)
        if not identity or identity in seen:
            continue
        seen.add(identity)
        result.append(record)
    return result
