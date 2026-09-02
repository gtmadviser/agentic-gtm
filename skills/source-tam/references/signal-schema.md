# Canonical signal schema

Buying signals from every source land in one shape, are deduplicated structurally, and are staged before anything writes to a CRM. Downstream logic never special-cases a source.

## Design principles

1. Normalize once. Every collector maps to the canonical schema before anything else.
2. Event-driven, not export-driven. Collectors push as signals occur or on a tight schedule.
3. Dedup is structural. A deterministic id per signal makes re-runs idempotent.
4. Stage before the CRM. All collectors write to a `signals` table first. Validation and dedupe happen there. One gated publisher promotes clean signals.
5. Source-agnostic activation. Routing and channel choice read the normalized signal, not the source.

## The record

| Column | Type | Meaning |
|---|---|---|
| `signal_id` | text, primary key | `sha1(signal_type \| entity_key \| natural_key)` |
| `signal_type` | enum | `new_in_role`, `linkedin_engagement`, `funding_round`, `company_news`, `hiring`, `job_post_language`, `tech_on_website`, `pricing_page`, `community_thread`, `alert` |
| `entity_key` | text | the person or company the signal belongs to (LinkedIn slug or normalized domain) |
| `natural_key` | text | what makes this signal unique in its source |
| `occurred_at` | timestamp | when the signal happened; falls back to `ingested_at` |
| `ingested_at` | timestamp | when it was captured |
| `source_system` | text | provider slug |
| `person_ref` | text, nullable | LinkedIn slug or email |
| `company_domain` | text, nullable | normalized domain |
| `title` | text | short human title |
| `summary` | text | one line |
| `evidence_url` | text | always populated |
| `confidence` | numeric 0 to 1 | how sure the collector is |
| `score` | integer 0 to 100 | warmth weight from a per-type rule |
| `payload` | json | raw source object, never lost |
| `published_at` | timestamp, nullable | null until promoted to the CRM |

Plus `signals_seen (signal_id, first_seen_at)` as the idempotency log.

## Natural keys per type

| signal_type | entity_key | natural_key |
|---|---|---|
| linkedin_engagement | actor slug | post id plus engagement type |
| new_in_role | person slug | role start date |
| funding_round | company domain | announced date |
| company_news | company domain | article url |
| hiring | company domain | job id or job url |
| job_post_language | company domain | job id plus matched phrase |
| tech_on_website | company domain | technology plus first-seen date |
| pricing_page | company domain | page hash |
| community_thread | user or company | thread timestamp |
| alert | alert entity | alert id plus fired time |

Insert with `ON CONFLICT (signal_id) DO NOTHING`. A re-run never double-reports.

## Routing

Route by account owner, not contact owner.

| Account state | Action |
|---|---|
| Owned by a rep | task plus notification to the owner with title and url; no enrollment |
| Customer, open opportunity, or an active sales-qualified lead | notify only; never enroll |
| Unassigned and in ICP | eligible for a campaign, subject to suppression sets |
| Out of ICP | store, do not act |

Channel discipline: a warm signal earns a personal channel; a cold-but-fit signal goes to email.

## Scoring

Start with a per-type weight and adjust from outcomes. A comment outranks a reaction, a funding round outranks generic news, a senior title outranks an individual contributor. Recompute weekly from replies and meetings per signal type.

## Build order

1. Staging plus dedupe, no CRM writes. Stand up one collector for the most prepared signal type.
2. Review the model with the team. Agree the CRM object.
3. Turn on the publisher for one signal type.
4. Add sources. Each is mapping work, not new logic.
