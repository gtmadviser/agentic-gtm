"""Instantly paused-campaign adapter (API v2).

Provider facts this adapter relies on (observed 2026-09, verify against the
current docs before changing):

- `POST /campaigns` requires `name` and `campaign_schedule`. A schedule has
  `schedules[]`, each with `name`, `timing.from`, `timing.to`, `days` keyed
  "0".."6" (Sunday..Saturday) and `timezone`.
- Campaign status codes: 0 draft, 1 active, 2 paused, 3 completed,
  4 running subsequences, -1 accounts unhealthy, -2 bounce protect,
  -99 account suspended.
- Sequences are replaced as a whole: `PATCH /campaigns/{id}` with a full
  `sequences` array. Never send a partial step list.
- `GET /campaigns/analytics?id=` returns per-campaign counts.
"""

from __future__ import annotations

from typing import Any

from ...config import credential
from ...contracts import ActionPlan, ApplyResult, CampaignDraft, CampaignMetrics
from ..base import AdapterError, APIClient, ProviderAdapter

SAFE_STATUSES = {0, 2, "0", "2", "draft", "paused"}


def instantly_schedule(schedule: dict[str, Any]) -> dict[str, Any]:
    """Translate the provider-neutral schedule into Instantly's required shape."""
    days = schedule.get("days") or [1, 2, 3, 4, 5]
    return {
        "schedules": [
            {
                "name": schedule.get("name") or "Working hours",
                "timing": {
                    "from": schedule.get("start") or "08:00",
                    "to": schedule.get("end") or "17:00",
                },
                "days": {str(index): (index in days) for index in range(7)},
                "timezone": schedule.get("timezone") or "Europe/Berlin",
            }
        ]
    }


def instantly_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Translate neutral steps into Instantly sequence steps. Email only."""
    result = []
    for step in steps:
        if step.get("channel", "email") != "email":
            raise AdapterError(
                f"Instantly campaigns support email steps only; got {step.get('channel')!r}"
            )
        variants = step.get("variants") or [
            {"subject": step.get("subject", ""), "body": step.get("body", "")}
        ]
        result.append(
            {
                "type": "email",
                "delay": int(step.get("day", 0)),
                "variants": [
                    {"subject": variant.get("subject", ""), "body": variant.get("body", "")}
                    for variant in variants
                ],
            }
        )
    return result


class InstantlyAdapter(ProviderAdapter):
    name = "instantly"
    capabilities = frozenset(
        {"inspect", "plan_campaign", "apply_campaign", "pull_campaigns", "pull_campaign_metrics"}
    )

    def __init__(self, token: str | None = None, **client_kwargs: Any) -> None:
        token = token or credential("INSTANTLY_API_KEY")
        self.api = APIClient(
            "https://api.instantly.ai/api/v2",
            {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            **client_kwargs,
        )

    def inspect(self) -> dict[str, Any]:
        return {"provider": self.name, "campaigns": self.pull_campaigns()}

    def plan_campaign(self, draft: CampaignDraft) -> dict[str, Any]:
        if draft.provider != self.name or draft.status != "paused":
            raise AdapterError("Instantly plans must target Instantly and remain paused")
        return {
            "desired_state": "paused",
            "campaign": {
                "name": draft.name,
                "schedule": draft.schedule.model_dump(mode="json"),
                "steps": [step.model_dump(mode="json") for step in draft.steps],
            },
        }

    def apply_campaign(self, plan: ActionPlan) -> ApplyResult:
        if plan.provider != self.name or plan.operation != "campaign.create_paused":
            raise AdapterError("plan does not authorize an Instantly paused campaign")
        if plan.payload.get("desired_state") != "paused":
            raise AdapterError("refusing campaign payload that is not draft/paused")
        campaign = plan.payload.get("campaign") or {}
        steps = instantly_steps(campaign.get("steps") or [])
        create_body = {
            "name": campaign.get("name"),
            "campaign_schedule": instantly_schedule(campaign.get("schedule") or {}),
        }
        created = self.api.request("POST", "/campaigns", json=create_body)
        provider_id = str(created.get("id") or "")
        if not provider_id:
            raise AdapterError("Instantly did not return a campaign ID")
        try:
            paused = self.api.request("POST", f"/campaigns/{provider_id}/pause")
        except AdapterError as exc:
            raise AdapterError(
                f"Created empty Instantly campaign {provider_id}, but pausing failed. "
                "No sequence content or contacts were added; pause the empty shell manually."
            ) from exc
        paused_status = paused.get("status", paused.get("campaign_status"))
        if paused_status not in SAFE_STATUSES:
            raise AdapterError(
                f"Created empty Instantly campaign {provider_id}, but pause was not verified. "
                "No sequence content or contacts were added."
            )
        if steps:
            self.api.request(
                "PATCH", f"/campaigns/{provider_id}", json={"sequences": [{"steps": steps}]}
            )
        state = self.api.request("GET", f"/campaigns/{provider_id}")
        status = state.get("status", state.get("campaign_status"))
        if status not in SAFE_STATUSES:
            raise AdapterError(f"campaign verification returned unsafe status: {status}")
        return ApplyResult(
            plan_id=plan.id,
            provider=self.name,
            status="applied",
            provider_ids=[provider_id],
            verified=True,
            message=(
                f"Created empty shell, paused it, added {len(steps)} email steps, "
                "and verified state"
            ),
        )

    def pull_campaigns(self) -> list[dict[str, Any]]:
        response = self.api.request("GET", "/campaigns")
        return response.get("items", response) if isinstance(response, dict) else response

    def pull_campaign_metrics(self, campaign_ids: list[str] | None = None) -> list[CampaignMetrics]:
        """Pull lifetime counts per campaign. Field names follow the v2 analytics API."""
        from datetime import UTC, datetime

        params = {"id": campaign_ids[0]} if campaign_ids and len(campaign_ids) == 1 else {}
        rows = self.api.request("GET", "/campaigns/analytics", params=params)
        rows = rows if isinstance(rows, list) else rows.get("items", [])
        now = datetime.now(UTC)
        metrics = []
        for row in rows:
            campaign_id = str(row.get("campaign_id") or row.get("id") or "")
            if not campaign_id or (campaign_ids and campaign_id not in campaign_ids):
                continue
            sent = int(row.get("emails_sent_count") or 0)
            bounced = int(row.get("bounced_count") or 0)
            metrics.append(
                CampaignMetrics(
                    provider=self.name,
                    campaign=row.get("campaign_name") or campaign_id,
                    campaign_id=campaign_id,
                    kind="cumulative",
                    variant="",
                    window_start=datetime.fromtimestamp(0, UTC),
                    window_end=now,
                    sent=sent,
                    delivered=max(sent - bounced, 0),
                    bounced=bounced,
                    replied=int(row["reply_count_unique"]) if row.get("reply_count_unique") is not None else None,
                    positive_replies=None,
                    opportunities=int(row["total_opportunities"]) if row.get("total_opportunities") is not None else None,
                    source="instantly.analytics",
                )
            )
        return metrics
