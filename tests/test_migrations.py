from importlib.resources import files


def test_initial_migration_is_idempotent_and_complete() -> None:
    sql = files("agentic_gtm").joinpath("sql", "0001_initial.sql").read_text(encoding="utf-8")
    for table in (
        "accounts",
        "contacts",
        "opportunities",
        "activities",
        "evidence",
        "experiments",
        "campaigns",
        "action_plans",
        "apply_results",
    ):
        assert f"create table if not exists {table}" in sql.lower()
    assert "unique (provider, provider_id)" in sql.lower()
    assert "enable row level security" in sql.lower()
