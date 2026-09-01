"""Instantly paused-campaign adapter."""

from __future__ import annotations

from typing import Any

from ...config import credential
from ...contracts import ActionPlan, ApplyResult, CampaignDraft
from ..base import AdapterError, APIClient, ProviderAdapter


class InstantlyAdapter(ProviderAdapter):
    name = "instantly"
    capabilities = frozenset({"inspect", "plan_campaign", "apply_campaign", "pull_campaigns"})

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
                "schedule": draft.schedule,
                "steps": draft.steps,
            },
        }

    def apply_campaign(self, plan: ActionPlan) -> ApplyResult:
        if plan.provider != self.name or plan.operation != "campaign.create_paused":
            raise AdapterError("plan does not authorize an Instantly paused campaign")
        if plan.payload.get("desired_state") != "paused":
            raise AdapterError("refusing campaign payload that is not draft/paused")
        campaign = plan.payload.get("campaign") or {}
        created = self.api.request("POST", "/campaigns", json={"name": campaign.get("name")})
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
        if paused_status not in {0, 2, "0", "2", "draft", "paused"}:
            raise AdapterError(
                f"Created empty Instantly campaign {provider_id}, but pause was not verified. "
                "No sequence content or contacts were added."
            )
        update = {}
        if campaign.get("steps"):
            update["sequences"] = [{"steps": campaign["steps"]}]
        if campaign.get("schedule"):
            update["campaign_schedule"] = campaign["schedule"]
        if update:
            self.api.request("PATCH", f"/campaigns/{provider_id}", json=update)
        state = self.api.request("GET", f"/campaigns/{provider_id}")
        status = state.get("status", state.get("campaign_status"))
        if status not in {0, 2, "0", "2", "draft", "paused"}:
            raise AdapterError(f"campaign verification returned unsafe status: {status}")
        return ApplyResult(
            plan_id=plan.id,
            provider=self.name,
            status="applied",
            provider_ids=[provider_id],
            verified=True,
            message="Created empty shell, paused it, added sequence content, and verified state",
        )

    def pull_campaigns(self) -> list[dict[str, Any]]:
        response = self.api.request("GET", "/campaigns")
        return response.get("items", response) if isinstance(response, dict) else response
