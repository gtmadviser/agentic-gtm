"""Explicit provider registry. Affiliate data is intentionally absent."""

from __future__ import annotations

from typing import Any

from .ai_ark import AIArkAdapter
from .blitz import BlitzAdapter
from .hubspot import HubSpotAdapter
from .instantly import InstantlyAdapter
from .lemlist import LemlistAdapter
from .slack import SlackAdapter

ADAPTERS = {
    "hubspot": HubSpotAdapter,
    "ai_ark": AIArkAdapter,
    "blitz": BlitzAdapter,
    "lemlist": LemlistAdapter,
    "instantly": InstantlyAdapter,
    "slack": SlackAdapter,
}


def adapter_for(name: str, **kwargs: Any):
    try:
        adapter = ADAPTERS[name]
    except KeyError as exc:
        choices = ", ".join(sorted(ADAPTERS))
        raise ValueError(f"Unknown provider {name!r}. Choose one of: {choices}") from exc
    return adapter(**kwargs)
