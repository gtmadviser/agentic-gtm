from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from agentic_gtm.database import FileStore
from agentic_gtm.enrichment import PaidCalls, PaidRun, fingerprint


def run(**overrides):
    return PaidRun(
        **{
            "client_id": "synthetic-client",
            "account_scope": "test-account",
            "provider": "test",
            "plan_hash": fingerprint("synthetic"),
            "max_calls": 10,
            "budget_microusd": 100,
            "prices_microusd": {"profile": 25},
            "price_basis": "synthetic test upper bound",
            **overrides,
        }
    )


def call(paid, inputs=None, fetch=lambda: {"value": "synthetic"}, **kwargs):
    return paid.call(
        "profile",
        inputs or {"id": "OpaqueID"},
        fetch,
        schema_version="v1",
        ttl_seconds=60,
        **kwargs,
    )


def test_cache_is_client_account_context_and_input_scoped(tmp_path):
    store = FileStore(tmp_path)
    first = PaidCalls(store, run())
    assert call(first)["action"] == "fetched"
    same = PaidCalls(store, run())
    assert (
        call(same, fetch=lambda: pytest.fail("cache hit must not execute provider"))["action"]
        == "cache_hit"
    )
    assert same.summary()["requests"] == 0
    assert same.summary()["ledger"][0]["reserved_microusd"] == 0
    for overrides in ({"client_id": "second-client"}, {"account_scope": "second-account"}):
        assert call(PaidCalls(store, run(**overrides)))["action"] == "fetched"
    assert call(same, {"id": "opaqueid"})["action"] == "fetched"
    assert call(same, context={"icp": "revision-2"})["action"] == "fetched"
    assert fingerprint({"x": None}) != fingerprint({})
    assert fingerprint({"url": "https://example.test/Case?q=A"}) != fingerprint(
        {"url": "https://example.test/case?q=a"}
    )


def test_limits_reserved_before_call_and_immutable_plan(tmp_path):
    store = FileStore(tmp_path)
    accepted = run(budget_microusd=25)
    paid = PaidCalls(store, accepted)
    call(paid)
    with pytest.raises(ValueError, match="spend ceiling"):
        call(paid, {"id": "another"}, lambda: pytest.fail("budget exceeded before provider"))
    assert paid.summary()["reserved_microusd"] == 25
    with pytest.raises(ValueError, match="immutable"):
        PaidCalls(store, accepted.model_copy(update={"budget_microusd": 500}))


def test_uncertain_call_blocks_new_runs_without_replay(tmp_path):
    store = FileStore(tmp_path)
    paid = PaidCalls(store, run())
    with pytest.raises(TimeoutError):
        call(paid, fetch=lambda: (_ for _ in ()).throw(TimeoutError("synthetic")))
    assert paid.summary()["ledger"][0]["status"] == "uncertain"
    assert paid.summary()["reserved_microusd"] == 25
    with pytest.raises(ValueError, match="uncertain"):
        call(PaidCalls(store, run()), fetch=lambda: pytest.fail("uncertain calls cannot replay"))


def test_concurrent_runs_cannot_double_call_same_provider_input(tmp_path):
    entered, release = Event(), Event()
    first = PaidCalls(FileStore(tmp_path), run())
    second = PaidCalls(FileStore(tmp_path), run())

    def provider():
        entered.set()
        assert release.wait(5)
        return {"ok": True}

    with ThreadPoolExecutor(2) as executor:
        future = executor.submit(call, first, None, provider)
        assert entered.wait(5)
        try:
            with pytest.raises(ValueError, match="pending"):
                call(second, fetch=lambda: pytest.fail("duplicate provider call"))
        finally:
            release.set()
        assert future.result()["action"] == "fetched"
    assert call(second)["action"] == "cache_hit"
    assert second.summary()["requests"] == 0


def test_expired_cache_requires_new_paid_reservation(tmp_path):
    import json

    paid = PaidCalls(FileStore(tmp_path), run())
    call(paid)
    path = tmp_path / "enrichment-state.json"
    state = json.loads(path.read_text())
    for cached in state["cache"].values():
        cached["expires_at"] = "2000-01-01T00:00:00+00:00"
    path.write_text(json.dumps(state))
    assert call(paid)["action"] == "fetched"
    assert paid.summary()["requests"] == 2
