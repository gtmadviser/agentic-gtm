"""Slack report planning and verified posting."""

from __future__ import annotations

from typing import Any

import httpx

from ...config import credential, env_value
from ...contracts import ActionPlan, ApplyResult
from ..base import AdapterError, APIClient, ProviderAdapter


class SlackAdapter(ProviderAdapter):
    name = "slack"
    capabilities = frozenset({"inspect", "plan_report", "apply_report"})

    def __init__(self, token: str | None = None, **client_kwargs: Any) -> None:
        self.token = token or env_value("SLACK_BOT_TOKEN", "").strip()
        self.webhook = env_value("SLACK_WEBHOOK_URL", "").strip()
        if not self.token and not self.webhook:
            credential("SLACK_BOT_TOKEN")
        self.api = (
            APIClient(
                "https://slack.com/api",
                {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
                **client_kwargs,
            )
            if self.token
            else None
        )

    def inspect(self) -> dict[str, Any]:
        if not self.api:
            return {"provider": self.name, "mode": "webhook", "verified": False}
        response = self.api.request("POST", "/auth.test")
        if not response.get("ok"):
            raise AdapterError(f"Slack auth.test failed: {response.get('error', 'unknown')}")
        return {
            "provider": self.name,
            "mode": "bot",
            "verified": True,
            "team": response.get("team"),
        }

    def plan_report(self, text: str, channel: str | None = None) -> dict[str, Any]:
        channel = channel or env_value("SLACK_CHANNEL_ID", "").strip()
        if self.token and not channel:
            raise AdapterError("SLACK_CHANNEL_ID is required for verified bot posting")
        return {"channel": channel or "webhook", "text": text, "unfurl_links": False}

    def apply_report(self, plan: ActionPlan) -> ApplyResult:
        if plan.provider != self.name or plan.operation != "slack.post_report":
            raise AdapterError("plan does not authorize a Slack report")
        if self.api:
            response = self.api.request("POST", "/chat.postMessage", json=plan.payload)
            if not response.get("ok"):
                raise AdapterError(f"Slack post failed: {response.get('error', 'unknown')}")
            return ApplyResult(
                plan_id=plan.id,
                provider=self.name,
                status="applied",
                provider_ids=[str(response.get("ts"))],
                verified=True,
                message="Slack report posted and message ID verified",
            )
        response = httpx.post(self.webhook, json=plan.payload, timeout=30)
        response.raise_for_status()
        return ApplyResult(
            plan_id=plan.id,
            provider=self.name,
            status="applied",
            provider_ids=[],
            verified=False,
            message="Webhook accepted the report; delivery is unverified",
        )
