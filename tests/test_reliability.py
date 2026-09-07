import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest
from typer.testing import CliRunner

from agentic_gtm.adapters.base import AdapterError, APIClient, CapabilityError
from agentic_gtm.adapters.lemlist import LemlistAdapter
from agentic_gtm.cli.app import _metrics_from_rows, app
from agentic_gtm.config import credential, load_settings
from agentic_gtm.contracts import Account, ApplyResult, CampaignMetrics
from agentic_gtm.database import FileStore
from agentic_gtm.database.supabase import SupabaseStore
from agentic_gtm.safety import make_plan
from agentic_gtm.workflows.metrics import parse_metrics_csv, summarize
from agentic_gtm.workspace import initialize_workspace


def metric(**updates):
    return CampaignMetrics.model_validate(
        {
            "provider": "example",
            "campaign": "Example",
            "campaign_id": "stable-id",
            "window_start": "2026-08-01T00:00:00Z",
            "window_end": "2026-08-08T00:00:00Z",
            "sent": 250,
            **updates,
        }
    )


def test_workspace_env_isolated_and_nested_store_resolution(tmp_path, monkeypatch):
    for variable in ("EXAMPLE_TEST_CREDENTIAL", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
        monkeypatch.delenv(variable, raising=False)
    left, right = tmp_path / "left", tmp_path / "right"
    initialize_workspace(left)
    initialize_workspace(right)
    (left / ".env").write_text("EXAMPLE_TEST_CREDENTIAL=synthetic-left\n")
    monkeypatch.chdir(left / "campaigns")
    settings = load_settings()
    assert settings.workspace_root == left
    assert settings.resolve(settings.store.path) == left / ".gtm/store"
    assert credential("EXAMPLE_TEST_CREDENTIAL") == "synthetic-left"
    load_settings(right / "gtm.yaml")
    with pytest.raises(RuntimeError, match="Missing"):
        credential("EXAMPLE_TEST_CREDENTIAL")
    monkeypatch.setenv("EXAMPLE_TEST_CREDENTIAL", "synthetic-shell")
    load_settings(left / "gtm.yaml")
    assert credential("EXAMPLE_TEST_CREDENTIAL") == "synthetic-shell"


def test_typed_file_roundtrip_preserves_empty_and_null(tmp_path):
    store = FileStore(tmp_path)
    values = {
        "id": "one",
        "empty": "",
        "null": None,
        "literal": "json:false",
        "count": 3,
        "flag": False,
        "nested": {"value": 2},
    }
    store.upsert("accounts", [values], "id")
    assert store.select("accounts") == [values]
    store.upsert("campaign_metrics", [metric().model_dump(mode="json")], "campaign_id")
    assert _metrics_from_rows(store.select("campaign_metrics"))[0].variant == ""
    with pytest.raises(ValueError, match="Invalid stored"):
        _metrics_from_rows([{"sent": "not-a-number"}])


def test_metric_snapshots_use_latest_stable_id_despite_rename():
    rows = [
        metric(kind="cumulative", sent=100),
        metric(kind="cumulative", sent=250, campaign="Renamed", window_end="2026-08-09T00:00:00Z"),
    ]
    result = summarize(rows)
    assert result["totals"]["sent"] == 250
    assert result["campaigns"][0]["campaign"] == "Renamed"
    assert result["totals"]["positive_reply_rate"] is None
    assert result["ranking"] == []


def test_metric_overlaps_mixed_units_and_fractional_counts_rejected(tmp_path):
    with pytest.raises(ValueError, match="overlap"):
        summarize([metric(), metric(window_start="2026-08-07T00:00:00Z")])
    with pytest.raises(ValueError, match="units differ"):
        summarize([metric(), metric(campaign_id="another", unit="contact")])
    with pytest.raises(ValueError, match="Do not mix"):
        summarize([metric(), metric(kind="cumulative")])
    path = tmp_path / "metrics.csv"
    path.write_text("campaign,sent,window_start,window_end\nExample,2.5,2026-08-01,2026-08-02\n")
    with pytest.raises(ValueError, match="line 2"):
        parse_metrics_csv(path)


@pytest.mark.parametrize("failure", ["timeout", "server"])
def test_mutation_failure_is_not_automatically_retried(failure):
    calls = []

    def handler(request):
        calls.append(request)
        if failure == "timeout":
            raise httpx.ReadTimeout("private provider response", request=request)
        return httpx.Response(500, text="private provider response")

    client = APIClient("https://example.test", {}, transport=httpx.MockTransport(handler))
    with pytest.raises(AdapterError) as error:
        client.request("POST", "/campaigns", json={"name": "Example"})
    assert len(calls) == 1
    assert "private provider response" not in str(error.value)


def test_two_workers_can_claim_plan_only_once(tmp_path):
    store = FileStore(tmp_path)
    plan = store.create_plan(
        make_plan("slack.post_report", "slack", ["C-example"], {"text": "Example"}, "Example")
    )
    duplicate = store.create_plan(
        make_plan("slack.post_report", "slack", ["C-example"], {"text": "Example"}, "Example")
    )
    assert duplicate.id == plan.id

    def claim(_):
        try:
            FileStore(tmp_path).claim_apply(plan.id)
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(claim, range(2))) == [False, True]
    store.mark_needs_review(plan.id)
    with pytest.raises(ValueError, match="needs_review"):
        store.claim_apply(plan.id)
    assert store.describe()["pending_plans"] == 0
    result = ApplyResult(
        plan_id=plan.id,
        provider="slack",
        status="applied",
        verified=True,
        message="Example reconciled",
    )
    store.record_apply(result)
    assert len(store.select("apply_results")) == 1


