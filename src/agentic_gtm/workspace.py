"""Safe workspace initialization shared by the CLI and release generator."""

from __future__ import annotations

import os
import shutil
from importlib.resources import files
from pathlib import Path

DIRECTORIES = (
    "context",
    "context/knowledge",
    "market",
    "strategy",
    "experiments",
    "campaigns",
    "meetings",
    "reports",
    "scripts/git-hooks",
    ".claude/hooks",
    "supabase/migrations",
)

ROUTER = """# Agent router

For LinkedIn post engagers use `linkedin-engager-outreach` for collection, ICP scoring and outreach handoff.

Start every session with the `gtm-kickoff` skill. It runs `gtm doctor` and `gtm --json next`,
explains which stage the workspace is in, and routes to the right skill from `{skills}`.

Read `OPERATING-CONTRACT.md` before acting. Use the `gtm` CLI or the selected skill's documented provider helper.
For `gtm`, add `--json` for stable output; helpers follow their documented output contract. Never bypass plan/apply approval gates.

## Chain (in order)

| Stage | Skill | Done when |
|---|---|---|
| context | onboard-company-brain | `context/company.md` and `context/knowledge/` hold labelled facts |
| icp | refine-icp | `market/icp.md` has an approved working definition |
| crm | inspect-crm | field map confirmed in `gtm.yaml`, opportunities synced |
| experiment | design-gtm-experiment | an approved file under `experiments/` |
| audience | source-tam, research-accounts | accounts or contacts in the store |
| copy | write-outreach | a copy set under `campaigns/` that passed the rubric |
| plan, applied | stage-campaign | plan reviewed, applied with an explicit plan id, provider verified paused |
| review | review-outreach, weekly-gtm-review | a report under `reports/` |

Supporting skills: map-market, audit-deliverability (before any launch), advance-deals,
handover-gtm-engine.

## Hard rules for any agent in this workspace

- Never delete files, records, mailboxes, campaigns, or DNS without asking first.
- Read-only on assets you do not own. Mutating scripts use an explicit allowlist, default deny.
- No test leads in live systems. No unilateral launch. Campaigns stay paused.
- Dry-run first. Every external write goes through `plan` then `apply --plan <id>`.
- Every credit-consuming call shows provider, expected spend, cap and purpose, then waits.
- Secrets live only in `.env`. Contacts and provider IDs live only in the store, never in Git.
- The latest stakeholder decision in `strategy/decisions.md` beats older notes.
- Never resolve conflicting metrics silently. Record the conflict.
"""

PRE_COMMIT = """#!/bin/sh
# Secret guard: blocks commits that ADD a secret value from .env or a
# credential-looking literal. Only added lines are scanned, so a commit that
# removes a secret passes. Bypass for a confirmed false positive only:
#   git commit --no-verify
repo_root=$(git rev-parse --show-toplevel)
added=$(git diff --cached -U0 | grep '^+' | grep -v '^+++' || true)
[ -z "$added" ] && exit 0
fail=0

# 1) Any secret VALUE from .env appearing in added lines.
if [ -f "$repo_root/.env" ]; then
  while IFS= read -r line; do
    case "$line" in ''|'#'*) continue ;; esac
    key=${line%%=*}
    val=${line#*=}
    case "$key" in
      *KEY*|*SECRET*|*TOKEN*|*PW*|*PASSWORD*|*CONNECTION*|*URL*) ;;
      *) continue ;;
    esac
    [ "${#val}" -lt 8 ] && continue
    if printf '%s' "$added" | grep -qF -- "$val"; then
      printf 'BLOCKED: staged changes add the value of %s from .env\\n' "$key" >&2
      fail=1
    fi
  done < "$repo_root/.env"
fi

# 2) Credential-looking literals (KEY = "long-random-string").
if printf '%s' "$added" | grep -qiE "(api[_-]?key|secret|token|passw(or)?d)['\\"]?[[:space:]]*[=:][[:space:]]*['\\"][A-Za-z0-9_.-]{16,}"; then
  printf 'BLOCKED: staged changes add a credential-looking literal.\\n' >&2
  fail=1
fi

# 3) Lead-level PII exports: CSV or XLSX outside allowlisted paths.
if git diff --cached --name-only --diff-filter=A | grep -qiE '\\.(csv|xlsx|xls)$'; then
  printf 'BLOCKED: a spreadsheet is staged. Lead lists belong in the store, not in Git.\\n' >&2
  printf 'If this file is synthetic, commit with --no-verify and say so in the message.\\n' >&2
  fail=1
fi

# 4) gitleaks, when installed.
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks protect --staged --no-banner || fail=1
fi

if [ "$fail" -ne 0 ]; then
  printf 'Unstage the secret or export. Keys belong in .env only.\\n' >&2
fi
exit $fail
"""

STOP_HOOK = """#!/bin/sh
# Stop hook: when Claude finishes a turn with uncommitted or unpushed work,
# print a reminder so decisions and artifacts do not sit in a dirty tree.
repo=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
uncommitted=$(git -C "$repo" status --porcelain 2>/dev/null | grep -c .)
unpushed=$(git -C "$repo" log @{u}..HEAD --oneline 2>/dev/null | grep -c .)
[ "$uncommitted" -eq 0 ] && [ "$unpushed" -eq 0 ] && exit 0
printf '{"systemMessage": "agentic-gtm workspace: %s uncommitted change(s), %s unpushed commit(s). Commit decisions and artifacts before closing the session."}\\n' "$uncommitted" "$unpushed"
"""

