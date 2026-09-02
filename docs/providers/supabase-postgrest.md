# Supabase and PostgREST reference

Public docs: https://supabase.com/docs and https://postgrest.org/en/stable/

## Role in the engine

Supabase is the default operational store: accounts, contacts, opportunities, activities, campaign records, metric snapshots, action plans, and apply results. The project belongs to the company running the engine. Nothing in this repository depends on a hosted service of ours.

State lives in tables. Process lives in Markdown. If you find yourself grepping Markdown to count something, add a table or a view instead.

The CLI also runs without Supabase: when the two env vars are absent and the policy allows it, records go to CSV and JSON files under `.gtm/store/`. Same contracts, same commands, no database. See [data-and-privacy.md](../data-and-privacy.md).

## Auth

| Item | Value |
|---|---|
| Env vars | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` |
| Headers | `apikey: <key>` and `Authorization: Bearer <key>` on every call |
| Base URL | `<SUPABASE_URL>/rest/v1` |
| Migrations only | `SUPABASE_DB_URL` for `gtm db migrate` |

PostgREST needs the `apikey` header even when the bearer token is the service-role JWT. The service-role key bypasses row level security, so it stays on the operator's machine and in server-side jobs. Never ship it to a browser or a dashboard; use the anon key with RLS policies there.

## Rate limits and retries

No hard published limit on the REST layer, but the database has a statement timeout. Long scans, sorts on unindexed columns, and count-exact requests over millions of rows hit it. Retry 5xx once with backoff; if a slice keeps failing, halve the page size.

## Pagination

| Rule | Detail |
|---|---|
| Hard cap | responses return at most 1000 rows regardless of `limit` |
| Walk with Range | `Range-Unit: items` and `Range: 0-999`, then `1000-1999`, and so on |
| End of set | HTTP 416 means past the end; treat it as the loop terminator |
| Size first | `Prefer: count=exact` with `Range: 0-0` returns the count cheaply |
| Ordering | never `order=` on an unindexed column over a large filtered set; it trips the statement timeout (SQLSTATE 57014) |
| Last slice 500 | the final partial page can time out on planner edge cases; retry, then drop to page size 200 |

Prefer exact-match filters (`col=eq.value`) over `like` patterns; they use the index directly.

## Key operations

| Purpose | Method | Path | Notes |
|---|---|---|---|
| Upsert | POST | `/{table}?on_conflict=provider,provider_id` | `Prefer: resolution=merge-duplicates,return=representation` |
| Insert ignore | POST | `/{table}?on_conflict=plan_id` | `Prefer: resolution=ignore-duplicates,return=minimal` |
| Select | GET | `/{table}?select=*&id=eq.<uuid>&limit=1` | filters are query params |
| Patch | PATCH | `/{table}?id=eq.<uuid>&status=eq.pending` | conditional update by filter |
| Count | GET | `/{table}?select=id` with `Prefer: count=exact` and `Range: 0-0` | cheap sizing |

The upsert key for every provider record is `(provider, provider_id)`. Action plans are unique on `idempotency_key`. Apply results are unique on `plan_id`. These constraints are what make re-runs safe.

## Schema

`supabase/migrations/0001_initial.sql` creates the tables and enables row level security on every one. The migration is idempotent (`create table if not exists`). Run it with `gtm db migrate` or paste it into the SQL editor. Later migrations are numbered and applied in order.

Add columns and views when you need to chart, alert on, join, or compare week over week. Keep prose, runbooks, and drafts as files.

## Gotchas

| Symptom | Cause | Fix | Observed |
|---|---|---|---|
| 401 with a valid service key | `apikey` header missing | send both headers | 2026-04 |
| Only 1000 rows returned | PostgREST cap | Range pagination | 2026-04 |
| 500 "canceling statement due to statement timeout" | sort on an unindexed column over a large set | drop the order clause, dedupe client-side | 2026-04 |
| Silent duplicates | upsert without `on_conflict` | always pass the conflict target | 2026-05 |
| Dashboard sees nothing | RLS on, anon key, no policy | add read policies for the views the dashboard needs | 2026-05 |
| Counts drift between markdown and tables | someone wrote state to a file | the table wins; refresh the file | 2026-06 |

## What the gtm CLI does with it

- `gtm doctor` reports whether Supabase is configured and which store is active.
- Every connected command upserts through the REST layer with the conflict keys above.
- `gtm campaign plan` and `gtm report slack plan` store immutable plans; `apply` reads the plan back, verifies its hash, and records the result so a second apply is a no-op.

## Verify before coding

Check the PostgREST version notes for header changes before relying on a `Prefer` value, and test any new filter on a count-only request before pulling rows.
