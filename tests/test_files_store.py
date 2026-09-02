from agentic_gtm.config import Settings
from agentic_gtm.contracts import ApplyResult
from agentic_gtm.database import FileStore, open_store
from agentic_gtm.safety import make_plan


def test_files_store_upserts_by_conflict_key_and_round_trips_nested(tmp_path) -> None:
    store = FileStore(tmp_path / "store")
    store.upsert(
        "accounts",
        [
            {"provider": "blitz", "provider_id": "1", "name": "A", "attributes": {"k": 1}},
            {"provider": "blitz", "provider_id": "2", "name": "B", "attributes": {}},
        ],
        "provider,provider_id",
    )
    store.upsert(
        "accounts",
        [{"provider": "blitz", "provider_id": "1", "name": "A2", "attributes": {"k": 2}}],
        "provider,provider_id",
    )
    rows = store.select("accounts")
    assert len(rows) == 2
    first = next(row for row in rows if row["provider_id"] == "1")
    assert first["name"] == "A2"
    assert first["attributes"] == {"k": 2}
    assert store.select("accounts", {"provider_id": "eq.2", "limit": "5"})[0]["name"] == "B"
    assert (tmp_path / "store" / ".gitignore").read_text() == "*\n"


def test_files_store_plan_lifecycle(tmp_path) -> None:
    store = FileStore(tmp_path / "store")
    plan = store.create_plan(
        make_plan("slack.post_report", "slack", ["C1"], {"text": "hi"}, "post")
    )
    assert store.get_plan(plan.id).verify()
    assert store.applied_result(plan.id) is None
    assert store.describe()["pending_plans"] == 1
    store.record_apply(
        ApplyResult(
            plan_id=plan.id, provider="slack", status="applied", verified=True, message="ok"
        )
    )
    assert store.applied_result(plan.id).status == "applied"
    assert store.get_plan(plan.id).status == "applied"


def test_open_store_falls_back_to_files_without_supabase(tmp_path, monkeypatch) -> None:
    for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings(store={"backend": "auto", "path": str(tmp_path / "s")})
    assert open_store(settings, quiet=True).backend == "files"


def test_open_store_respects_require_supabase_policy(tmp_path, monkeypatch) -> None:
    import pytest

    for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings(
        store={"backend": "auto", "path": str(tmp_path / "s")},
        policies={"require_supabase_for_connected_workflows": True},
    )
    with pytest.raises(RuntimeError, match="requires Supabase"):
        open_store(settings, quiet=True)
