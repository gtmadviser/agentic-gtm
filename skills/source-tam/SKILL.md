---
name: source-tam
description: Size the total addressable market, turn the approved ICP into provider queries, and source normalized accounts and contacts through the configured AI Ark or Blitz adapter with provenance, suppression, and verification. Use after the ICP and exclusions are approved; do not use for speculative scraping, unplanned credit spend, or campaign enrollment.
---

# Source TAM

> Sourcing sits between ICP and Personalize in the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate). Its job is to turn one approved ICP slice into a list of accounts and contacts that is small enough to review, clean enough to send to, and traceable enough to learn from. It sizes the universe first, probes before it scales, spends credits only with an approved plan, and never treats a raw export as a sendable list.

## When to use / when not to

Use when:
- `market/icp.md` has an approved working definition and explicit exclusions.
- An experiment in `experiments/` names the audience this list serves.
- You need to size a market, build a first probe list, or expand an approved list.

Do not use when:
- The ICP is still a declared belief with no exclusions. Run `refine-icp` first.
- The goal is enrichment of an existing list. That is a sub-step here, not a standalone job.
- Someone wants contacts pushed into a sequencer. Sourcing never authorises outreach. That is `stage-campaign`.

## Inputs

| Input | Where | What you take from it |
|---|---|---|
| Approved ICP and anti-ICP | `market/icp.md` | firmographic bounds, persona ladder, disqualifiers |
| Active experiment | `experiments/*.json` | audience definition, sample size, safeguards |
| Provider selection | `gtm.yaml` `providers.sourcing` | `ai_ark` or `blitz` |
| Readiness | `gtm --json doctor` | credentials, store backend |
| Existing records | store tables `accounts`, `contacts`, `opportunities` | what already exists, what is owned, what is suppressed |
| Suppressions | `.gtm/suppressions/*.csv` | customers, open deals, competitors, opt-outs, bounced, burned domains |
| Prior queries | `.gtm/queries/*.json` | what was tried, what it returned |

## Procedure

1. **Confirm readiness.** Run `gtm --json doctor`. Confirm the sourcing provider is ready and which store is active. If the store is `files`, results land in `.gtm/store/accounts.csv` and `.gtm/store/contacts.csv`.
2. **Size the universe before touching a provider.** Write `market/tam.md` with three layers: the universe (geography, industry codes, size band, legal form), the slice this experiment targets, and the probe. Attach a count to each layer and label it `measured` (from a register, a provider count endpoint, or a prior export) or `estimate`. Do not put an estimate into a budget.
3. **Translate the ICP into a query file.** Write `.gtm/queries/<slug>-v1.json`. One version per filter change. Keep the anti-ICP as explicit excludes, never as a mental note. See `references/query-json-examples.md`.
4. **Show the credit plan and wait.** Before any call that consumes credits, present provider, remaining credits, expected spend, cap, and purpose. Proceed only after explicit approval. See `references/credit-approval.md`.
5. **Probe with 25.** Run `gtm --json source accounts --query .gtm/queries/<slug>-v1.json --limit 25`. Review every row against the ICP. Record precision as fit rows out of 25. If precision is below 20 of 25, change one filter, bump the version, and probe again.
6. **Expand in steps.** 100, then 500, then the full slice. Re-check precision on a random 25 at each step. When a query returns nothing, loosen exactly one filter, never the anti-ICP or a suppression rule.
7. **Source contacts for approved accounts only.** Run `gtm --json source contacts --query .gtm/queries/<slug>-people-v1.json --limit N` with the persona ladder from the ICP as title includes and excludes. One decision maker per domain per campaign.
8. **Fill missing emails through the waterfall.** Cheapest and most accurate provider first, verify every found address, stop at the first verified hit, store provenance per record. See `references/sourcing-waterfall.md`.
9. **Apply the three mandatory filters and the suppression sets.** Sender side, recipient side, cross-campaign dedupe. Log counts before and after. An unavailable or empty exclusion source is a failure, not a pass. See `references/mandatory-filters.md` and `references/suppression-and-blocklists.md`.
10. **Write the data-quality report.** `reports/sourcing-<YYYY-MM-DD>.md` with query version, provider, observed date, result count, duplicate count, precision on probe, verification pass rate, and unresolved risks. Aggregates only. No names or emails in Git.

## Hard rules

