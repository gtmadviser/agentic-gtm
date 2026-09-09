"""Stable `gtm` command surface."""

from __future__ import annotations

import json
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
from ..adapters.base import CapabilityError
from ..catalog import recommend
from ..config import Settings, env_value, has_supabase, load_settings
from ..contracts import CampaignDraft, CampaignMetrics
from ..database import Store, open_store
from ..safety import assert_plan_can_apply, make_plan, redact
from ..safety.checkpoints import review_record, verify_review, write_review
from ..starter import health as starter_health
from ..starter import upgrade_plan
from ..workflows import run_demo
from ..workflows.metrics import (
    CSV_COLUMNS,
    parse_metrics_csv,
    render_outreach_review,
    render_pipeline_review,
    render_weekly_review,
    summarize,
    summarize_pipeline,
)
from ..workflows.next import evaluate
from ..workspace import initialize_workspace, install_git_hook

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
metrics_app = typer.Typer(no_args_is_help=True)
starter_app = typer.Typer(no_args_is_help=True)
checkpoint_app = typer.Typer(no_args_is_help=True)
app.add_typer(db_app, name="db")
app.add_typer(sync_app, name="sync")
app.add_typer(campaign_app, name="campaign")
app.add_typer(review_app, name="review")
app.add_typer(report_app, name="report")
report_app.add_typer(slack_app, name="slack")
app.add_typer(stack_app, name="stack")
app.add_typer(metrics_app, name="metrics")
app.add_typer(starter_app, name="starter")
app.add_typer(checkpoint_app, name="checkpoint")
console = Console()

CREDENTIALS = {
    "hubspot": "HUBSPOT_ACCESS_TOKEN",
    "ai_ark": "AI_ARK_API_KEY",
    "blitz": "BLITZAPI_API_KEY",
    "lemlist": "LEMLIST_API_KEY",
    "instantly": "INSTANTLY_API_KEY",
    "slack": "SLACK_BOT_TOKEN|SLACK_WEBHOOK_URL",
    "harvest": "HARVEST_API_KEY",
}
METRICS_CONFLICT = "provider,campaign_id,variant,kind,unit,window_start,window_end"


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


def connected_store(ctx: typer.Context, settings: Settings | None = None) -> Store:
    quiet = bool((ctx.find_root().obj or {}).get("json"))
    return open_store(settings or load_settings(), quiet=quiet)


def configured_provider(settings: Settings, category: str) -> str:
    provider = settings.providers.get(category)
    if not provider:
        raise RuntimeError(f"Select providers.{category} explicitly in gtm.yaml")
    return provider


def _store_status(settings: Settings) -> dict[str, Any]:
    configured = settings.store.backend
    if configured == "supabase" or (configured == "auto" and has_supabase()):
        active = "supabase"
    else:
        active = "files"
    ready = active == "files" or has_supabase()
    return {
        "configured": configured,
        "active": active,
        "ready": ready,
        "path": settings.store.path if active == "files" else None,
        "supabase_credentials": has_supabase(),
        "policy_requires_supabase": settings.policies.require_supabase_for_connected_workflows,
    }


def _metrics_from_rows(rows: list[dict[str, Any]]) -> list[CampaignMetrics]:
    allowed = set(CampaignMetrics.model_fields)
    result = []
    for index, row in enumerate(rows, start=1):
        data = {k: v for k, v in row.items() if k in allowed}
        # Legacy CSV stores encoded a blank variant as null.
        data["variant"] = data.get("variant") or ""
        if data.get("source") == "instantly.analytics.legacy" or (
            data.get("source") == "instantly.analytics" and not data.get("kind")
        ):
            raise ValueError(
                "Legacy Instantly snapshots have no reliable campaign ID or reply semantics; archive those rows and resync before reviewing"
            )
        try:
            result.append(CampaignMetrics.model_validate(data))
        except ValueError as exc:
            raise ValueError(
                f"Invalid stored campaign metric at row {index}; repair it before reviewing"
            ) from exc
    return result


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
    hook = install_git_hook(directory)
    emit(
        ctx,
        {
            "directory": str(directory.resolve()),
            "created": created,
            "skipped_existing": True,
            "git_hook_installed": hook,
            "next": "cp .env.example .env, then run `gtm doctor` and `gtm next`",
        },
        title="Workspace initialized",
    )


