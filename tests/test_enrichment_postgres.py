"""Optional real PostgreSQL contract checks; use an isolated synthetic database only."""

import os
from pathlib import Path
from uuid import uuid4

import pytest

from agentic_gtm.enrichment import PaidCalls, PaidRun, fingerprint

psycopg = pytest.importorskip("psycopg")
TEST_HOST = os.getenv("GTM_TEST_PG_HOST") or os.getenv("GTM_TEST_PG_SOCKET")
pytestmark = pytest.mark.skipif(not TEST_HOST, reason="No isolated test database configured")


@pytest.fixture(scope="module", autouse=True)
def isolated_schema():
    with psycopg.connect(host=TEST_HOST, port=55439, dbname="postgres") as connection:
        for role in ("anon", "authenticated", "service_role"):
            if not connection.execute("select 1 from pg_roles where rolname = %s", (role,)).fetchone():
                connection.execute(psycopg.sql.SQL("create role {}").format(psycopg.sql.Identifier(role)))
        migration = (Path(__file__).resolve().parents[1] / "src/agentic_gtm/sql/0004_enrichment.sql").read_text()
        connection.execute(migration)
        connection.execute(migration)  # Idempotent upgrade on the same synthetic schema.


class PgStore:
    def enrichment_rpc(self, operation, payload):
        from psycopg.types.json import Jsonb

        with psycopg.connect(
            host=TEST_HOST, port=55439, dbname="postgres"
        ) as connection:
            return connection.execute(
                "select gtm_enrichment(%s, %s)", (operation, Jsonb(payload))
            ).fetchone()[0]


def paid(client_id):
    return PaidCalls(
        PgStore(),
        PaidRun(
            client_id=client_id,
            account_scope="synthetic",
            provider="test",
            plan_hash=fingerprint("fixture"),
            max_calls=2,
            budget_microusd=25,
            prices_microusd={"profile": 25},
            price_basis="synthetic",
        ),
    )


def call(run, inputs, callback=lambda: {"synthetic": True}):
    return run.call("profile", inputs, callback, schema_version="1", ttl_seconds=60)


def test_sql_cache_budget_and_uncertain_reservations():
    client = "synthetic-" + str(uuid4())
    first, second = paid(client), paid(client)
    assert call(first, {"id": "same"})["action"] == "fetched"
    assert (
        call(second, {"id": "same"}, lambda: pytest.fail("must use cache"))["action"] == "cache_hit"
    )
    assert second.summary()["requests"] == 0
    with pytest.raises(psycopg.Error, match="spend ceiling"):
        call(first, {"id": "different"})
    with pytest.raises(TimeoutError):
        call(second, {"id": "timeout"}, lambda: (_ for _ in ()).throw(TimeoutError("synthetic")))
    assert second.summary()["reserved_microusd"] == 25
    with pytest.raises(psycopg.Error, match="uncertain"):
        call(paid(client), {"id": "timeout"})


def test_sql_concurrent_runs_share_pending_lock():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    first, second = paid("synthetic-" + str(uuid4())), None
    second = paid(first.run.client_id)
    entered, release = Event(), Event()

    def fetch():
        entered.set()
        assert release.wait(5)
        return {"synthetic": True}

    with ThreadPoolExecutor(2) as executor:
        future = executor.submit(call, first, {"id": "shared"}, fetch)
        assert entered.wait(5)
        try:
            with pytest.raises(psycopg.Error, match="pending"):
                call(second, {"id": "shared"})
        finally:
            release.set()
        assert future.result()["action"] == "fetched"
    assert call(second, {"id": "shared"})["action"] == "cache_hit"
