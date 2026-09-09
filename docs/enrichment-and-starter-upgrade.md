# Enrichment, evaluation and starter upgrade notes

## Shared paid-call infrastructure

The provider-neutral `PaidCalls` helper supports client/account/endpoint/input
scoping, schema/context versions, finite TTLs and an inspectable run ledger.
It reserves integer micro-USD upper bounds before network I/O. Those numbers
are approved estimates, not claimed invoice charges. Cache hits cost zero new
calls. Inputs retain case, nulls and query semantics; adapters must normalize
only fields whose semantics they understand.

Files stores commit run, cache and ledger state together in one atomically
replaced `enrichment-state.json` under the existing process lock. Supabase uses
normalized tables and one transactional RPC with run-row and cache-key locking.
Different runs cannot reserve the same pending request twice. An uncertain call
retains its reservation and blocks replay until an operator reconciles it.
Neither backend changes another client's records or introduces SQLite.

The first integrated provider path is the five-stage Harvest LinkedIn pipeline.
AI Ark/Blitz and private operational scripts do not automatically acquire these
protections; integrate through `PaidCalls` when migrating each adapter. No live
client data or existing cache was migrated by this source change.

For Supabase, back up the intended client database, inspect `gtm db migrate
--dry-run`, then apply `0004_enrichment.sql` through your normal migration process.
The RPC is callable by `service_role`, not anonymous/authenticated clients; tables
have RLS. Installing or testing the runtime does not run a live migration.

For derived ICP output, include the rubric/persona/prompt/model revisions and
relevant factual inputs in the context hash. Current qualification produces an
input/rubric hash and runs offline; it does not call a model or cache LLM guesses.
CRM/DNC freshness is checked independently before an outreach draft is eligible.

## Checkpoints and starter changes

`gtm checkpoint record` captures a reviewed sample's files, recipe version and
reviewer. `verify` rejects changed content or revisions. A LinkedIn expansion
plan can bind that record. This is local artifact validation, not a deployment
attestation. Existing plan/apply controls still govern remote mutations.

`gtm init` now installs all migrations and records generated-file hashes in
`.generated.json`. Existing files are preserved. `gtm doctor` / `gtm starter check`
show missing or locally changed generated assets; client-authored edits are not
automatically treated as faults.

Generate a candidate starter from the intended runtime version in a separate
empty directory, then run:

```bash
gtm --json starter upgrade-plan /path/to/candidate --workspace /path/to/client
```

The result distinguishes additions, safe updates, conflicts and proposed
removals. It makes no changes. Review the diff, preserve client edits and apply
only the desired assets; never regenerate on top of a customized client repo.
A manifest verifies contents against a local baseline, not upstream authenticity.
Runtime release/tag publication remains a separate release operation.

## Evaluation and design provenance

`evals/linkedin-engager-outreach/` includes fictional company/persona/relationship
cases, held-out expected decisions, invocation cases and a saved-output grader.
The default runner tests deterministic guards. Agent comparisons require saved
outputs, actual attempted actions and model/skill revision metadata; see its
README. No paid model calls are part of CI.

The abstractions were informed by [Rowbound](https://github.com/eliasstravik/rowbound),
[Stockpile](https://github.com/eliasstravik/stockpile),
[gtm-skills](https://github.com/eliasstravik/gtm-skills) and
[skill evaluations](https://github.com/eliasstravik/skills). The implementation is
written for the existing Python/files/Supabase contracts; their code was not vendored.

Validation uses synthetic data and mocked Harvest, plus optional real PostgreSQL
transaction tests against an isolated test socket. Provider billing, CRM field
maps and actual campaign settings still need the client's live verification.