@app.command()
def doctor(ctx: typer.Context, config: Path = typer.Option(Path("gtm.yaml"))) -> None:
    """Explain which capabilities are ready and how to enable the rest."""
    settings = load_settings(config)
    store = _store_status(settings)
    capabilities = {}
    for category, provider in settings.providers.items():
        names = [name for name in CREDENTIALS.get(provider, "").split("|") if name]
        ready = any(env_value(name, "").strip() for name in names)
        capabilities[category] = {
            "provider": provider,
            "ready": ready and store["ready"],
            "missing": [] if ready else names,
        }
    result = {
        "version": __version__,
        "config": str(config),
        "config_exists": (settings.workspace_root / "gtm.yaml").exists(),
        "demo": {"ready": True, "credentials": []},
        "store": store,
        "supabase": {
            "ready": has_supabase(),
            "migrations_ready": bool(env_value("SUPABASE_DB_URL")),
        },
        "capabilities": capabilities,
        "starter": starter_health(settings.workspace_root),
    }
    emit(ctx, result, title="Agentic GTM doctor")


@starter_app.command("check")
def check_starter(ctx: typer.Context, workspace: Path = Path(".")) -> None:
    emit(ctx, starter_health(workspace))


@starter_app.command("upgrade-plan")
def plan_starter_upgrade(ctx: typer.Context, candidate: Path, workspace: Path = Path(".")) -> None:
    """Compare a generated candidate with the installed baseline and client edits."""
    emit(ctx, upgrade_plan(workspace, candidate))


@checkpoint_app.command("record")
def checkpoint_record(ctx: typer.Context, artifact: list[str] = typer.Option(...), recipe_version: str = typer.Option(...), reviewer: str = typer.Option(...), out: Path = typer.Option(...), workspace: Path = Path(".")) -> None:
    """Record an already-performed review of concrete sample artifacts."""
    record = review_record(workspace, artifact, recipe_version, reviewer)
    write_review(out, record)
    emit(ctx, {"sha256": record["sha256"], "artifacts": len(artifact), "path": str(out)})


@checkpoint_app.command("verify")
def checkpoint_verify(ctx: typer.Context, checkpoint: Path, accepted_hash: str = typer.Option(...), recipe_version: str = typer.Option(...), workspace: Path = Path(".")) -> None:
    verify_review(workspace, json.loads(checkpoint.read_text()), accepted_hash, recipe_version)
    emit(ctx, {"valid": True, "external_actions": []})


@app.command("next")
def next_stage(
    ctx: typer.Context,
    config: Path = typer.Option(Path("gtm.yaml")),
    workspace: Path = typer.Option(Path("."), help="Workspace root."),
) -> None:
    """Report which stage is done and which skill to run next."""
    settings = load_settings(config)
    try:
        store: Store | None = open_store(settings, quiet=True)
    except RuntimeError:
        store = None
    emit(
        ctx,
        evaluate(settings.workspace_root if workspace == Path(".") else workspace, settings, store),
        title="Next stage",
    )


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
    load_settings()
    db_url = env_value("SUPABASE_DB_URL", "").strip()
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
        output = settings.resolve(Path(".gtm") / f"{provider}-inspection.json")
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
    store = connected_store(ctx, settings)
    counts = {}
    for table, records in pulled.items():
        body = [record.model_dump(mode="json") for record in records]
        store.upsert(table, body, "provider,provider_id")
        counts[table] = len(body)
    emit(ctx, {"provider": provider, "store": store.backend, "synced": counts, "idempotent": True})


@app.command()
def source(
    ctx: typer.Context,
    kind: str = typer.Argument(..., help="accounts or contacts"),
    query: Path = typer.Option(..., exists=True, readable=True, help="Provider query JSON."),
    limit: int = typer.Option(25, min=1, max=500),
    config: Path = typer.Option(Path("gtm.yaml")),
    dry_run: bool = typer.Option(
        False, help="Validate the query and show the call without running it."
    ),
) -> None:
    """Source accounts or contacts through the explicitly selected provider."""
    if kind not in {"accounts", "contacts"}:
        raise typer.BadParameter("kind must be accounts or contacts")
    settings = load_settings(config)
    provider = configured_provider(settings, "sourcing")
    filters = json.loads(query.read_text(encoding="utf-8"))
    if dry_run:
        emit(
            ctx,
            {
                "status": "dry_run",
                "provider": provider,
                "kind": kind,
                "limit": limit,
                "filters": filters,
                "credits": "this call consumes provider credits; approve before running",
            },
        )
        return
    adapter = adapter_for(provider)
    records = getattr(adapter, f"search_{kind}")(filters, limit=limit)
    store = connected_store(ctx, settings)
    store.upsert(kind, [item.model_dump(mode="json") for item in records], "provider,provider_id")
    emit(
        ctx,
        {
            "provider": provider,
            "store": store.backend,
            "kind": kind,
            "count": len(records),
            "provenance_recorded": True,
            "records": records,
        },
    )


