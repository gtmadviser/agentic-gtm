import json

from typer.testing import CliRunner

from agentic_gtm.cli.app import app

runner = CliRunner()


def test_version_without_command() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == "0.1.0"


def test_demo_creates_all_acceptance_artifacts(tmp_path) -> None:
    output = tmp_path / "demo"
    result = runner.invoke(app, ["--json", "demo", "--output", str(output)])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["synthetic"] is True
    assert payload["campaign_status"] == "paused"
    assert payload["external_writes"] == 0
    assert sorted(path.name for path in output.iterdir()) == [
        "campaign-plan.json",
        "experiment.json",
        "icp.json",
        "weekly-review.md",
    ]


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