def test_stable_provider_identity_preserves_legacy_id(tmp_path):
    first = Account(provider="example", provider_id="one", name="Example")
    second = Account(provider="example", provider_id="one", name="Updated")
    assert first.id == second.id
    legacy = str(uuid4())
    store = FileStore(tmp_path)
    store.upsert(
        "accounts", [{**first.model_dump(mode="json"), "id": legacy}], "provider,provider_id"
    )
    assert (
        store.upsert("accounts", [second.model_dump(mode="json")], "provider,provider_id")[0]["id"]
        == legacy
    )


def test_supabase_claim_uses_compare_and_swap():
    plan = make_plan("slack.post_report", "slack", ["C-example"], {"text": "Example"}, "Example")

    def handler(request):
        if request.method == "GET":
            return httpx.Response(200, json=[plan.model_dump(mode="json")])
        assert request.method == "PATCH"
        assert request.url.params["status"] == "eq.pending"
        assert request.url.params["hash"] == f"eq.{plan.hash}"
        assert json.loads(request.content) == {"status": "applying"}
        return httpx.Response(200, json=[])

    store = SupabaseStore(
        "https://example.test", "synthetic", transport=httpx.MockTransport(handler)
    )
    with pytest.raises(ValueError, match="already been claimed"):
        store.claim_apply(plan.id)


def test_lemlist_rejects_multiple_variants_before_any_write():
    calls = []
    adapter = LemlistAdapter(
        token="synthetic", transport=httpx.MockTransport(lambda request: calls.append(request))
    )
    plan = make_plan(
        "campaign.create_paused",
        "lemlist",
        ["example"],
        {
            "desired_state": "paused",
            "campaign": {
                "name": "Example",
                "steps": [
                    {"channel": "email", "variants": [{"body": "A"}, {"body": "B"}]},
                ],
            },
        },
        "Example",
    )
    with pytest.raises(CapabilityError, match="one variant"):
        adapter.apply_campaign(plan)
    assert calls == []


def test_init_contains_skills_without_overwriting_local_customization(tmp_path):
    initialize_workspace(tmp_path)
    skill = tmp_path / ".agents/skills/linkedin-engager-outreach/SKILL.md"
    assert skill.exists()
    assert (
        tmp_path / ".claude/skills/linkedin-engager-outreach/scripts/harvest_engagers.py"
    ).exists()
    skill.write_text("Custom local instructions")
    initialize_workspace(tmp_path)
    assert skill.read_text() == "Custom local instructions"


def test_cli_review_from_nested_folder_uses_company_workspace(tmp_path, monkeypatch):
    initialize_workspace(tmp_path)
    for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
        monkeypatch.delenv(name, raising=False)
    store = FileStore(tmp_path / ".gtm/store")
    store.upsert("campaign_metrics", [metric().model_dump(mode="json")], "campaign_id")
    monkeypatch.chdir(tmp_path / "campaigns")
    result = CliRunner().invoke(app, ["--json", "review", "outreach"])
    assert result.exit_code == 0, result.exception
    payload = json.loads(result.output)
    assert payload["totals"]["sent"] == 250
    assert payload["artifact"] == str(
        tmp_path / "reports" / f"outreach-{datetime.now(UTC).date()}.md"
    )
