# Data and privacy

This page says what lives where, what never enters Git, how the store works with and without Supabase, and what an EU outbound operator has to keep in mind. It is operational guidance, not legal advice.

## Three places, three kinds of data

| Place | Holds | Never holds |
|---|---|---|
| Git (the company workspace) | company context, decisions, approved ICP, experiment definitions, campaign drafts without recipients, approved aggregate reports, playbooks, plan and result references | contacts, raw exports, provider IDs of people, credentials, mailbox addresses, per-person research |
| The store (Supabase by default, files as fallback) | accounts, contacts, opportunities, activities, campaign records, metric snapshots, sync cursors, action plans, apply results, provenance | credentials |
| Nowhere durable | credentials (environment only), provider response recordings, scratch pulls | |

The rule of thumb: if a row is about a person, it belongs in the store. If a paragraph is about how you decide, it belongs in Git.

## The store

**Supabase (default).** Set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`, run `gtm db migrate` or apply `supabase/migrations/0001_initial.sql`, and every connected command reads and writes there. The project is yours; nothing here phones home. See [providers/supabase-postgrest.md](providers/supabase-postgrest.md).

**Files (fallback).** When the Supabase variables are absent and `policies.require_supabase_for_connected_workflows` is `false` in `gtm.yaml`, the same commands write CSV and JSON files under `.gtm/store/`. Record tables become one CSV per table with nested fields JSON-encoded in the cell. Action plans and apply results become one JSON file each. The same contracts, conflict keys, and approval gates apply. `gtm doctor` prints which store is active, and every JSON result carries a `store` field.

Use files for a first week, a demo, a tiny motion, or when the team lives in spreadsheets anyway. Move to Supabase when more than one person needs the data, when you want views and dashboards, or when the CSVs pass a few thousand rows.

`.gtm/` is gitignored. It stays that way. Copying a CSV from `.gtm/store/` into the repository is a data leak, not a shortcut.

## PII minimisation

- Pull only the properties a workflow needs. The HubSpot pull reads a fixed short list of standard properties and nothing else until the field map says otherwise.
- Keep person-level research in the store with a source URL and observed date. Write only approved account briefs or aggregate rules to Git.
- Do not infer sensitive traits. Fit and urgency scoring uses company and role signals only.
- Redact before you paste. The CLI redacts keys and bearer tokens in every output; you still own what goes into chat, screenshots, and tickets.
- Reply bodies are personal data. Store the classification and a short reason, not the full text, unless you have a reason to keep it.

## Retention and deletion

- Never delete a record that replied or was marked interested without a backup and an explicit approval. Those rows are your attribution evidence.
- Before bulk deletion in a sequencer, back the leads up to your store. Sequencer APIs cap deletes and the UI is faster for thousands of rows; either way, back up first.
- Honour deletion requests within the statutory window. Suppress the address and domain everywhere, then delete or anonymise the store rows.
- Unsubscribes and hostile replies go on a suppression list immediately, in the sequencer and in the store. A customer's domain goes on the suppression list the day the deal closes.
- Keep an append-only deletion log with date, reason, and count.

## EU outbound awareness

Not legal advice. Talk to counsel for your jurisdiction and your data.

- **GDPR.** Cold B2B email to a business contact usually rests on legitimate interest (Article 6(1)(f)). Document the balancing test, keep the data minimal, provide a clear opt-out in every message, and honour access and deletion requests.
- **Germany, UWG section 7.** Unsolicited commercial email without prior consent is treated as an unreasonable nuisance and can be pursued by competitors and associations, not only by the recipient. Some verticals are known to litigate. Decide per vertical, with counsel, whether email, letter, phone, or LinkedIn is the channel. Do not let a sequencer decide that for you.
- **Local sending identity.** Send from a local persona, a local phone number in the signature, and a local business address. Recipients reply to people, not to fleets.
- **Language.** Translating copy does not produce local results. Write native or do not ship.
- **Opt-out mechanics.** A working reply-to-stop path in every step. Silence is not consent to continue; keep sequences short.
- **Suppression lists.** Customers, open opportunities, competitors, unsubscribes, bounces, and prior recipients within the re-approach window. Every campaign build checks all of them.

## Secrets

- `.env` only, gitignored from the first commit. Scripts read the environment.
- `gtm init` writes a pre-commit hook under `scripts/git-hooks/` that blocks a commit when a staged line contains a value from `.env` or a credential-looking literal. Install it with `cp scripts/git-hooks/pre-commit .git/hooks/`. It scans added lines only, so a commit that removes a secret still passes.
- `scripts/scan_public_release.py` scans the tree and, with `--history`, every commit for private keys, tokens, non-empty secret assignments, high-entropy fixture values, and real-looking domains in fixtures. Pass `--deny-file` with a private, gitignored list of terms that must never appear in a public release.
- Rotate any key that was ever printed, pasted, or committed, even if the commit was later removed. Transferred repositories carry unreachable blobs with them.

## Fixtures and examples

Every name, domain, person, metric, and event in `fixtures/` is fictional. Contributions with real customer names, campaign copy, provider response recordings, or contact data are rejected. Generic thresholds and rules of thumb are fine; identifiable client results are not.
