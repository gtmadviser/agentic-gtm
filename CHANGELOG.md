# Changelog

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
