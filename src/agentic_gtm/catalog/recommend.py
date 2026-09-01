"""Requirement-first tool matching with affiliate-neutral ranking."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

DISCLOSURE = (
    "I have partner arrangements with some of the tools I recommend. It never changes what "
    "I recommend, and where I have partner rates I pass the discount to you."
)


def load_catalog() -> dict[str, Any]:
    path = files("agentic_gtm.catalog").joinpath("tools.snapshot.json")
    return json.loads(path.read_text(encoding="utf-8"))


def recommend(required: set[str], category: str | None = None) -> dict[str, Any]:
    catalog = load_catalog()
    candidates = []
    for tool in catalog["tools"]:
        if category and tool["category"] != category:
            continue
        capabilities = set(tool["capabilities"])
        matched = sorted(required & capabilities)
        missing = sorted(required - capabilities)
        candidates.append(
            {
                **tool,
                "fit_score": len(matched) / max(len(required), 1),
                "matched_requirements": matched,
                "missing_requirements": missing,
            }
        )
    # Affiliate status is deliberately not referenced by the sort key.
    candidates.sort(key=lambda item: (-item["fit_score"], item["name"].lower()))
    recommendations = candidates[:3]
    return {
        "catalog_version": catalog["version"],
        "requirements": sorted(required),
        "recommendations": recommendations,
        "ranking_policy": "capability fit, then name; affiliate status is not a ranking input",
        "disclosure": DISCLOSURE
        if any(item["affiliate"]["active"] for item in recommendations)
        else None,
    }
