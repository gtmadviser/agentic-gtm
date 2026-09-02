from importlib.resources import files
from pathlib import Path


def _sql() -> str:
    sql_dir = files("agentic_gtm").joinpath("sql")
    return "\n".join(
        item.read_text(encoding="utf-8")
        for item in sorted(sql_dir.iterdir(), key=lambda item: item.name)
        if item.name.endswith(".sql")
    )


def test_migrations_are_idempotent_and_complete() -> None:
    sql = _sql().lower()
    for table in (
        "accounts",
        "contacts",
        "opportunities",
        "activities",
        "evidence",
        "experiments",
        "campaigns",
        "campaign_metrics",
        "action_plans",
        "apply_results",
    ):
        assert f"create table if not exists {table}" in sql
    assert "unique (provider, provider_id)" in sql
    assert "enable row level security" in sql
    assert "alter table campaign_metrics enable row level security" in sql


def test_packaged_and_repo_migrations_match() -> None:
    root = Path(__file__).resolve().parents[1]
    packaged = {
        item.name: item.read_text(encoding="utf-8")
        for item in files("agentic_gtm").joinpath("sql").iterdir()
        if item.name.endswith(".sql")
    }
    repo = {
        path.name: path.read_text(encoding="utf-8")
        for path in (root / "supabase" / "migrations").glob("*.sql")
    }
    assert packaged == repo
