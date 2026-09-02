import json
from datetime import UTC, datetime
from pathlib import Path

from typer.testing import CliRunner

from agentic_gtm.cli.app import app
from agentic_gtm.config import Settings
from agentic_gtm.contracts import CampaignMetrics
from agentic_gtm.database import FileStore
from agentic_gtm.workflows.metrics import certainty, parse_metrics_csv, summarize
from agentic_gtm.workflows.next import evaluate

runner = CliRunner()


def _metrics(sent: int, replied: int, positive: int, meetings: int, opps: int, variant="A"):
    return CampaignMetrics(
        provider="demo",
        campaign="c",
        variant=variant,
        window_start=datetime(2026, 8, 1, tzinfo=UTC),
        window_end=datetime(2026, 8, 31, tzinfo=UTC),
        sent=sent,
        bounced=int(sent * 0.01),
        replied=replied,
        positive_replies=positive,
        meetings=meetings,
        opportunities=opps,
    )


def test_certainty_tiers() -> None:
    assert certainty(10) == "too_early"
    assert certainty(200) == "directional"
    assert certainty(500) == "usable"
    assert certainty(2000) == "solid"


def test_summary_uses_kpi_hierarchy_and_flags_reply_vanity() -> None:
    summary = summarize([_metrics(600, 30, 10, 3, 2, "A"), _metrics(600, 45, 5, 0, 0, "B")])
    a, b = summary["campaigns"]
    assert a["opportunities_per_1k_sent"] == 3.33
    assert "reply_vanity_trap" in b["flags"]
    assert summary["ranking"][0].endswith("/ A")
    assert summary["totals"]["certainty"] == "usable"


def test_parse_metrics_csv_requires_columns(tmp_path) -> None:
    path = tmp_path / "m.csv"
    path.write_text(
        "campaign,sent,window_start,window_end,replied\nc,300,2026-08-01,2026-08-31,9\n"
    )
    rows = parse_metrics_csv(path, default_provider="manual")
    assert rows[0].provider == "manual"
    assert rows[0].effective_delivered == 300
    bad = tmp_path / "bad.csv"
    bad.write_text("name,count\nx,1\n")
    try:
        parse_metrics_csv(bad)
    except ValueError as exc:
        assert "campaign" in str(exc)
    else:
        raise AssertionError("missing columns must fail")


def test_next_walks_the_gates(tmp_path) -> None:
    settings = Settings(providers={})
    store = FileStore(tmp_path / ".gtm" / "store")
    result = evaluate(tmp_path, settings, store)
    assert result["next"]["stage"] == "context"
    (tmp_path / "context").mkdir()
    (tmp_path / "context" / "company.md").write_text(
        "# Company\n\n" + "\n".join(f"- fact {i} (observed)" for i in range(6))
    )
    (tmp_path / "market").mkdir()
    (tmp_path / "market" / "icp.md").write_text(
        "# ICP\n\n## Approved working definition\n\n"
        "B2B software companies with 20 to 80 employees that just hired a first revenue leader.\n"
    )
    result = evaluate(tmp_path, settings, store)
    assert [s["name"] for s in result["stages"] if s["done"]] == ["context", "icp", "crm"]
    assert result["next"]["skill"] == "design-gtm-experiment"


def test_files_workflow_end_to_end(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
        monkeypatch.delenv(name, raising=False)
    assert runner.invoke(app, ["--json", "init", "."]).exit_code == 0
    csv = tmp_path / "metrics.csv"
    csv.write_text(
        "provider,campaign,variant,window_start,window_end,sent,delivered,bounced,replied,"
        "positive_replies,meetings,opportunities\n"
        "manual,LinkedIn test,A,2026-08-01,2026-08-31,250,,0,18,7,2,1\n"
    )
    imported = runner.invoke(app, ["--json", "metrics", "import", "--file", str(csv)])
    assert imported.exit_code == 0, imported.output
    assert json.loads(imported.output)["store"] == "files"
    review = runner.invoke(app, ["--json", "review", "outreach"])
    assert review.exit_code == 0, review.output
    payload = json.loads(review.output)
    assert payload["rows"] == 1
    assert payload["campaigns"][0]["certainty"] == "directional"
    assert Path(payload["artifact"]).exists()
    nxt = runner.invoke(app, ["--json", "next"])
    assert nxt.exit_code == 0, nxt.output
    assert json.loads(nxt.output)["store"] == "files"
    draft = {
        "name": "Test",
        "provider": "lemlist",
        "audience_query": {},
        "steps": [{"day": 0, "channel": "email", "subject": "hi", "body": "Body"}],
        "status": "paused",
    }
    (tmp_path / "campaigns" / "test.json").write_text(json.dumps(draft))
    planned = runner.invoke(
        app, ["--json", "campaign", "plan", "--draft", str(tmp_path / "campaigns" / "test.json")]
    )
    assert planned.exit_code == 0, planned.output
    plan_id = json.loads(planned.output)["plan"]["id"]
    dry = runner.invoke(app, ["--json", "campaign", "apply", "--plan", plan_id, "--dry-run"])
    assert dry.exit_code == 0, dry.output
    assert json.loads(dry.output)["external_writes"] == 0
    assert not (tmp_path / ".gtm" / "store" / "apply-results" / f"{plan_id}.json").exists()
