# Provider references

One page per provider the `gtm` CLI or the skills touch. Each page records the auth pattern, the endpoints we rely on, the pagination idiom, and the gotchas that cost real time. Gotchas carry an observed date. Vendors change their APIs, so treat every entry as a hypothesis to re-verify, not a fact.

| Provider | Role in the engine | Page |
|---|---|---|
| Instantly | Email sequencer, mailbox fleet host, inbox placement tests | [instantly.md](instantly.md) |
| lemlist | Multichannel sequencer (LinkedIn + email), lemwarm warm-up | [lemlist.md](lemlist.md) |
| HubSpot | CRM of record: companies, contacts, deals, pipelines | [hubspot.md](hubspot.md) |
| Supabase / PostgREST | Operational store for contacts, plans, metrics | [supabase-postgrest.md](supabase-postgrest.md) |
| Mailbox and domain providers | Zapmail, Mission Inbox, Dynadot, Namecheap, warm-up tools | [mailbox-and-domain-providers.md](mailbox-and-domain-providers.md) |
| Sourcing, enrichment, verification | AI Ark, Blitz, verification providers, Clay | [sourcing-enrichment-verification.md](sourcing-enrichment-verification.md) |
| Slack | Approval-gated report posting | [slack.md](slack.md) |

See also [data-and-privacy.md](../data-and-privacy.md) for what goes where and what never enters Git.

## Shared rules

These apply to every provider, every script, and every skill.

1. **Verify before coding.** Fetch the vendor's current docs page before writing a new call. Endpoint shapes drift. A gotcha listed here may already be fixed, or a new one may exist.
2. **Credentials come from the environment only.** Read `.env` through the environment. Never pass a key as a CLI argument, never print one, never commit one. Keys in argv are readable by every local process.
3. **Dry-run first.** Every script that writes to a provider takes `--dry-run` and defaults to it where practical. Print the exact targets and payload summary before the real run.
4. **Idempotent by default.** Re-running a script must not duplicate records. Upsert on a stable key, keep a resumable state file, and treat "already exists" responses as success, not failure.
5. **Approval before external writes.** The CLI creates an immutable plan first and applies only with an explicit plan ID. Scripts outside the CLI follow the same shape: print plan, ask, then act.
6. **Campaigns stay paused.** No adapter, script, or skill in this repository activates or sends. Activation is a human action in the vendor UI.
7. **Rate limits are real.** Sleep between calls, chunk batch endpoints, and retry only on 429 and 5xx with backoff. A 4xx is a bug in the request, not a transient error.
8. **Read-only on other people's assets.** Campaigns, mailboxes, and CRM records owned by teammates or a client's reps are read-only unless that person authorises the change. Mutating scripts carry an explicit allowlist of IDs they own and default to deny.
9. **Credit-consuming operations show their cost first.** Before any enrichment, verification, or export that burns credits, print the plan, the remaining balance, and the cap, and get approval.
10. **Log the observed date on every gotcha you add.** Future readers need to know how stale a workaround is.

## How to add a provider page

Copy the anatomy below, fill it from the vendor docs plus what you observed, and keep client context out.

```
# <Provider> reference
Role in the engine
Auth (env var, header)
Base URL
Rate limits and retry behaviour
Pagination
Key endpoints we use (table: purpose, method, path, notes)
Gotchas (table: symptom, cause, fix, observed)
What the gtm CLI does with it
Verify-before-coding rule
```
