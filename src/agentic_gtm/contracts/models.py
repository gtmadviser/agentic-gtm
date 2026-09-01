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


class CampaignDraft(Contract):
    id: UUID = Field(default_factory=uuid4)
    name: str
    provider: Literal["lemlist", "instantly"]
    audience_query: dict[str, Any]
    steps: list[dict[str, Any]]
    schedule: dict[str, Any] = Field(default_factory=dict)
    suppression_lists: list[str] = Field(default_factory=list)
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
