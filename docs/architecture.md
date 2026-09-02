# Architecture

```text
Agent Skill (skills/<name>/SKILL.md + references/)
      |
      v
deterministic `gtm` CLI  ->  provider adapter  ->  provider API
      |
      +-> store: Supabase (default) or CSV/JSON under .gtm/store/
      +-> reviewable artifacts in Git: context/, market/, experiments/, campaigns/, reports/
```

`skills/` contains portable Agent Skills. Each one is a procedure with hard rules, a checklist, an output contract and reference files. Skills select a workflow, load repository context, call the `gtm` CLI, interpret structured results, and update durable Markdown or JSON artifacts. `gtm-kickoff` is the entry point; `gtm next` tells it where the workspace stands.

`src/agentic_gtm/` owns deterministic behavior: schemas, provider authentication, retries, pagination, normalization, deduplication, idempotency, approval hashes, metric maths, the gate machine, and safe apply operations. Adapters expose capability-oriented `inspect`, `pull`, `search`, `plan`, `apply`, and `pull_campaign_metrics` methods.

The store is startup-owned. `store.backend: auto` uses Supabase when `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are present and falls back to CSV tables and JSON plans under `.gtm/store/` otherwise. Both backends implement the same `Store` protocol (`src/agentic_gtm/database/base.py`), so every command behaves the same way. Supabase tables come from `supabase/migrations`; the files store needs nothing.

Git holds context, decisions, experiments, copy sets, approved aggregates and playbooks. The store holds contacts, accounts, opportunities, campaign metrics, provider IDs, plans and apply records. `.gtm/` is ignored.

The generated starter is a release artifact. `scripts/generate_starter.py` copies canonical skills into `.agents/skills/` and `.claude/skills/`, writes a pinned runtime version, and generates the company workspace. CI compares its checksums to prevent drift. Provider behaviour and gotchas are documented under `docs/providers/`.
