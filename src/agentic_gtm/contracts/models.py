"""Stable provider-neutral data contracts."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProviderRecord(Contract):
    id: UUID = Field(default_factory=uuid4)
    provider: str
    provider_id: str
    source_url: HttpUrl | None = None
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    attributes: dict[str, Any] = Field(default_factory=dict)


class Account(ProviderRecord):
    name: str
    domain: str | None = None
    industry: str | None = None
    employee_count: int | None = Field(default=None, ge=0)
    country_code: str | None = Field(default=None, min_length=2, max_length=2)


class Contact(ProviderRecord):
    account_id: UUID | None = None
    full_name: str
    title: str | None = None
    email: str | None = None
    linkedin_url: HttpUrl | None = None


class Opportunity(ProviderRecord):
    account_id: UUID | None = None
    name: str
    stage: str
    status: Literal["open", "won", "lost"]
    amount: float | None = None
    currency: str | None = None
    close_date: datetime | None = None


class Activity(ProviderRecord):
    account_id: UUID | None = None
    contact_id: UUID | None = None
    opportunity_id: UUID | None = None
    kind: str
    occurred_at: datetime
    summary: str | None = None


class Evidence(Contract):
    id: UUID = Field(default_factory=uuid4)
    subject: str
    claim: str
    kind: Literal["declared", "observed", "hypothesis", "decision"]
    source: str
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    confidence: float = Field(ge=0, le=1)
    supports: bool = True


class Experiment(Contract):
    id: UUID = Field(default_factory=uuid4)
    name: str
    audience: str
    trigger: str
    channel: str
    hypothesis: str
    denominator: str
    safeguards: list[str]
    decision_rule: str
    owner: str
    status: Literal["draft", "approved", "running", "complete"] = "draft"


class CampaignVariant(Contract):
    subject: str = ""
    body: str = ""
    hypothesis: str | None = None


class CampaignStep(Contract):
    """One touch in a sequence. `day` is the offset from the previous step."""

    day: int = Field(ge=0)
    channel: Literal["email", "linkedin_invite", "linkedin_message", "manual"] = "email"
    subject: str = ""
    body: str = ""
    variants: list[CampaignVariant] = Field(default_factory=list)

    def all_variants(self) -> list[CampaignVariant]:
        if self.variants:
            return self.variants
        return [CampaignVariant(subject=self.subject, body=self.body)]


class CampaignSchedule(Contract):
    timezone: str = "Europe/Berlin"
    start: str = "08:00"
    end: str = "17:00"
    days: list[int] = Field(default_factory=lambda: [1, 2, 3, 4, 5])
    name: str = "Working hours"


class CampaignDraft(Contract):
    id: UUID = Field(default_factory=uuid4)
    name: str
    provider: Literal["lemlist", "instantly"]
    audience_query: dict[str, Any]
    steps: list[CampaignStep]
    schedule: CampaignSchedule = Field(default_factory=CampaignSchedule)
    suppression_lists: list[str] = Field(default_factory=list)
    experiment_id: UUID | None = None
    status: Literal["draft", "paused"] = "paused"

    @model_validator(mode="after")
    def enforce_paused(self) -> CampaignDraft:
        if self.status != "paused":
            raise ValueError("campaign drafts must remain paused")
        return self


class MetricSnapshot(Contract):
    id: UUID = Field(default_factory=uuid4)
    metric: str
    numerator: float
    denominator: float
    window_start: datetime
    window_end: datetime
    dimensions: dict[str, str] = Field(default_factory=dict)

    @property
    def rate(self) -> float | None:
        return self.numerator / self.denominator if self.denominator else None


class CampaignMetrics(Contract):
    """Counts for one campaign (and optional variant) in one window.

    Rates are derived, never stored. `sent` is the universal denominator for
    per-1k metrics; `delivered` (sent minus bounced) is the denominator for
    reply rates. Imported from any tool export or pulled by an adapter.
    """

    id: UUID = Field(default_factory=uuid4)
    provider: str
    campaign: str
    variant: str = ""
    window_start: datetime
    window_end: datetime
    sent: int = Field(default=0, ge=0)
    delivered: int | None = Field(default=None, ge=0)
    bounced: int = Field(default=0, ge=0)
    replied: int = Field(default=0, ge=0)
    positive_replies: int = Field(default=0, ge=0)
    meetings: int = Field(default=0, ge=0)
    opportunities: int = Field(default=0, ge=0)
    source: str = "import"
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def effective_delivered(self) -> int:
        if self.delivered is not None:
            return self.delivered
        return max(self.sent - self.bounced, 0)


class ActionPlan(Contract):
    id: UUID = Field(default_factory=uuid4)
    operation: str
    provider: str
    targets: list[str]
    payload: dict[str, Any]
    payload_summary: str
    idempotency_key: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC) + timedelta(hours=24))
    hash: str = ""
    status: Literal["pending", "applied", "expired"] = "pending"

    def canonical_payload(self) -> str:
        body = {
            "id": str(self.id),
            "operation": self.operation,
            "provider": self.provider,
            "targets": self.targets,
            "payload": self.payload,
            "payload_summary": self.payload_summary,
            "idempotency_key": self.idempotency_key,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }
        return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def sealed(self) -> ActionPlan:
        digest = hashlib.sha256(self.canonical_payload().encode()).hexdigest()
        return self.model_copy(update={"hash": digest})

    def verify(self) -> bool:
        expected = hashlib.sha256(self.canonical_payload().encode()).hexdigest()
        return bool(self.hash) and self.hash == expected


class ApplyResult(Contract):
    plan_id: UUID
    provider: str
    status: Literal["applied", "already_applied", "rejected"]
    provider_ids: list[str] = Field(default_factory=list)
    verified: bool
    message: str
    applied_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
