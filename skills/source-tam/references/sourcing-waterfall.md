# The sourcing waterfall

A list is built in stages. Each stage has one output, one idempotency key, and one exit condition. Stages are resumable checkpoints: a re-run reads rows where its own output is empty and the predecessor's output is present. Nothing is recomputed, nothing is billed twice.

## The seven stages

| # | Stage | Output | Idempotency key | Exit condition |
|---|---|---|---|---|
| S0 | Base and ICP filter | ICP-tagged rows with a stable join key | `company_uid` | row is `in_icp` with a tier |
| S1 | Decision-maker name | `owner_first`, `owner_last`, `name_source`, `name_confidence` | `company_uid` | name present or `exhausted` |
| S2 | Own domain | `domain`, `domain_source`, `domain_confidence` | `company_uid` | domain present or `exhausted` |
| S3 | Email discovery | candidate emails with `email_source` | `(company_uid, email)` | at least one candidate or `exhausted` |
| S4 | Verification | `valid`, `catch_all`, `invalid`, `unknown` | `email` | terminal state per candidate |
| S5 | Dedupe and legal gate | one sendable contact per domain, `consent_basis`, `address_type` | `domain` | one winner per domain, legally tiered |
| S6 | Load | rows in the sequencer and in the store | `(contact_id, campaign_id)` | loaded, no same-domain duplicate |

`company_uid` is a hash of country, register id, and normalized name. Two sources agreeing on a name raise `name_confidence`. S1 and S2 run in parallel; S3 needs both.

## Ordering inside a stage

Cheapest and most accurate first. Flat-rate or already-paid sources before per-credit providers. Pattern guessing plus verification before any paid finder. Expensive providers only on the residual.

A typical S3 order:

1. A flat-rate provider you already pay for, tried on every row that has a domain.
2. Pattern candidates (`first.last`, `firstlast`, `f.last`, `flast`, `first`, `last` at the domain), sent straight to verification.
3. A per-credit finder that bills only on hit.
4. A per-credit finder that bills per search.
5. Batch providers with asynchronous results, run on the misses of everything above.

Stop at the first verified hit. Never attach an email whose name does not match the decision maker you extracted. Keep one best candidate per company, not four.

## Verification tiers

Verification is the binding constraint in most pipelines because accurate verifiers are slow. Split the load:

| Candidate origin | Verifier |
|---|---|
| Vendor-supplied, already marked verified | cheap bulk verifier, sub-second, spot-check 5% with the accurate verifier |
| Pattern-guessed | accurate verifier, slow, one candidate at a time |
| Role inbox (`info@`, `office@`) | MX and syntax check only, then generic copy |

Before any paid verification run: MX check, syntax check, and a per-domain catch-all flag. A catch-all domain is not bounce-tested; route it to the role inbox with generic copy.

Cache verification by email with a time to live: 60 to 90 days for `valid`, 30 days for `catch_all`, permanent for `invalid`.

## Provenance fields on every contact

```
email_source      provider slug or "pattern"
verify_state      valid | catch_all | invalid | unknown
verify_source     provider slug
verified_at       ISO timestamp
name_source       register | provider slug | website
consent_basis     opt_out | legitimate_interest | opt_in | none
address_type      named | role
sendable          true only when verify_state = valid and consent_basis != none
```

## Legal gate (S5)

Consent regimes differ by country. Before sourcing a market, classify it as opt-out (a lawful basis exists for business addresses without prior consent) or opt-in (prior consent required), and record the basis in `market/tam.md`. Named business addresses are personal data in most jurisdictions; role inboxes carry lower risk. Where the basis is unclear, default to role inboxes and get counsel sign-off before named sends. Register-sourced contact data often carries reuse restrictions; read the licence.

## Throughput rules of thumb

- Verification cache keyed on email is the single biggest lever. Reuse it across campaigns.
- Never call a domain-dependent finder on rows without a domain.
- Cap concurrent requests at the provider's documented ceiling and let overflow fall through to the next provider instead of queueing.
- A per-stage funnel with counts and cost per 1,000 usable contacts shows which vertical is worth the spend. Publish it in `reports/sourcing-<date>.md`.

## The supply arithmetic

At 20 sends per mailbox per day and a 90-day re-approach window, monthly net-new demand roughly equals monthly send volume. Size the sourcing pipeline to that number before adding mailboxes. More mailboxes without more usable supply produce re-sends to the same domains.