@metrics_app.command("import")
def metrics_import(
    ctx: typer.Context,
    file: Path = typer.Option(..., "--file", exists=True, readable=True, help="Metrics CSV."),
    provider: str = typer.Option("import", help="Provider label when the CSV has no column."),
    config: Path = typer.Option(Path("gtm.yaml")),
) -> None:
    """Import campaign counts from any tool export or a manual channel log."""
    rows = parse_metrics_csv(file, default_provider=provider)
    settings = load_settings(config)
    store = connected_store(ctx, settings)
    summary = summarize(rows)  # Reject an invalid import before persisting its rows.
    store.upsert(
        "campaign_metrics", [row.model_dump(mode="json") for row in rows], METRICS_CONFLICT
    )
    emit(
        ctx,
        {
            "file": str(file),
            "store": store.backend,
            "imported": len(rows),
            "columns": CSV_COLUMNS,
            "totals": summary["totals"],
        },
        title="Metrics imported",
    )


def _campaign_payload(draft: CampaignDraft) -> dict[str, Any]:
    # Pure preflight: reject unsupported content before persisting an apply plan.
    from ..adapters.instantly.adapter import instantly_steps
    from ..adapters.lemlist.adapter import lemlist_step

    steps = [step.model_dump(mode="json") for step in draft.steps]
    if draft.provider == "instantly":
        instantly_steps(steps)
    elif draft.provider == "lemlist":
        for step in steps:
            lemlist_step(step)
    else:
        raise ValueError("No paused-campaign adapter for this provider")
    return {
        "desired_state": "paused",
        "campaign": {
            "name": draft.name,
            "schedule": draft.schedule.model_dump(mode="json"),
            "steps": [step.model_dump(mode="json") for step in draft.steps],
        },
    }


@campaign_app.command("plan")
def campaign_plan(
    ctx: typer.Context,
    draft_file: Path = typer.Option(..., "--draft", exists=True, readable=True),
    config: Path = typer.Option(Path("gtm.yaml")),
) -> None:
    """Create and persist an immutable plan for a paused campaign."""
    draft = CampaignDraft.model_validate_json(draft_file.read_text(encoding="utf-8"))
    variants = sum(len(step.all_variants()) for step in draft.steps)
    plan = make_plan(
        "campaign.create_paused",
        draft.provider,
        [str(draft.id)],
        _campaign_payload(draft),
        f"Create one paused campaign named {draft.name!r} with {len(draft.steps)} steps "
        f"and {variants} variants",
    )
    settings = load_settings(config)
    store = connected_store(ctx, settings)
    persisted = store.create_plan(plan)
    emit(
        ctx,
        {"store": store.backend, "plan": persisted},
        title="Review this plan before applying",
    )


@campaign_app.command("apply")
def campaign_apply(
    ctx: typer.Context,
    plan_id: UUID = typer.Option(..., "--plan", help="Explicit action plan UUID."),
    dry_run: bool = typer.Option(
        False, help="Validate the plan and show the write without doing it."
    ),
    config: Path = typer.Option(Path("gtm.yaml")),
) -> None:
    """Apply exactly one reviewed paused-campaign plan."""
    settings = load_settings(config)
    store = connected_store(ctx, settings)
    prior = store.applied_result(plan_id)
    if prior:
        emit(
            ctx,
            prior.model_copy(
                update={
                    "status": "already_applied",
                    "message": "Plan was already applied; no duplicate write",
                }
            ),
        )
        return
    plan = store.get_plan(plan_id)
    assert_plan_can_apply(plan)
    if dry_run:
        emit(
            ctx,
            {
                "status": "dry_run",
                "provider": plan.provider,
                "operation": plan.operation,
                "targets": plan.targets,
                "payload_summary": plan.payload_summary,
                "expires_at": plan.expires_at,
                "hash": plan.hash,
                "external_writes": 0,
            },
            title="Dry run: nothing was written",
        )
        return
    plan = store.claim_apply(plan_id)
    try:
        result = adapter_for(plan.provider).apply_campaign(plan)
    except Exception:
        store.mark_needs_review(plan_id)
        raise
    emit(ctx, store.record_apply(result), title="Campaign apply complete")


@sync_app.command("campaigns")
def sync_campaigns(ctx: typer.Context, config: Path = typer.Option(Path("gtm.yaml"))) -> None:
    """Pull campaign state, and campaign metrics where the provider supports it."""
    settings = load_settings(config)
    provider = configured_provider(settings, "sequencer")
    adapter = adapter_for(provider)
    campaigns = adapter.pull_campaigns()
    store = connected_store(ctx, settings)
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
    metrics_note: str | int
    try:
        metrics = adapter.pull_campaign_metrics()
        store.upsert(
            "campaign_metrics", [row.model_dump(mode="json") for row in metrics], METRICS_CONFLICT
        )
        metrics_note = len(metrics)
    except CapabilityError as exc:
        metrics_note = str(exc)
    emit(
        ctx,
        {
            "provider": provider,
            "store": store.backend,
            "count": len(records),
            "metrics": metrics_note,
            "idempotent": True,
        },
    )


