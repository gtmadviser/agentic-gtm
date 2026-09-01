"""Stable `gtm` command surface."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any
from uuid import UUID

import typer
from rich.console import Console
from rich.table import Table

from .. import __version__
from ..adapters import adapter_for
from ..catalog import recommend
from ..config import Settings, has_supabase, load_settings
from ..contracts import CampaignDraft
from ..database import SupabaseStore
from ..safety import assert_plan_can_apply, make_plan, redact
from ..workflows import run_demo
from ..workspace import initialize_workspace

app = typer.Typer(
    no_args_is_help=True,
    invoke_without_command=True,
    help="Local-first, approval-gated GTM operations.",
)
db_app = typer.Typer(no_args_is_help=True)
sync_app = typer.Typer(no_args_is_help=True)
campaign_app = typer.Typer(no_args_is_help=True)
review_app = typer.Typer(no_args_is_help=True)
report_app = typer.Typer(no_args_is_help=True)
slack_app = typer.Typer(no_args_is_help=True)
stack_app = typer.Typer(no_args_is_help=True)
app.add_typer(db_app, name="db")
app.add_typer(sync_app, name="sync")
app.add_typer(campaign_app, name="campaign")
app.add_typer(review_app, name="review")
app.add_typer(report_app, name="report")
report_app.add_typer(slack_app, name="slack")
app.add_typer(stack_app, name="stack")
console = Console()


def _json_default(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, (datetime, UUID, Path)):
        return str(value)
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def emit(ctx: typer.Context, payload: Any, *, title: str | None = None) -> None:
    safe = redact(payload)
    if (ctx.find_root().obj or {}).get("json"):
        typer.echo(json.dumps(safe, indent=2, sort_keys=True, default=_json_default))
        return
    if title:
        console.print(f"[bold]{title}[/bold]")
    if isinstance(safe, dict):
        table = Table(show_header=False, box=None)
        for key, value in safe.items():
            rendered = (
                json.dumps(value, default=_json_default)
                if isinstance(value, (dict, list))
                else str(value)
            )
            table.add_row(str(key).replace("_", " ").title(), rendered)
        console.print(table)
    else:
        console.print(safe)


def connected_store() -> SupabaseStore:
    if not has_supabase():
        raise RuntimeError(
            "Connected workflows require SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env"
        )
    return SupabaseStore()


def configured_provider(settings: Settings, category: str) -> str:
    provider = settings.providers.get(category)
    if not provider:
        raise RuntimeError(f"Select providers.{category} explicitly in gtm.yaml")
    return provider


@app.callback()
def root(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the installed version.",
        is_eager=True,
    ),
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    if version:
        typer.echo(__version__)
        raise typer.Exit()


@app.command()
def demo(
    ctx: typer.Context,
    output: Path = typer.Option(Path("demo-output"), help="Artifact directory."),
) -> None:
    """Run a no-key workflow against wholly fictional data."""
    emit(ctx, run_demo(output), title="Synthetic demo complete")


@app.command("init")
def initialize(
    ctx: typer.Context,
    directory: Path = typer.Argument(Path(".")),
) -> None:
    """Initialize a company-owned GTM workspace without overwriting files."""
    created = initialize_workspace(directory)
    version_file = directory / ".agentic-gtm-version"
    if not version_file.exists():
        version_file.write_text(f"{__version__}\n", encoding="utf-8")
        created.append(version_file.name)
    emit(
        ctx,
        {"directory": str(directory.resolve()), "created": created, "skipped_existing": True},
        title="Workspace initialized",
    )


@app.command()
def doctor(ctx: typer.Context, config: Path = typer.Option(Path("gtm.yaml"))) -> None:
    """Explain which capabilities are ready and how to enable the rest."""
    settings = load_settings(config)
    credential_map = {
        "hubspot": "HUBSPOT_ACCESS_TOKEN",
        "ai_ark": "AI_ARK_API_KEY",
        "blitz": "BLITZAPI_API_KEY",
        "lemlist": "LEMLIST_API_KEY",
        "instantly": "INSTANTLY_API_KEY",
        "slack": "SLACK_BOT_TOKEN|SLACK_WEBHOOK_URL",
    }
    capabilities = {}
    for category, provider in settings.providers.items():
        names = credential_map.get(provider, "").split("|")
        ready = any(os.getenv(name, "").strip() for name in names if name)
        capabilities[category] = {
            "provider": provider,
            "ready": ready and has_supabase(),
            "missing": []
            if ready and has_supabase()
            else [
                *([] if has_supabase() else ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]),
                *([] if ready else names),
            ],
        }
    result = {
        "config": str(config),
        "config_exists": config.exists(),
        "demo": {"ready": True, "credentials": []},
        "supabase": {
            "ready": has_supabase(),
            "migrations_ready": bool(os.getenv("SUPABASE_DB_URL")),
        },
        "capabilities": capabilities,
    }
    emit(ctx, result, title="Agentic GTM doctor")


@db_app.command("migrate")
def db_migrate(
    ctx: typer.Context,
    dry_run: bool = typer.Option(False, help="List migrations without connecting."),
) -> None:
    """Apply packaged, idempotent migrations to the startup-owned database."""
    migration_dir = files("agentic_gtm").joinpath("sql")
    migrations = sorted(item for item in migration_dir.iterdir() if item.name.endswith(".sql"))
    if dry_run:
        emit(ctx, {"migrations": [item.name for item in migrations], "applied": False})
        return
    db_url = os.getenv("SUPABASE_DB_URL", "").strip()
    if not db_url:
        raise RuntimeError("SUPABASE_DB_URL is required only for gtm db migrate")
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError(
            "Install database support: uv tool install 'gtmadviser-agentic-gtm[postgres]'"
        ) from exc
    with psycopg.connect(db_url) as connection, connection.transaction():
        for migration in migrations:
            connection.execute(migration.read_text(encoding="utf-8"))
    emit(ctx, {"migrations": [item.name for item in migrations], "applied": True})


@sync_app.command("crm")
def sync_crm(ctx: typer.Context, config: Path = typer.Option(Path("gtm.yaml"))) -> None:
    """Inspect HubSpot, require field-map confirmation, then pull normalized CRM data."""
    settings = load_settings(config)
    provider = configured_provider(settings, "crm")
    adapter = adapter_for(provider)
    field_map = settings.field_maps.get(provider) or {}
    if not field_map:
        inspection = adapter.inspect()
        output = Path(".gtm") / f"{provider}-inspection.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(inspection, indent=2, default=_json_default), encoding="utf-8")
        emit(
            ctx,
            {
                "status": "field_map_confirmation_required",
                "inspection": str(output),
                "next": f"Confirm field_maps.{provider} in gtm.yaml, then rerun gtm sync crm",
            },
        )
        raise typer.Exit(2)
    pulled = adapter.pull(field_map)
    store = connected_store()
    counts = {}
    for table, records in pulled.items():
        body = [record.model_dump(mode="json") for record in records]
        store.upsert(table, body, "provider,provider_id")
        counts[table] = len(body)
    emit(ctx, {"provider": provider, "synced": counts, "idempotent": True})


@app.command()
def source(
    ctx: typer.Context,
    kind: str = typer.Argument(..., help="accounts or contacts"),
    query: Path = typer.Option(..., exists=True, readable=True, help="Provider query JSON."),
    limit: int = typer.Option(25, min=1, max=500),
    config: Path = typer.Option(Path("gtm.yaml")),
) -> None:
    """Source accounts or contacts through the explicitly selected provider."""
    if kind not in {"accounts", "contacts"}:
        raise typer.BadParameter("kind must be accounts or contacts")
    settings = load_settings(config)
    provider = configured_provider(settings, "sourcing")
    adapter = adapter_for(provider)
    filters = json.loads(query.read_text(encoding="utf-8"))
    records = getattr(adapter, f"search_{kind}")(filters, limit=limit)
    store = connected_store()
    store.upsert(kind, [item.model_dump(mode="json") for item in records], "provider,provider_id")
    emit(
        ctx,
        {
            "provider": provider,
            "kind": kind,
            "count": len(records),
            "provenance_recorded": True,
            "records": records,
        },
    )


def _campaign_payload(draft: CampaignDraft) -> dict[str, Any]:
    return {
        "desired_state": "paused",
        "campaign": {
            "name": draft.name,
            "schedule": draft.schedule,
            "steps": draft.steps,
        },
    }


@campaign_app.command("plan")
def campaign_plan(
    ctx: typer.Context,
    draft_file: Path = typer.Option(..., "--draft", exists=True, readable=True),
) -> None:
    """Create and persist an immutable plan for a paused campaign."""
    draft = CampaignDraft.model_validate_json(draft_file.read_text(encoding="utf-8"))
    plan = make_plan(
        "campaign.create_paused",
        draft.provider,
        [str(draft.id)],
        _campaign_payload(draft),
        f"Create one paused campaign named {draft.name!r}",
    )
    persisted = connected_store().create_plan(plan)
    emit(ctx, persisted, title="Review this plan before applying")


@campaign_app.command("apply")
def campaign_apply(
    ctx: typer.Context,
    plan_id: UUID = typer.Option(..., "--plan", help="Explicit action plan UUID."),
) -> None:
    """Apply exactly one reviewed paused-campaign plan."""
    store = connected_store()
    prior = store.applied_result(plan_id)
    if prior:
        result = prior.model_copy(
            update={
                "status": "already_applied",
                "message": "Plan was already applied; no duplicate write",
            }
        )
        emit(ctx, result)
        return
    plan = store.get_plan(plan_id)
    assert_plan_can_apply(plan)
    result = adapter_for(plan.provider).apply_campaign(plan)
    emit(ctx, store.record_apply(result), title="Campaign apply complete")


@sync_app.command("campaigns")
def sync_campaigns(ctx: typer.Context, config: Path = typer.Option(Path("gtm.yaml"))) -> None:
    """Pull campaign state from the selected sequencer."""
    settings = load_settings(config)
    provider = configured_provider(settings, "sequencer")
    campaigns = adapter_for(provider).pull_campaigns()
    store = connected_store()
    records = [
        {
            "provider": provider,
            "provider_id": str(item.get("id") or item.get("_id")),
            "observed_at": datetime.now(UTC).isoformat(),
            "body": item,
        }
        for item in campaigns
        if item.get("id") or item.get("_id")
    ]
    store.upsert("campaigns", records, "provider,provider_id")
    emit(ctx, {"provider": provider, "count": len(records), "idempotent": True})


def _write_review(kind: str, data: dict[str, Any], output: Path) -> None:
    lines = [f"# {kind.title()} GTM review", "", f"Generated: {datetime.now(UTC).isoformat()}", ""]
    lines.extend(["## Approved aggregates", ""])
    lines.extend(f"- {key.replace('_', ' ').title()}: {value}" for key, value in data.items())
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Add an evidence-backed interpretation; do not infer causality from an aggregate.",
            "",
            "## Owners and next actions",
            "",
            "- Assign one human owner and due date to each approved action.",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _review(ctx: typer.Context, kind: str, output: Path | None) -> None:
    store = connected_store()
    tables = {
        "outreach": ("campaigns", "metric_snapshots"),
        "pipeline": ("opportunities", "accounts"),
        "weekly": ("opportunities", "campaigns", "experiments", "metric_snapshots"),
    }[kind]
    aggregates = {
        f"{table}_records": len(store.select(table, {"limit": "10000"})) for table in tables
    }
    destination = output or Path("reports") / f"{kind}-{datetime.now(UTC).date().isoformat()}.md"
    _write_review(kind, aggregates, destination)
    emit(ctx, {"kind": kind, "artifact": str(destination), "aggregates": aggregates})


@review_app.command("outreach")
def review_outreach(ctx: typer.Context, output: Path | None = typer.Option(None)) -> None:
    """Review normalized campaign performance."""
    _review(ctx, "outreach", output)


@review_app.command("pipeline")
def review_pipeline(ctx: typer.Context, output: Path | None = typer.Option(None)) -> None:
    """Review won, lost, and open pipeline separately."""
    _review(ctx, "pipeline", output)


@review_app.command("weekly")
def review_weekly(ctx: typer.Context, output: Path | None = typer.Option(None)) -> None:
    """Create the weekly cross-system GTM review."""
    _review(ctx, "weekly", output)


@slack_app.command("plan")
def slack_plan(
    ctx: typer.Context,
    report_file: Path = typer.Option(..., "--report", exists=True, readable=True),
    channel: str | None = typer.Option(None, help="Slack channel ID; defaults to env."),
) -> None:
    """Create an immutable Slack report plan."""
    target = channel or os.getenv("SLACK_CHANNEL_ID", "").strip() or "webhook"
    payload = {
        "channel": target,
        "text": report_file.read_text(encoding="utf-8"),
        "unfurl_links": False,
    }
    plan = make_plan(
        "slack.post_report",
        "slack",
        [target],
        payload,
        f"Post approved report {report_file.name} to {target}",
    )
    emit(ctx, connected_store().create_plan(plan), title="Review this Slack plan before applying")


@slack_app.command("apply")
def slack_apply(
    ctx: typer.Context,
    plan_id: UUID = typer.Option(..., "--plan", help="Explicit action plan UUID."),
) -> None:
    """Apply exactly one reviewed Slack report plan."""
    store = connected_store()
    prior = store.applied_result(plan_id)
    if prior:
        emit(
            ctx,
            prior.model_copy(
                update={
                    "status": "already_applied",
                    "message": "Plan was already applied; no duplicate post",
                }
            ),
        )
        return
    plan = store.get_plan(plan_id)
    assert_plan_can_apply(plan)
    result = adapter_for("slack").apply_report(plan)
    emit(ctx, store.record_apply(result), title="Slack apply complete")


@stack_app.command("recommend")
def stack_recommend(
    ctx: typer.Context,
    require: list[str] = typer.Option([], "--require", help="Required capability; repeatable."),
    category: str | None = typer.Option(None),
) -> None:
    """Rank tools by declared capability fit, independent of affiliate status."""
    emit(ctx, recommend(set(require), category), title="Requirement-first recommendations")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
