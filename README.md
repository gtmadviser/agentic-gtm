# Agentic GTM

> **Public alpha (`0.1.0`)** — ready for inspection and synthetic demos. Connected provider workflows need beta installations and live-test credentials before a `1.0` release.

An open, local-first GTM operating system for technical founders and first GTM hires. Twelve portable Agent Skills use a deterministic `gtm` CLI to read your tools, normalize data into your Supabase project, create reviewable Markdown and JSON artifacts, and require explicit approval before any external write.

```text
Agent Skill -> deterministic gtm CLI -> provider adapter -> your Supabase
                    |
                    +-> reviewable Markdown/JSON artifacts
```

The repository contains no hosted service, telemetry, shared backend, autonomous scheduler, campaign activation command, or MCP server. Your credentials stay in environment variables and your operational data stays in infrastructure you own.

## Quick start

Requires Python 3.11+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv tool install git+https://github.com/gtmadviser/agentic-gtm.git
gtm demo
gtm init my-gtm
cd my-gtm
cp .env.example .env
gtm doctor
```

The package name reserved for a future PyPI release is `gtmadviser-agentic-gtm`.

Use this repository as a Claude Code or Codex plugin, or point any shell-capable agent at `skills/` and the installed `gtm` command. The same canonical skills power both plugin manifests.

## Stable commands

```text
gtm demo
gtm init
gtm doctor
gtm db migrate
gtm sync crm
gtm source accounts|contacts
gtm campaign plan
gtm campaign apply --plan <plan-id>
gtm sync campaigns
gtm review outreach|pipeline|weekly
gtm report slack plan|apply
gtm stack recommend
```

Add global `--json` before the command for stable machine-readable output. `gtm demo` needs no keys. Connected workflows require `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`; only the selected workflow's provider credentials are additionally required.

## Safety contract

- Reads run only inside the scopes declared in `gtm.yaml`.
- External writes first create an immutable action plan with exact targets, a payload summary, an idempotency key, and a SHA-256 hash.
- Apply commands require an explicit plan ID and reject changed, expired, or already-applied plans.
- Sequencer adapters only create paused campaigns. There is no send or activate command.
- Because both sequencer APIs may initially return a new empty shell as running/active, adapters immediately pause the shell before adding any sequence content. They never add contacts. A failed pause aborts the operation and reports the empty shell ID for manual verification.
- Slack bot mode verifies message IDs and supports idempotency; webhook mode is clearly marked unverified.
- Secrets are read from environment variables, never CLI flags.

See [SECURITY.md](SECURITY.md), [OPERATING-CONTRACT.md](OPERATING-CONTRACT.md), and [docs/architecture.md](docs/architecture.md).

## Providers

| Category | Adapters |
|---|---|
| CRM | HubSpot |
| Sourcing | AI Ark, Blitz |
| Sequencing | lemlist, Instantly |
| Collaboration | Slack |

Provider selection is explicit in `gtm.yaml`. Affiliate status never selects or ranks a provider. The versioned optional catalog includes the disclosure shown whenever a tracked link appears.

## Licensing

Python code, JSON schemas, SQL migrations, and tests are MIT licensed. Skills, playbooks, documentation, and written frameworks are CC BY 4.0. See [LICENSES.md](LICENSES.md) for the path-level matrix.

## Services

The free system is fully functional.

- Want this adapted to your company? [Agentic GTM by GTM Adviser](https://gtmadviser.com/agentic-gtm)
- Want someone to operate it for you? [gtmengine.io](https://gtmengine.io)
