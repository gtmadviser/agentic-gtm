"""lemlist paused-campaign adapter.

Provider facts this adapter relies on (observed 2026-08, verify against the
current docs before changing):

- Basic auth with an empty user and the API key as password.
- Steps live at `POST /sequences/{sequenceId}/steps`, not under campaigns.
  The email body field is `message`, the step needs a `type`, and delays are
  expressed as `delay` plus `delayType: "within"`.
- Step types: `email`, `linkedinInvite`, `linkedinSend`, `manual`.
- Senders and folders are UI-only; the API accepts them silently.
- Campaign statistics have no stable public endpoint here; import them from the
  CSV export with `gtm metrics import`.
"""

from __future__ import annotations

import base64
from typing import Any

from ...config import credential
from ...contracts import ActionPlan, ApplyResult, CampaignDraft
from ..base import AdapterError, APIClient, CapabilityError, ProviderAdapter

STEP_TYPES = {
    "email": "email",
    "linkedin_invite": "linkedinInvite",
    "linkedin_message": "linkedinSend",
    "manual": "manual",
}


def lemlist_step(step: dict[str, Any]) -> dict[str, Any]:
    """Translate one neutral step into the lemlist step payload."""
    channel = step.get("channel", "email")
    if channel not in STEP_TYPES:
        raise AdapterError(f"lemlist does not support channel {channel!r}")
    variants = step.get("variants") or [
        {"subject": step.get("subject", ""), "body": step.get("body", "")}
    ]
    primary = variants[0]
    payload: dict[str, Any] = {
        "type": STEP_TYPES[channel],
        "delay": int(step.get("day", 0)),
        "delayType": "within",
        "message": primary.get("body", ""),
    }
    if channel == "email":
        payload["subject"] = primary.get("subject", "")
    return payload


class LemlistAdapter(ProviderAdapter):
    name = "lemlist"
    capabilities = frozenset({"inspect", "plan_campaign", "apply_campaign", "pull_campaigns"})

    def __init__(self, token: str | None = None, **client_kwargs: Any) -> None:
        token = token or credential("LEMLIST_API_KEY")
        auth = base64.b64encode(f":{token}".encode()).decode()
        self.api = APIClient(
            "https://api.lemlist.com/api",
            {"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
            **client_kwargs,
        )

    def inspect(self) -> dict[str, Any]:
        return {"provider": self.name, "campaigns": self.api.request("GET", "/campaigns")}

    def plan_campaign(self, draft: CampaignDraft) -> dict[str, Any]:
        if draft.provider != self.name or draft.status != "paused":
            raise AdapterError("lemlist plans must target lemlist and remain paused")
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
            raise AdapterError("plan does not authorize a lemlist paused campaign")
        if plan.payload.get("desired_state") != "paused":
            raise AdapterError("refusing campaign payload that is not paused")
        campaign = plan.payload.get("campaign") or {}
        create_payload = {"name": campaign.get("name")}
        timezone = (campaign.get("schedule") or {}).get("timezone")
        if timezone:
            create_payload["timezone"] = timezone
        created = self.api.request("POST", "/campaigns", json=create_payload)
        provider_id = str(created.get("_id") or created.get("id") or "")
        sequence_id = str(created.get("sequenceId") or "")
        if not provider_id:
            raise AdapterError("lemlist did not return a campaign ID")
        try:
            paused = self.api.request("POST", f"/campaigns/{provider_id}/pause")
        except AdapterError as exc:
            raise AdapterError(
                f"Created empty lemlist campaign {provider_id}, but pausing failed. "
                "No steps or contacts were added; pause the empty shell manually."
            ) from exc
        if str(paused.get("state") or "").lower() != "paused":
            raise AdapterError(
                f"Created empty lemlist campaign {provider_id}, but pause was not verified. "
                "No steps or contacts were added."
            )
        steps = campaign.get("steps") or []
        if steps and not sequence_id:
            raise AdapterError("Paused campaign was created, but lemlist returned no sequence ID")
        for step in steps:
            self.api.request("POST", f"/sequences/{sequence_id}/steps", json=lemlist_step(step))
        state = self.api.request("GET", f"/campaigns/{provider_id}")
        status = str(
            state.get("state") or state.get("status") or state.get("campaignStatus") or ""
        ).lower()
        if status not in {"paused", "draft"}:
            raise AdapterError(
                f"campaign verification returned unsafe status: {status or 'unknown'}"
            )
        return ApplyResult(
            plan_id=plan.id,
            provider=self.name,
            status="applied",
            provider_ids=[provider_id],
            verified=True,
            message=f"Created empty shell, paused it, added {len(steps)} steps, and verified {status}",
        )

    def pull_campaigns(self) -> list[dict[str, Any]]:
        response = self.api.request("GET", "/campaigns")
        return response if isinstance(response, list) else response.get("campaigns", [])

    def pull_campaign_metrics(self, campaign_ids: list[str] | None = None) -> list[Any]:
        raise CapabilityError(
            "lemlist metrics are not pulled by this adapter. Export the campaign report as CSV "
            "and run `gtm metrics import --file <csv>`."
        )