1. Probe limit is 25. No first pull larger than 25 rows on a new query version.
2. Expand only when probe precision is at least 20 of 25.
3. One filter change per query version. Versions are never overwritten.
4. No credit-consuming operation without a shown and approved plan.
5. An email is `sendable` only after a verification result of `valid` stored with provider and timestamp. `catch_all` and `unknown` are not sendable to named people.
6. One decision maker per company domain per campaign.
7. Re-approach window is at least 60 days since the last message to the same domain. 90 days is the default.
8. Contacts that replied or were labelled interested are never deleted from any system. Back up the store before any bulk deletion elsewhere.
9. Customers, open opportunities, competitors, opt-outs, and complaint cases are excluded before a list is called usable.
10. Person-level records live in the store. Git gets `market/tam.md`, query files are local under `.gtm/`, reports carry aggregates only.
11. Sourcing never authorises outreach. Nothing here creates a campaign or enrolls a contact.
12. Affiliate status never selects a provider. `providers.sourcing` in `gtm.yaml` is the only selector.

## Checklist

- [ ] `gtm --json doctor` shows the sourcing provider ready and names the store backend
- [ ] `market/tam.md` has universe, slice, probe, each with a labelled count
- [ ] Query file exists at `.gtm/queries/<slug>-v<N>.json` and encodes every anti-ICP exclusion
- [ ] Credit plan shown and approved before the first paid call
- [ ] Probe of 25 reviewed row by row; precision recorded
- [ ] Expansion happened in steps with a re-check at each step
- [ ] Every email carries `email_source`, `verify_state`, `verify_source`, `verified_at`
- [ ] Sender-side, recipient-side, and cross-campaign filters applied with before and after counts
- [ ] Suppression sets applied: customers, open deals, competitors, opt-outs, complaints, own domains
- [ ] `reports/sourcing-<date>.md` written with aggregates only
- [ ] No names, emails, phone numbers, or provider IDs in any Git-tracked file

## Output contract

| Artifact | Location | Tracked in Git | Content |
|---|---|---|---|
| TAM sizing | `market/tam.md` | yes | universe, slice, probe, labelled counts, sources |
| Query files | `.gtm/queries/<slug>-v<N>.json` | no | provider filters, one version per change |
| Accounts | store table `accounts` | no | normalized records with `provider`, `provider_id`, `observed_at`, `attributes.provenance` |
| Contacts | store table `contacts` | no | normalized records plus verification fields in `attributes` |
| Suppressions | `.gtm/suppressions/*.csv` | no | one file per set, one value per line, with `added_at` and `reason` |
| Data-quality report | `reports/sourcing-<date>.md` | yes | aggregates, precision, pass rates, risks |

Status vocabulary for a list: `raw` (provider output), `filtered` (mandatory filters applied), `verified` (every email verified), `usable` (suppressions applied and reviewed). Only `usable` lists move to `stage-campaign`.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Query returns 0 rows | Industry or title taxonomy mismatch, or a language-specific keyword | Loosen one filter, check the provider's exact taxonomy names, retry the probe |
| Probe precision below 80% | ICP proxy criteria with no causal link, or a too-broad keyword | Tighten one filter, re-read the anti-ICP, do not expand |
| Many rows with the same domain | Provider returns people first | Dedupe on normalized domain, keep the most senior title |
| Verification pass rate below 70% | Pattern-guessed emails or stale vendor data | Move pattern guesses to the accurate verifier, drop the vendor for this slice |
| Bounce rate above 2% on the first send | Bounced-recipient filter read a nullable status column instead of send events | Rebuild the bounced ledger from ground-truth events, re-filter, pause |
| Dead senders reappear in a build | Sequencer reports cancelled mailboxes as active | Use the provider inventory as the allowlist, never the sequencer flag alone |
| Duplicate contacts across campaigns | No domain ledger | Add `(domain, campaign, loaded_at)` to `.gtm/suppressions/domain-ledger.csv` and check the re-approach window |
| Credit balance drops unexpectedly | A provider bills per search or per technology found, not per hit | Read the billing model into the credit plan, cap the run, resume from cache |

## References

- `references/sourcing-waterfall.md` - the seven-stage machine, idempotency keys, verification tiers
- `references/signal-schema.md` - canonical signal record, deterministic ids, routing
- `references/mandatory-filters.md` - the three filters every build must pass
- `references/suppression-and-blocklists.md` - suppression sets and the CRM-to-blocklist rule
- `references/credit-approval.md` - the approval template for paid operations
- `references/query-json-examples.md` - fictional query files for both adapters
- `references/vendor-evaluation.md` - how to compare data vendors before buying

Licensed CC BY 4.0 by GTM Adviser.
