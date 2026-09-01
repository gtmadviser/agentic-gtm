"""Safe workspace initialization shared by the CLI and release generator."""

from __future__ import annotations

from pathlib import Path

DIRECTORIES = (
    "context",
    "market",
    "strategy",
    "experiments",
    "campaigns",
    "meetings",
    "reports",
    "supabase/migrations",
)

FILES = {
    "AGENTS.md": """# Agent router

Read `OPERATING-CONTRACT.md`, then select the relevant skill from `.agents/skills/`. Use the `gtm` CLI for provider operations and stable JSON. Never bypass plan/apply approval gates.
""",
    "CLAUDE.md": """# Agent router

Read `OPERATING-CONTRACT.md`, then select the relevant skill from `.claude/skills/`. Use the `gtm` CLI for provider operations and stable JSON. Never bypass plan/apply approval gates.
""",
    "OPERATING-CONTRACT.md": """# Operating contract

- Git contains context, decisions, experiments, approved aggregates, and playbooks—not raw people or provider data.
- Supabase contains contacts, accounts, opportunities, activities, provider IDs, cursors, and approval records.
- Separate declared beliefs, observed evidence, hypotheses, and decisions.
- Inspect CRM fields and obtain human field-map confirmation before pulling.
- External writes require an immutable plan and an explicit apply command.
- Campaigns remain paused. This repository cannot activate or send campaigns.
- Credentials are environment variables and must never be printed or committed.
""",
    "gtm.yaml": """version: 1
company:
  name: ""
providers:
  crm: hubspot
  sourcing: blitz
  sequencer: lemlist
  collaboration: slack
policies:
  external_writes: plan_then_apply
  campaigns_must_remain_paused: true
  require_supabase_for_connected_workflows: true
scopes:
  hubspot:
    objects: [companies, contacts, deals]
field_maps:
  hubspot: {}
artifacts:
  root: .
""",
    ".env.example": """SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_DB_URL=
HUBSPOT_ACCESS_TOKEN=
AI_ARK_API_KEY=
BLITZAPI_API_KEY=
LEMLIST_API_KEY=
INSTANTLY_API_KEY=
SLACK_BOT_TOKEN=
SLACK_CHANNEL_ID=
SLACK_WEBHOOK_URL=
""",
    ".gitignore": """.env
.gtm/
.DS_Store
""",
    "context/company.md": """# Company context

## Product

## Customers

## Positioning

## Constraints

## Stack and owners

## Missing evidence
""",
    "market/icp.md": """# Working ICP

## Declared belief

## Observed evidence

## Exclusions and anti-ICP

## Approved working definition
""",
    "strategy/decisions.md": "# Decision log\n",
    "experiments/README.md": "# Experiments\n\nDefine hypothesis, denominator, safeguards, and decision rule before execution.\n",
    "campaigns/README.md": "# Campaigns\n\nStore reviewable drafts and plan references here; never raw contacts.\n",
    "meetings/README.md": "# Meetings\n\nStore redacted preparation and follow-up artifacts.\n",
    "reports/README.md": "# Reports\n\nStore approved aggregate reviews.\n",
}


def initialize_workspace(target: Path, *, overwrite: bool = False) -> list[str]:
    target.mkdir(parents=True, exist_ok=True)
    for directory in DIRECTORIES:
        (target / directory).mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    for relative, content in FILES.items():
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and not overwrite:
            continue
        destination.write_text(content, encoding="utf-8")
        created.append(relative)
    return created
