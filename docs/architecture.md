# Architecture

`skills/` contains portable Agent Skills. They select a workflow, load relevant repository context, call the stable `gtm` CLI, interpret structured results, and update durable Markdown or JSON artifacts.

`src/agentic_gtm/` owns deterministic behavior: schemas, provider authentication, retries, pagination, normalization, deduplication, idempotency, approval hashes, and safe apply operations. Adapters expose capability-oriented `inspect`, `pull`, `search`, `plan`, and `apply` methods.

Supabase is startup-owned. The REST adapter writes normalized operational records and action plans into the tables created by `supabase/migrations`. No runtime path depends on gtmadviser.com.

The generated starter is a release artifact. `scripts/generate_starter.py` copies canonical skills into `.agents/skills/` and `.claude/skills/`, writes a pinned runtime version, and generates the company workspace. CI compares its checksums to prevent drift.
