import json

from typer.testing import CliRunner

from agentic_gtm.cli.app import app

runner = CliRunner()


def test_version_without_command() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.2.0"


def test_demo_creates_all_acceptance_artifacts(tmp_path) -> None:
    output = tmp_path / "demo"
    result = runner.invoke(app, ["--json", "demo", "--output", str(output)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["synthetic"] is True
    assert payload["campaign_status"] == "paused"
    assert payload["external_writes"] == 0
    assert sorted(path.name for path in output.iterdir()) == [
        "campaign-draft.json",
        "campaign-plan.json",
        "experiment.json",
        "icp.json",
        "metrics-sample.csv",
        "outreach-review.md",
        "weekly-review.md",
    ]
    review = (output / "outreach-review.md").read_text(encoding="utf-8")
    assert "reply_vanity_trap" in review


def test_init_never_overwrites_existing_file(tmp_path) -> None:
    (tmp_path / "context").mkdir()
    company = tmp_path / "context" / "company.md"
    company.write_text("keep me", encoding="utf-8")
    result = runner.invoke(app, ["--json", "init", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert company.read_text(encoding="utf-8") == "keep me"


def test_doctor_disables_only_missing_capabilities(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "synthetic-test-key")
    monkeypatch.setenv("HUBSPOT_ACCESS_TOKEN", "synthetic-test-token")
    (tmp_path / "gtm.yaml").write_text(
        "version: 1\nproviders:\n  crm: hubspot\n  sourcing: blitz\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["--json", "doctor"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["capabilities"]["crm"]["ready"] is True
    assert payload["capabilities"]["sourcing"]["ready"] is False
    assert payload["demo"]["ready"] is True
    assert payload["store"]["active"] == "supabase"


def test_doctor_reports_files_store_without_supabase(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("LEMLIST_API_KEY", "synthetic-test-key")
    (tmp_path / "gtm.yaml").write_text("version: 1\nproviders:\n  sequencer: lemlist\n")
    result = runner.invoke(app, ["--json", "doctor"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["store"]["active"] == "files"
    assert payload["capabilities"]["sequencer"]["ready"] is True


def test_init_writes_hooks_and_router(tmp_path) -> None:
    result = runner.invoke(app, ["--json", "init", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "scripts" / "git-hooks" / "pre-commit").exists()
    assert (tmp_path / ".claude" / "settings.json").exists()
    assert (tmp_path / "context" / "knowledge" / "README.md").exists()
    assert "gtm-kickoff" in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "store:" in (tmp_path / "gtm.yaml").read_text(encoding="utf-8")
