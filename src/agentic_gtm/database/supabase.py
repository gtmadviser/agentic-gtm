"""Minimal startup-owned Supabase REST store."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from ..adapters.base import APIClient
from ..config import credential, env_value
from ..contracts import ActionPlan, ApplyResult
from ..safety.plans import assert_plan_can_apply


class SupabaseStore:
    backend = "supabase"

    def __init__(
        self, url: str | None = None, key: str | None = None, **client_kwargs: Any
    ) -> None:
        url = (url or credential("SUPABASE_URL")).rstrip("/")
        key = key or credential("SUPABASE_SERVICE_ROLE_KEY")
        self.api = APIClient(
            f"{url}/rest/v1",
            {
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            **client_kwargs,
        )

    def upsert(
        self, table: str, records: list[dict[str, Any]], on_conflict: str
    ) -> list[dict[str, Any]]:
        if not records:
            return []
        if on_conflict == "provider,provider_id":
            import json

            existing = {}
            for provider in {row["provider"] for row in records}:
                ids = [str(row["provider_id"]) for row in records if row["provider"] == provider]
                for offset in range(0, len(ids), 100):
                    wanted = ",".join(json.dumps(value) for value in ids[offset : offset + 100])
                    for row in self.select(
                        table,
                        {
                            "provider": f"eq.{provider}",
                            "provider_id": f"in.({wanted})",
                            "select": "id,provider,provider_id",
                        },
                    ):
                        existing[(row["provider"], row["provider_id"])] = row["id"]
            records = [
                {**row, "id": existing.get((row["provider"], row["provider_id"]), row["id"])}
                if "id" in row
                else row
                for row in records
            ]
        return self.api.request(
            "POST",
            f"/{table}",
            params={"on_conflict": on_conflict},
            headers={"Prefer": "resolution=merge-duplicates,return=representation"},
            json=records,
        )

    def select(self, table: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
        return self.api.request("GET", f"/{table}", params={"select": "*", **(params or {})})

    def create_plan(self, plan: ActionPlan) -> ActionPlan:
        sealed = plan.sealed()
        body = sealed.model_dump(mode="json")
        rows = self.api.request(
            "POST",
            "/action_plans",
            headers={"Prefer": "return=representation"},
            json=body,
        )
        return ActionPlan.model_validate(rows[0] if isinstance(rows, list) else rows)

    def get_plan(self, plan_id: UUID | str) -> ActionPlan:
        rows = self.select("action_plans", {"id": f"eq.{plan_id}", "limit": "1"})
        if not rows:
            raise LookupError(f"Action plan {plan_id} was not found in this Supabase project")
        return ActionPlan.model_validate(rows[0])

    def claim_apply(self, plan_id: UUID | str) -> ActionPlan:
        plan = self.get_plan(plan_id)
        assert_plan_can_apply(plan)
        rows = self.api.request(
            "PATCH",
            "/action_plans",
            params={"id": f"eq.{plan.id}", "status": "eq.pending", "hash": f"eq.{plan.hash}"},
            headers={"Prefer": "return=representation"},
            json={"status": "applying"},
        )
        if not rows:
            raise ValueError(
                "Plan has already been claimed or changed; no external action performed"
            )
        return plan

    def mark_needs_review(self, plan_id: UUID | str) -> None:
        self.api.request(
            "PATCH",
            "/action_plans",
            params={"id": f"eq.{plan_id}", "status": "eq.applying"},
            json={"status": "needs_review"},
        )

    def record_apply(self, result: ApplyResult) -> ApplyResult:
        body = result.model_dump(mode="json")
        self.api.request(
            "POST",
            "/apply_results",
            headers={"Prefer": "resolution=ignore-duplicates,return=minimal"},
            params={"on_conflict": "plan_id"},
            json=body,
        )
        self.api.request(
            "PATCH",
            "/action_plans",
            params={"id": f"eq.{result.plan_id}", "status": "in.(pending,applying)"},
            headers={"Prefer": "return=minimal"},
            json={"status": "needs_review" if result.status == "rejected" else "applied"},
        )
        return result

    def applied_result(self, plan_id: UUID | str) -> ApplyResult | None:
        rows = self.select("apply_results", {"plan_id": f"eq.{plan_id}", "limit": "1"})
        return ApplyResult.model_validate(rows[0]) if rows else None

    def describe(self) -> dict[str, Any]:
        pending = self.select("action_plans", {"status": "eq.pending", "select": "id"})
        return {"backend": self.backend, "pending_plans": len(pending)}


def supabase_env_present() -> bool:
    return bool(env_value("SUPABASE_URL") and env_value("SUPABASE_SERVICE_ROLE_KEY"))
