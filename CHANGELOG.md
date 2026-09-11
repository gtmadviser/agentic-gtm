# Changelog

## Unreleased

- Add a `discovery` stage wrapping Harvest `post-search`, so engagement collection is
  no longer limited to the approved company/founder/employee roster. An announcement is
  also carried by investors and press, whose posts reach buyers the roster's own posts
  never touch. Candidates are written `approved: false` and ranked by reach; keyword
  search is fuzzy, so review is required before any engagement spend.
- Budget `max_records` per (source, endpoint) instead of once per run. A shared counter
  let `post-reactions` consume the whole cap and leave `post-comments` with zero pages,
  silently dropping the higher-signal commenters. `normalize` now applies the cap the
  same way rather than discarding records the fetch stage paid for.
- Add `export`, which joins people and events into a review-ready sheet keeping the
  specific reaction type, per-post interaction detail and verbatim comments, with the
  rationale columns left blank for a human to fill.
- Skip skill-resource `force_include` for editable wheels. It materialised a real
  `site-packages/agentic_gtm/resources/` tree with no `__init__.py`, which was picked up
  as a namespace portion for `agentic_gtm` and shadowed the source package: importing
  `agentic_gtm` succeeded while `agentic_gtm.workflows` raised `ModuleNotFoundError`.

- Extend the LinkedIn playbook from explicit posts to founder/company/employee
  discovery, reviewed current-role rosters, selective enrichment and routed outreach.
- Add client/account-scoped enrichment cache, atomic paid-call reservations and
  migration `0004_enrichment.sql`; integrate the five-stage Harvest helper.
- Add separate company/persona qualification guards, synthetic skill evaluations,
  content-bound sample checkpoints and reviewable starter upgrade plans.

- Add `linkedin-engager-outreach`: Harvest post collection, local identity/event
  dedupe, evidence-based ICP scoring, account/contact CRM routing and reviewed
  LinkedIn outreach handoff. Includes a bounded, cached collection helper and
  synthetic regression tests. No client data or live sending is bundled.
- Resolve workspace `.env`, local stores and generated reports relative to the
  selected configuration; prevent credential leakage between loaded workspaces.
- Preserve empty strings/nulls and existing record IDs in local CSV upserts;
  serialize file writes, expose JSON apply results to readiness checks, and
  count pending plans accurately. Generate stable IDs for new provider records.
- Claim plans before campaign/Slack writes and block automatic replay after
  failures. Mutating HTTP requests are no longer retried implicitly.
- Distinguish lifetime metric snapshots from interval counts, group by campaign
  ID, reject overlapping windows/mixed units and preserve unknown outcomes.
  Instantly human replies use the unique field; opportunities are not relabeled
  positive replies. Weekly reports state their actual snapshot scope.
- Reject unsupported lemlist variants before writes; expose manual schedule and
  content verification requirements. Fix the copy-to-draft skill handoff.
- Include canonical skills/helpers in installed wheels and initialized
  workspaces; copy all migrations into generated starters.
- Add migration `0003_reliability.sql`. See [upgrade notes](docs/reliability-upgrade.md).

## 0.2.0 (2026-09-02)

The playbook release. The 0.1.0 skills were policy statements; 0.2.0 fills them with the rules, numbers, checklists and references from real outbound engagements, and makes the CLI usable without a database.

### Skills
- Every skill rewritten to 90-150 lines with 2-7 reference files: procedure, hard rules with numbers, checklist, output contract, failure modes.
- New: `write-outreach` (copy rules, subject lines, follow-ups, variables and spintax, DACH pack, anti-slop writing gate, 12-point review rubric).
- New: `handover-gtm-engine` (operator routine, acceptance checklist, handoff and wrap-up templates, hard rules for agents).
- New: `gtm-kickoff` (guided entry point that runs `gtm next` and routes).
- Renamed: `source-market` is now `source-tam`.
- `audit-deliverability` carries the fleet thresholds, placement tests, burn detection and launch gates.
- `review-outreach` carries the KPI hierarchy, reply taxonomy, certainty tiers and retro method.

### CLI
- Store abstraction: Supabase by default, CSV tables and JSON plans under `.gtm/store/` when no credentials are present. `store.backend` in `gtm.yaml`: `auto`, `supabase`, `files`.
- `gtm next`: deterministic gate machine over the workspace.
- `gtm metrics import --file <csv>`: bring counts from any tool export or a manual channel.
- `gtm review outreach|pipeline|weekly` compute real rates: bounce, reply, positive reply, per-1k metrics, certainty tiers, reply-vanity and bounce flags.
- `--dry-run` on `campaign apply`, `report slack apply`, and `source`.
- `gtm sync campaigns` pulls campaign metrics where the adapter supports it (Instantly).
- `gtm init` writes a pre-commit secret guard, a Claude Code Stop hook, an agent router with hard rules, and a knowledge-layer folder; installs the hook when the workspace is a Git repository.

### Adapters and contracts
- Typed `CampaignStep`, `CampaignVariant`, `CampaignSchedule`, `CampaignMetrics`.
- Instantly: sends the required `campaign_schedule`, translates steps to sequences, pulls analytics.
- lemlist: translates steps to the sequences endpoint (`message`, `type`, `delayType`).
- Explicit User-Agent on every provider call.
- `stack recommend` returns no recommendation when nothing matches a requirement.

### Docs
- `docs/providers/`: Instantly, lemlist, HubSpot, Supabase and PostgREST, mailbox and domain providers, sourcing and verification, Slack.
- `docs/data-and-privacy.md`.
- Migration `0002_campaign_metrics.sql`.

## 0.1.0 (2026-09-01)

Public alpha: twelve thin skills, the `gtm` CLI, plan/apply safety, HubSpot, AI Ark, Blitz, lemlist, Instantly and Slack adapters, Supabase store.