CLAUDE_SETTINGS = """{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "sh .claude/hooks/check-git-state.sh",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
"""

FILES = {
    "AGENTS.md": ROUTER.format(skills=".agents/skills/"),
    "CLAUDE.md": ROUTER.format(skills=".claude/skills/"),
    "OPERATING-CONTRACT.md": """# Operating contract

- Git contains context, decisions, experiments, approved aggregates, copy sets, and playbooks. Never raw people or provider data.
- The store contains contacts, accounts, opportunities, activities, provider IDs, campaign metrics, cursors, and approval records. Supabase by default; CSV tables under `.gtm/store/` when no database is configured.
- Separate declared beliefs, observed evidence, hypotheses, and decisions.
- Inspect CRM fields and obtain human field-map confirmation before pulling.
- Define hypothesis, denominator, safeguards, and decision rule before any experiment runs.
- External writes require an immutable plan and an explicit apply command.
- Campaigns remain paused. This repository cannot activate or send campaigns.
- Credentials are environment variables and must never be printed or committed.
- Every credit-consuming operation is approved first.
""",
    "gtm.yaml": """version: 1
company:
  name: ""
providers:
  crm: hubspot
  sourcing: blitz
  sequencer: lemlist
  collaboration: slack
store:
  backend: auto        # auto | supabase | files
  path: .gtm/store     # used by the files backend only
policies:
  external_writes: plan_then_apply
  campaigns_must_remain_paused: true
  require_supabase_for_connected_workflows: false
scopes:
  hubspot:
    objects: [companies, contacts, deals]
field_maps:
  hubspot: {}
artifacts:
  root: .
""",
    ".env.example": """# Store (recommended). Leave empty to use CSV tables under .gtm/store/.
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
# Optional: only required by `gtm db migrate`.
SUPABASE_DB_URL=

# Provider credentials; set only what your selected workflows use.
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
.env.*
!.env.example
.gtm/
.DS_Store
.claude/settings.local.json
*.csv
*.xlsx
*.xls
exports/
data/
""",
    ".claude/settings.json": CLAUDE_SETTINGS,
    ".claude/hooks/check-git-state.sh": STOP_HOOK,
    "scripts/git-hooks/pre-commit": PRE_COMMIT,
    "context/company.md": """# Company context

## Product

## Customers

## Positioning

## Constraints

## Stack and owners

## Voice override
<!-- formal or informal address, forbidden punctuation, spelling variant, who writes step 1 -->

## Missing evidence
""",
    "context/knowledge/README.md": """# Knowledge layer

One insight per file, named `<category>--<slug>.md`, with frontmatter: title, category, status
(emergent | validated | canonical), source, date_extracted, confidence, tags, references, label
(declared | observed | hypothesis | decision). Raw transcripts and exports never live here.
""",
    "market/icp.md": """# Working ICP

## Declared belief

## Observed evidence

## Exclusions and anti-ICP

## Approved working definition
""",
    "strategy/decisions.md": "# Decision log\n\n<!-- YYYY-MM-DD, decision, owner, evidence, supersedes -->\n",
    "experiments/README.md": (
        "# Experiments\n\nOne file per hypothesis. Define hypothesis, denominator, safeguards, "
        "and decision rule before execution. Status: draft, approved, running, complete.\n"
    ),
    "campaigns/README.md": (
        "# Campaigns\n\nCopy sets (`*-copy.md`), campaign drafts (`*.json`), and plan references. "
        "Never raw contacts.\n"
    ),
    "meetings/README.md": "# Meetings\n\nStore redacted preparation and follow-up artifacts.\n",
    "reports/README.md": (
        "# Reports\n\nApproved aggregate reviews from `gtm review outreach|pipeline|weekly`. "
        "Import manual channel counts with `gtm metrics import`.\n"
    ),
}

EXECUTABLE = {".claude/hooks/check-git-state.sh", "scripts/git-hooks/pre-commit"}


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
        if relative in EXECUTABLE:
            os.chmod(destination, 0o755)
        created.append(relative)
    packaged = files("agentic_gtm").joinpath("resources", "skills")
    source = packaged if packaged.is_dir() else Path(__file__).resolve().parents[2] / "skills"

    def copy_tree(origin, destination):
        for item in origin.iterdir():
            if item.name == "__pycache__" or " 2." in item.name or item.name.endswith(".pyc"):
                continue
            path = destination / item.name
            if item.is_dir():
                copy_tree(item, path)
            elif overwrite or not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(item.read_bytes())
                created.append(str(path.relative_to(target)))

    for agent in (".agents", ".claude"):
        copy_tree(source, target / agent / "skills")
    return created


def install_git_hook(target: Path) -> bool:
    """Copy the secret guard into .git/hooks when the workspace is a Git repository."""
    git_dir = target / ".git"
    source = target / "scripts" / "git-hooks" / "pre-commit"
    if not git_dir.is_dir() or not source.exists():
        return False
    hooks = git_dir / "hooks"
    hooks.mkdir(exist_ok=True)
    destination = hooks / "pre-commit"
    if destination.exists():
        return False
    shutil.copy2(source, destination)
    os.chmod(destination, 0o755)
    return True
