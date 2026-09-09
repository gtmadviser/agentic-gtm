"""Provider-neutral paid-call accounting. Planning never opens a provider client."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from .database.base import Store


def fingerprint(value: Any) -> str:
    # Preserve case, nulls, arrays and query semantics. Providers normalize only known fields.
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


class PaidRun(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    run_id: str = Field(default_factory=lambda: str(uuid4()), min_length=1)
    client_id: str = Field(min_length=1)
    account_scope: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    plan_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    max_calls: int = Field(ge=1, le=10000)
    budget_microusd: int = Field(ge=1)
    prices_microusd: dict[str, int] = Field(min_length=1)
    price_basis: str = Field(min_length=1)

    def checked(self) -> dict:
        if any(type(cost) is not int or cost <= 0 for cost in self.prices_microusd.values()):
            raise ValueError("Each endpoint needs a positive upper-bound cost in micro-USD")
        return self.model_dump(mode="json")


class PaidCalls:
    def __init__(self, store: Store, run: PaidRun):
        self.store, self.run = store, run
        store.enrichment_rpc("register", run.checked())

    def call(
        self,
        endpoint: str,
        inputs: dict,
        fetch: Callable[[], Any],
        *,
        schema_version: str,
        ttl_seconds: int,
        context: dict | None = None,
        validate: Callable[[Any], Any] = lambda value: value,
    ) -> dict:
        if not 1 <= ttl_seconds <= 31_536_000:
            raise ValueError("Cache TTL must be 1 second to 1 year")
        if endpoint not in self.run.prices_microusd:
            raise ValueError("Endpoint is outside the accepted pricing plan")
        identity = {
            "client_id": self.run.client_id,
            "account_scope": self.run.account_scope,
            "provider": self.run.provider,
            "endpoint": endpoint,
            "schema_version": schema_version,
            "inputs": inputs,
            "context": context or {},
        }
        now = datetime.now(UTC)
        request = {
            "run_id": self.run.run_id,
            "call_id": str(uuid4()),
            "cache_key": fingerprint(identity),
            "endpoint": endpoint,
            "input_hash": fingerprint(inputs),
            "now": now.isoformat(),
        }
        claim = self.store.enrichment_rpc("reserve", request)
        if claim["action"] == "cache_hit":
            validate(claim["response"])
            return claim
        try:
            response = fetch()
            validate(response)
            # Reject non-JSON data before attempting to complete a reservation.
            fingerprint(response)
            result = {
                **request,
                "response": response,
                "status": "success",
                "observed_at": datetime.now(UTC).isoformat(),
                "expires_at": (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat(),
            }
            self.store.enrichment_rpc("finish", result)
            return {"action": "fetched", **result}
        except Exception:
            # Error strings/headers can contain credentials. Persist only the uncertain state.
            # If this write fails, the pending reservation still prevents a replay.
            self.store.enrichment_rpc("finish", {**request, "status": "uncertain"})
            raise

    def summary(self) -> dict:
        return self.store.enrichment_rpc("inspect", {"run_id": self.run.run_id})


def file_operation(state: dict, operation: str, data: dict) -> dict:
    """One atomic JSON transaction under FileStore's process lock; no network here."""
    runs = state.setdefault("runs", {})
    cache = state.setdefault("cache", {})
    calls = state.setdefault("calls", {})
    run_id = data["run_id"]
    if operation == "register":
        accepted = PaidRun.model_validate(data).checked()
        if run_id in runs and runs[run_id]["plan"] != accepted:
            raise ValueError("Paid run already exists with another immutable plan")
        runs.setdefault(run_id, {"plan": accepted, "requests": 0, "reserved_microusd": 0})
        return runs[run_id]
    if run_id not in runs:
        raise ValueError("Paid run is not registered")
    run = runs[run_id]
    if operation == "inspect":
        ledger = [row for row in calls.values() if row["run_id"] == run_id]
        return {**run, "ledger": ledger}
    if operation == "reserve":
        if data["call_id"] in calls:
            raise ValueError("Call ID already exists; inspect its result before proceeding")
        cached = cache.get(data["cache_key"])
        if cached and cached["status"] != "ready":
            raise ValueError("Previous paid call is pending or uncertain; reconcile before reuse")
        if cached and datetime.fromisoformat(cached["expires_at"]) > datetime.fromisoformat(
            data["now"]
        ):
            calls[data["call_id"]] = {
                **data,
                "status": "cache_hit",
                "reserved_microusd": 0,
                "cost_source": "cache",
                "observed_at": cached["observed_at"],
            }
            return {"action": "cache_hit", **cached}
        price = run["plan"]["prices_microusd"].get(data["endpoint"])
        if not price:
            raise ValueError("Endpoint is outside the accepted pricing plan")
        if run["requests"] >= run["plan"]["max_calls"]:
            raise ValueError("Accepted request cap reached")
        if run["reserved_microusd"] + price > run["plan"]["budget_microusd"]:
            raise ValueError("Accepted spend ceiling would be exceeded")
        run["requests"] += 1
        run["reserved_microusd"] += price
        calls[data["call_id"]] = {
            **data,
            "status": "pending",
            "reserved_microusd": price,
            "cost_source": "accepted_upper_bound",
        }
        cache[data["cache_key"]] = {"call_id": data["call_id"], "status": "pending"}
        return {"action": "execute"}
    if operation == "finish":
        call = calls.get(data["call_id"])
        if not call or call["run_id"] != run_id or call["cache_key"] != data["cache_key"]:
            raise ValueError("Unknown paid-call reservation")
        if call["status"] != "pending":
            raise ValueError("Paid-call reservation already completed; inspect before changing")
        if data["status"] not in ("success", "uncertain"):
            raise ValueError("Invalid completion status")
        call["status"] = data["status"]
        entry = {"call_id": data["call_id"], "status": "uncertain"}
        if data["status"] == "success":
            entry.update(
                status="ready",
                response=data["response"],
                observed_at=data["observed_at"],
                expires_at=data["expires_at"],
            )
        cache[data["cache_key"]] = entry
        return {"status": call["status"]}
    raise ValueError("Unknown enrichment operation")
