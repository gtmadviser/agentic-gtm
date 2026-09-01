"""Immutable plan construction and apply validation."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from ..contracts import ActionPlan


def make_plan(
    operation: str,
    provider: str,
    targets: list[str],
    payload: dict[str, Any],
    summary: str,
) -> ActionPlan:
    identity = json.dumps(
        {"operation": operation, "provider": provider, "targets": targets, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
    )
    key = hashlib.sha256(identity.encode()).hexdigest()
    return ActionPlan(
        operation=operation,
        provider=provider,
        targets=targets,
        payload=payload,
        payload_summary=summary,
        idempotency_key=key,
    ).sealed()


def assert_plan_can_apply(plan: ActionPlan) -> None:
    if not plan.verify():
        raise ValueError("Action plan hash does not match its canonical payload")
    if plan.status != "pending":
        raise ValueError(f"Action plan is {plan.status}, not pending")
    if plan.expires_at <= datetime.now(UTC):
        raise ValueError("Action plan has expired; create and review a new plan")
    if plan.operation == "campaign.create_paused" and plan.payload.get("desired_state") != "paused":
        raise ValueError("Campaign action plan is not paused")
