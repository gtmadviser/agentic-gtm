# Agentic GTM

> **Public alpha (`0.2.0`)**. Skills and the synthetic demo are ready to use. Connected provider workflows need live-test credentials before a `1.0` release.

An open, local-first GTM operating system for technical founders and first GTM hires. Fifteen portable Agent Skills carry the playbooks from real outbound engagements: copy rules, deliverability thresholds, experiment design, the KPI hierarchy, handover. A deterministic `gtm` CLI reads your tools, keeps operational data in infrastructure you own, writes reviewable Markdown and JSON artifacts, and requires explicit approval before any external write.

```text
Agent Skill (skills/<name>/SKILL.md + references/)
      |
      v
deterministic gtm CLI -> provider adapter -> your sequencer, CRM, sourcing tool
      |
      +-> store: your Supabase project (default) or CSV tables under .gtm/store/
      +-> reviewable artifacts in Git: context/, market/, experiments/, campaigns/, reports/
```

No hosted service, no telemetry, no shared backend, no autonomous scheduler, no activation or send command, no MCP server. Credentials stay in environment variables.

## Quick start

Requires Python 3.11+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv tool install git+https://github.com/gtmadviser/agentic-gtm.git
gtm demo                      # fictional data, no keys, writes seven artifacts
gtm init my-gtm && cd my-gtm  # workspace, agent router, hooks, secret guard
cp .env.example .env
gtm doctor                    # which store and providers are ready
gtm next                      # which stage you are in and which skill to run
```

Then open the workspace in Claude Code or Codex and start with the `gtm-kickoff` skill. It runs `gtm next`, explains the stage model, and routes you.

### With or without a database

The store is Supabase by default. Set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`, run `gtm db migrate` once, and every command writes there.

Without those two variables the CLI keeps CSV tables and JSON plans under `.gtm/store/` (gitignored). Every command works the same way. Import counts from any tool export or a manual LinkedIn routine with `gtm metrics import --file metrics.csv`. This is enough for a first experiment. Switch to Supabase when a second person needs the data. `store.backend` in `gtm.yaml` pins the choice (`auto`, `supabase`, `files`).

## Skills

| Stage | Skill | What it carries |
|---|---|---|
| entry | `gtm-kickoff` | routing table, first session, minimal stack |
| context | `onboard-company-brain` | evidence labels, decision register, source register, knowledge layer |
| market | `map-market` | competitor profiles, signal sources, positioning hypotheses |
| icp | `refine-icp` | ICP from closed deals, best/worst customer, ICP template |
| crm | `inspect-crm` | field-map confirmation, won/lost/open analysis |
| experiment | `design-gtm-experiment` | preregistration template, sample sizes, hypothesis register, learnings log |
| audience | `source-tam` | sourcing waterfall, signal schema, mandatory filters, suppression, credit approval, vendor evaluation |
| audience | `research-accounts` | signal playbooks, personalization tiers, context-variable pattern |
| copy | `write-outreach` | copy rules, subject lines, follow-ups, variables and spintax, DACH pack, anti-slop gate and eval, review rubric |
| reach | `stage-campaign` | campaign structure, pre-launch checklist, draft schema, plan then apply |
| reach | `audit-deliverability` | thresholds, mailbox fleet, placement tests, burn detection, incident response, launch gates |
| measure | `review-outreach` | KPI hierarchy, reply taxonomy, retro method, metrics CSV |
| iterate | `weekly-gtm-review` | weekly rhythm, monthly review, report template |
| deals | `advance-deals` | meeting prep, follow-up, evidence-gap questions |
| handover | `handover-gtm-engine` | operator routine, acceptance checklist, handoff and wrap-up templates, hard rules for agents |

Every skill has a numbered procedure, hard rules with numbers, a checklist, an output contract, failure modes, and reference files. Use the repository as a Claude Code or Codex plugin, or point any shell-capable agent at `skills/` and the installed `gtm` command.

## Commands

```text
gtm demo
gtm init
gtm doctor
gtm next
gtm db migrate
gtm sync crm
gtm sync campaigns
gtm source accounts|contacts --query <json> [--dry-run]
gtm metrics import --file <csv>
gtm campaign plan --draft <json>
gtm campaign apply --plan <plan-id> [--dry-run]
gtm review outreach|pipeline|weekly
gtm report slack plan --report <md>
gtm report slack apply --plan <plan-id> [--dry-run]
gtm stack recommend --require <capability>
```

Add global `--json` before the command for stable machine-readable output. `gtm review` computes bounce rate, reply rate, positive reply rate, and positive replies, meetings and opportunities per 1k sent, with a certainty tier by sends and flags for bounce above 2% and the reply-vanity trap.

## Safety contract

- Reads run only inside the scopes declared in `gtm.yaml`.
- External writes first create an immutable action plan with exact targets, a payload summary, an idempotency key, and a SHA-256 hash.
- Apply commands require an explicit plan ID, support `--dry-run`, and reject changed, expired, or already-applied plans.
- Sequencer adapters only create paused campaigns. There is no send or activate command.
- Because both sequencer APIs may return a new empty shell as running, adapters pause the shell before adding any sequence content. They never add contacts. A failed pause aborts and reports the empty shell ID.
- Every credit-consuming call is shown as a plan first.
- `gtm init` installs a pre-commit secret guard that blocks `.env` values, credential literals and spreadsheets, and a Claude Code Stop hook that flags uncommitted work.
- Secrets are read from environment variables, never CLI flags.

See [SECURITY.md](SECURITY.md), [OPERATING-CONTRACT.md](OPERATING-CONTRACT.md), [docs/architecture.md](docs/architecture.md), [docs/data-and-privacy.md](docs/data-and-privacy.md) and [docs/providers/](docs/providers/).

## Providers

| Category | Adapters |
|---|---|
| CRM | HubSpot |
| Sourcing | AI Ark, Blitz |
| Sequencing | lemlist, Instantly (with analytics pull) |
| Collaboration | Slack |
| Store | Supabase, files |

Provider selection is explicit in `gtm.yaml`. Affiliate status never selects or ranks a provider; a requirement that matches nothing returns no recommendation. The versioned optional catalog includes the disclosure shown whenever a tracked link appears.

## Licensing

Python code, JSON schemas, SQL migrations, and tests are MIT licensed. Skills, playbooks, documentation, and written frameworks are CC BY 4.0. See [LICENSES.md](LICENSES.md) for the path-level matrix.

## Services

The free system is fully functional.

- Want this adapted to your company? [GTM Adviser](https://gtmadviser.com)
- Want someone to operate it for you? [gtmengine.io](https://gtmengine.io)
