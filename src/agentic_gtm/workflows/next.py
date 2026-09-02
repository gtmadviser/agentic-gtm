"""Deterministic gate machine: which stage is done, which comes next.

Every check reads only the workspace and the store. Nothing here calls a
provider. The output tells an agent (or a human) which skill to run next and
what evidence the current stage is missing.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..config import Settings
from ..contracts import CampaignDraft

STAGES: list[tuple[str, str, str]] = [
    ("context", "onboard-company-brain", "Company brain captured in context/company.md"),
    ("icp", "refine-icp", "Approved working ICP in market/icp.md"),
    ("crm", "inspect-crm", "CRM field map confirmed and opportunities synced"),
    ("experiment", "design-gtm-experiment", "An approved experiment file exists"),
    ("audience", "source-tam", "Accounts or contacts sourced into the store"),
    ("copy", "write-outreach", "A campaign draft with real copy exists"),
    ("plan", "stage-campaign", "An immutable action plan was created"),
    ("applied", "stage-campaign", "A plan was applied and the provider verified paused"),
    ("review", "review-outreach", "A review report exists under reports/"),
]


def _content_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _section(path: Path, heading: str) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.M)
    match = pattern.search(text)
    if not match:
        return ""
    rest = text[match.end() :]
    following = re.search(r"^##\s+", rest, re.M)
    body = rest[: following.start()] if following else rest
    return body.strip()


def _experiment_status(path: Path) -> str:
    try:
        if path.suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            return str(data.get("status", "")).lower()
        match = re.search(r"^status:\s*(\w+)", path.read_text(encoding="utf-8"), re.M | re.I)
        return match.group(1).lower() if match else ""
    except (OSError, ValueError):
        return ""


def _store_count(store: Any, table: str) -> int | None:
    if store is None:
        return None
    try:
        return len(store.select(table, {"limit": "1"}))
    except Exception:  # noqa: BLE001 - a broken store must not crash `gtm next`
        return None


def evaluate(root: Path, settings: Settings, store: Any | None) -> dict[str, Any]:
    root = Path(root)
    stages: list[dict[str, Any]] = []

    # context
    lines = _content_lines(root / "context" / "company.md")
    knowledge = list((root / "context" / "knowledge").glob("*--*.md"))
    stages.append(
        {
            "name": "context",
            "done": len(lines) >= 5 or bool(knowledge),
            "evidence": f"{len(lines)} content lines, {len(knowledge)} knowledge files",
        }
    )

    # icp
    approved = _section(root / "market" / "icp.md", "Approved working definition")
    stages.append(
        {
            "name": "icp",
            "done": len(approved) >= 40,
            "evidence": "approved working definition present"
            if approved
            else "approved working definition empty",
        }
    )

    # crm
    crm = settings.providers.get("crm")
    if not crm:
        stages.append({"name": "crm", "done": True, "evidence": "no CRM configured, skipped"})
    else:
        field_map = settings.field_maps.get(crm) or {}
        opportunities = _store_count(store, "opportunities")
        done = bool(field_map) and bool(opportunities)
        stages.append(
            {
                "name": "crm",
                "done": done,
                "evidence": (
                    f"field map {'confirmed' if field_map else 'missing'}; "
                    f"opportunities {'present' if opportunities else 'absent or store unavailable'}"
                ),
            }
        )

    # experiment
    statuses = [
        _experiment_status(path)
        for path in (root / "experiments").glob("*")
        if path.suffix in {".json", ".md"} and path.name.lower() != "readme.md"
    ]
    active = [status for status in statuses if status in {"approved", "running", "complete"}]
    stages.append(
        {
            "name": "experiment",
            "done": bool(active),
            "evidence": f"{len(statuses)} experiment files, {len(active)} approved or running",
        }
    )

    # audience
    accounts = _store_count(store, "accounts")
    contacts = _store_count(store, "contacts")
    stages.append(
        {
            "name": "audience",
            "done": bool(accounts or contacts),
            "evidence": "records in store" if (accounts or contacts) else "no sourced records",
        }
    )

    # copy
    drafts = 0
    for path in (root / "campaigns").glob("*.json"):
        try:
            draft = CampaignDraft.model_validate_json(path.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if any(variant.body.strip() for step in draft.steps for variant in step.all_variants()):
            drafts += 1
    stages.append(
        {"name": "copy", "done": drafts > 0, "evidence": f"{drafts} campaign drafts with copy"}
    )

    # plan / applied
    pending = None
    applied = _store_count(store, "apply_results")
    if store is not None:
        try:
            pending = store.describe().get("pending_plans")
        except Exception:  # noqa: BLE001
            pending = None
    stages.append(
        {
            "name": "plan",
            "done": bool(pending) or bool(applied),
            "evidence": f"pending plans: {pending if pending is not None else 'unknown'}",
        }
    )
    stages.append(
        {
            "name": "applied",
            "done": bool(applied),
            "evidence": "apply result recorded" if applied else "nothing applied yet",
        }
    )

    # review
    reports = [path for path in (root / "reports").glob("*.md") if path.name.lower() != "readme.md"]
    stages.append({"name": "review", "done": bool(reports), "evidence": f"{len(reports)} reports"})

    next_stage = next((stage for stage in stages if not stage["done"]), None)
    if next_stage is None:
        recommendation = {
            "stage": "iterate",
            "skill": "weekly-gtm-review",
            "why": "Every gate is satisfied. Run the weekly review and open the next experiment.",
        }
    else:
        name = next_stage["name"]
        skill, why = next((s, w) for n, s, w in STAGES if n == name)
        recommendation = {"stage": name, "skill": skill, "why": why}
    return {
        "workspace": str(root),
        "store": getattr(store, "backend", None),
        "stages": stages,
        "next": recommendation,
    }
