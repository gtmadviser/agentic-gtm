"""Store protocol shared by the Supabase and file backends."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from ..contracts import ActionPlan, ApplyResult

TABLES = (
    "accounts",
    "contacts",
    "opportunities",
    "activities",
    "evidence",
    "experiments",
    "campaigns",
    "campaign_metrics",
    "metric_snapshots",
    "action_plans",
    "apply_results",
)


@runtime_checkable
class Store(Protocol):
    """Minimal operational store. Both backends implement exactly this surface."""

    backend: str

    def upsert(
        self, table: str, records: list[dict[str, Any]], on_conflict: str
    ) -> list[dict[str, Any]]: ...

    def select(self, table: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]: ...

    def create_plan(self, plan: ActionPlan) -> ActionPlan: ...

    def get_plan(self, plan_id: UUID | str) -> ActionPlan: ...

    def record_apply(self, result: ApplyResult) -> ApplyResult: ...

    def applied_result(self, plan_id: UUID | str) -> ApplyResult | None: ...

    def describe(self) -> dict[str, Any]: ...
