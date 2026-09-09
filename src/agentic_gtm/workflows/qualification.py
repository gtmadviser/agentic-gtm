"""Offline evidence rubric and routing. Never turns a score into permission to send."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..enrichment import fingerprint


class Criterion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1)
    dimension: Literal["company", "persona"]
    mandatory: bool = True
    weight: int = Field(gt=0)


class Rubric(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(min_length=1)
    criteria: list[Criterion] = Field(min_length=2)
    company_threshold: float = Field(default=0.75, ge=0, le=1)
    persona_threshold: float = Field(default=0.75, ge=0, le=1)
    check_max_age_hours: int = Field(default=24, ge=1, le=168)


def fresh(value, now, hours):
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return timestamp.tzinfo is not None and timestamp <= now and (hours is None or now - timedelta(hours=hours) <= timestamp)
    except (TypeError, ValueError, AttributeError):
        return False


def qualify(row: dict, definition: dict, *, now: datetime | None = None) -> dict:
    rubric = Rubric.model_validate(definition)
    now = now or datetime.now(UTC)
    ids = [item.id for item in rubric.criteria]
    if len(set(ids)) != len(ids) or {c.dimension for c in rubric.criteria} != {
        "company",
        "persona",
    }:
        raise ValueError("Use unique criteria covering both company and persona")
    evaluations = row.get("criteria", {})
    dimensions, evidence, unknowns = {}, [], []
    for dimension in ("company", "persona"):
        score = known = total = 0
        mandatory_failed = mandatory_unknown = False
        for criterion in (c for c in rubric.criteria if c.dimension == dimension):
            item = evaluations.get(criterion.id, {})
            status = item.get("status", "unknown")
            sources = item.get("evidence", [])
            supported = sources and all(
                isinstance(source, dict)
                and source.get("source_url")
                and fresh(source.get("observed_at"), now, None)
                and source.get("value") is not None
                for source in sources
            )
            if status not in ("pass", "fail") or not supported:
                status = "unknown"
            total += criterion.weight
            if status == "unknown":
                unknowns.append(criterion.id)
                mandatory_unknown |= criterion.mandatory
            else:
                known += criterion.weight
                score += criterion.weight if status == "pass" else 0
                mandatory_failed |= criterion.mandatory and status == "fail"
            evidence.append(
                {
                    "criterion": criterion.id,
                    "dimension": dimension,
                    "status": status,
                    "evidence": sources,
                }
            )
        threshold = getattr(rubric, dimension + "_threshold")
        status = (
            "not_fit"
            if mandatory_failed
            else "review"
            if mandatory_unknown
            else "fit"
            if score / total >= threshold
            else "not_fit"
        )
        dimensions[dimension + "_fit"] = {
            "status": status,
            "score": score,
            "score_max": total,
            "known_weight": known,
        }
    checks = row.get("checks", {})
    lifecycle = checks.get("lifecycle")
    deals = checks.get("open_deals")
    clear_fields = (
        "opt_out",
        "competitor",
        "internal",
        "hard_exclusion",
        "recent_outreach",
        "campaign_member",
        "owner_conflict",
    )
    complete = all(type(checks.get(key)) is bool for key in clear_fields)
    complete &= lifecycle in ("prospect", "customer", "protected")
    complete &= type(deals) is int and deals >= 0
    complete &= checks.get("ownership_resolved") is True
    complete &= "account_owner" in checks and "contact_owner" in checks
    complete &= fresh(checks.get("crm_checked_at"), now, rubric.check_max_age_hours)
    complete &= fresh(checks.get("suppressions_checked_at"), now, rubric.check_max_age_hours)
    complete &= bool(checks.get("evidence_ids"))
    if row.get("is_internal") or any(checks.get(key) is True for key in clear_fields[:4]):
        route, reason = "exclude", "explicit_exclusion"
    elif lifecycle in ("customer", "protected") or (type(deals) is int and deals > 0):
        route, reason = "notify_only", "existing_relationship"
    elif any(value["status"] == "not_fit" for value in dimensions.values()):
        route, reason = "exclude", "not_icp_or_persona_fit"
    elif not row.get("person_id") or not row.get("profile_url") or not row.get("source_posts"):
        route, reason = "hold", "missing_identity_or_post"
    elif any(value["status"] == "review" for value in dimensions.values()):
        route, reason = "hold", "mandatory_fit_unknown"
    elif row.get("rubric_version") != rubric.version:
        route, reason = "hold", "rubric_changed"
    elif (
        not complete
        or checks.get("owner_conflict")
        or (
            checks.get("account_owner")
            and checks.get("contact_owner")
            and checks["account_owner"] != checks["contact_owner"]
        )
    ):
        route, reason = "hold", "unresolved_or_stale_relationship_checks"
    elif checks.get("account_owner") or checks.get("contact_owner"):
        route, reason = "owner_review", "owned_relationship"
    elif checks.get("recent_outreach") or checks.get("campaign_member"):
        route, reason = "hold", "prior_outreach"
    elif row.get("reviewed") is not True or not row.get("sender"):
        route, reason = "hold", "sender_or_review_missing"
    else:
        route, reason = "outreach_draft", "reviewed_unowned_prospect"
    return {
        "person_id": row.get("person_id"),
        "rubric_version": rubric.version,
        "input_hash": fingerprint({"row": row, "rubric": definition}),
        **dimensions,
        "criteria": evidence,
        "unknowns": unknowns,
        "route": route,
        "route_reason": reason,
        "engagement": {
            "posts": row.get("source_posts", []),
            "kinds": row.get("interactions", []),
            "sources": row.get("source_voices", []),
        },
        "external_actions": [],
        "enrollment_ready": False,
    }