def _write(destination: Path, text: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


@review_app.command("outreach")
def review_outreach(
    ctx: typer.Context,
    output: Path | None = typer.Option(None),
    config: Path = typer.Option(Path("gtm.yaml")),
) -> None:
    """Review campaign performance with the KPI hierarchy and certainty tiers."""
    settings = load_settings(config)
    store = connected_store(ctx, settings)
    metrics = _metrics_from_rows(store.select("campaign_metrics", {"limit": "10000"}))
    summary = summarize(metrics)
    now = datetime.now(UTC)
    destination = settings.resolve(
        output or Path("reports") / f"outreach-{now.date().isoformat()}.md"
    )
    _write(destination, render_outreach_review(summary, now))
    emit(ctx, {"kind": "outreach", "artifact": str(destination), "rows": len(metrics), **summary})


@review_app.command("pipeline")
def review_pipeline(
    ctx: typer.Context,
    output: Path | None = typer.Option(None),
    config: Path = typer.Option(Path("gtm.yaml")),
) -> None:
    """Review won, lost, and open pipeline separately."""
    settings = load_settings(config)
    store = connected_store(ctx, settings)
    opportunities = store.select("opportunities", {"limit": "10000"})
    summary = summarize_pipeline(opportunities)
    now = datetime.now(UTC)
    destination = settings.resolve(
        output or Path("reports") / f"pipeline-{now.date().isoformat()}.md"
    )
    _write(destination, render_pipeline_review(summary, now))
    emit(ctx, {"kind": "pipeline", "artifact": str(destination), **summary})


@review_app.command("weekly")
def review_weekly(
    ctx: typer.Context,
    output: Path | None = typer.Option(None),
    config: Path = typer.Option(Path("gtm.yaml")),
    workspace: Path = typer.Option(Path("."), help="Workspace root."),
) -> None:
    """Create the weekly cross-system GTM review."""
    settings = load_settings(config)
    store = connected_store(ctx, settings)
    metrics = _metrics_from_rows(store.select("campaign_metrics", {"limit": "10000"}))
    outreach = summarize(metrics)
    pipeline = summarize_pipeline(store.select("opportunities", {"limit": "10000"}))
    workspace = settings.workspace_root if workspace == Path(".") else workspace
    experiments = [
        path
        for path in (workspace / "experiments").glob("*")
        if path.suffix in {".json", ".md"} and path.name.lower() != "readme.md"
    ]
    try:
        pending = store.describe().get("pending_plans")
    except Exception:  # noqa: BLE001 - a describe failure must not block the review
        pending = "unknown"
    extras = {"experiments": len(experiments), "pending_plans": pending}
    now = datetime.now(UTC)
    destination = settings.resolve(
        output or Path("reports") / f"weekly-{now.date().isoformat()}.md"
    )
    _write(destination, render_weekly_review(outreach, pipeline, extras, now))
    emit(
        ctx,
        {
            "kind": "weekly",
            "artifact": str(destination),
            "outreach_totals": outreach["totals"],
            "pipeline": pipeline,
            **extras,
        },
    )


@slack_app.command("plan")
def slack_plan(
    ctx: typer.Context,
    report_file: Path = typer.Option(..., "--report", exists=True, readable=True),
    channel: str | None = typer.Option(None, help="Slack channel ID; defaults to env."),
    config: Path = typer.Option(Path("gtm.yaml")),
) -> None:
    """Create an immutable Slack report plan."""
    settings = load_settings(config)
    target = channel or env_value("SLACK_CHANNEL_ID", "").strip() or "webhook"
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
    settings = load_settings(config)
    store = connected_store(ctx, settings)
    emit(
        ctx,
        {"store": store.backend, "plan": store.create_plan(plan)},
        title="Review this Slack plan before applying",
    )


@slack_app.command("apply")
def slack_apply(
    ctx: typer.Context,
    plan_id: UUID = typer.Option(..., "--plan", help="Explicit action plan UUID."),
    dry_run: bool = typer.Option(
        False, help="Validate the plan and show the post without sending."
    ),
    config: Path = typer.Option(Path("gtm.yaml")),
) -> None:
    """Apply exactly one reviewed Slack report plan."""
    settings = load_settings(config)
    store = connected_store(ctx, settings)
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
    if dry_run:
        emit(
            ctx,
            {
                "status": "dry_run",
                "provider": "slack",
                "targets": plan.targets,
                "payload_summary": plan.payload_summary,
                "characters": len(str(plan.payload.get("text", ""))),
                "external_writes": 0,
            },
            title="Dry run: nothing was posted",
        )
        return
    if plan.provider != "slack" or plan.operation != "slack.post_report":
        raise ValueError("This plan does not authorize a Slack report")
    plan = store.claim_apply(plan_id)
    try:
        result = adapter_for("slack").apply_report(plan)
    except Exception:
        store.mark_needs_review(plan_id)
        raise
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
