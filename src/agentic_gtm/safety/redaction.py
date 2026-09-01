"""Conservative redaction for logs and human output."""

from __future__ import annotations

import re
from typing import Any

KEYS = re.compile(r"(token|secret|password|api[_-]?key|authorization|service_role)", re.I)
BEARER = re.compile(r"(?i)bearer\s+[a-z0-9._~+/-]{12,}")


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if KEYS.search(str(key)) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return BEARER.sub("Bearer [REDACTED]", value)
    return value
