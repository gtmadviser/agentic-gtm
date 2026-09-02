# HubSpot reference

Public docs: https://developers.hubspot.com/docs/api/crm/understanding-the-crm

## Role in the engine

HubSpot is the CRM of record. Won, lost, and open deals are the evidence base for the ICP. Contact and company records carry lead state across every channel. The engine reads HubSpot before any analysis and writes to it only through explicit plan and apply steps, never during a sync.

## Auth

| Item | Value |
|---|---|
| Env var | `HUBSPOT_ACCESS_TOKEN` (private app token) |
| Header | `Authorization: Bearer <token>` |
| Base URL | `https://api.hubapi.com` |

Create a private app with the smallest scope set that works. For the read-only CRM pull: `crm.objects.companies.read`, `crm.objects.contacts.read`, `crm.objects.deals.read`, `crm.schemas.companies.read`, `crm.schemas.contacts.read`, `crm.schemas.deals.read`. Add `crm.objects.owners.read` if you route by owner; without it owner lookups return 403 (observed 2026-06, verify against current docs). Write scopes only when a plan and apply workflow needs them.

## Rate limits and retries

Private apps get roughly 110 requests per 10 seconds; search endpoints are throttled harder, around 4 per second. Batch endpoints take at most 100 records per call. Retry 429 and 5xx with exponential backoff and honour `Retry-After`.

## Pagination

Search and list responses carry `paging.next.after`. Pass it back as `after`. Page size max 100. Search results lag writes by a few seconds, so never create-then-search; keep IDs from the create response.

## Key endpoints

| Purpose | Method | Path | Notes |
|---|---|---|---|
| Property schema | GET | `/crm/v3/properties/{objectType}` | run before any pull; this is the field-map step |
| Deal pipelines | GET | `/crm/v3/pipelines/deals` | stage IDs and labels, won and lost flags |
| Search objects | POST | `/crm/v3/objects/{objectType}/search` | filters, sorts, `properties`, `limit`, `after` |
| List objects | GET | `/crm/v3/objects/{objectType}` | bounded sample for access checks |
| Batch read | POST | `/crm/v3/objects/{objectType}/batch/read` | up to 100 IDs |
| Batch create or update | POST | `/crm/v3/objects/{objectType}/batch/create` or `/update` | up to 100; one bad record fails the batch |
| Associations | PUT | `/crm/v4/objects/contacts/{id}/associations/default/companies/{companyId}` | contact to company |
| List memberships | GET | `/crm/v3/lists/{listId}/memberships?limit=250` | suppression pulls |

### Field-map confirmation

Custom properties have meanings only the operator knows. The CLI inspects properties and pipelines, writes the inspection to `.gtm/`, and stops. A human confirms the semantic mapping in `gtm.yaml` under `field_maps.hubspot` before any pull runs. Do not guess what `custom_score_v2` means, and do not collapse won, lost, and open stages into one status.

Standard property names used by the default pull: companies `name`, `domain`, `industry`, `numberofemployees`; contacts `firstname`, `lastname`, `jobtitle`, `email`, `hs_linkedin_url`; deals `dealname`, `dealstage`, `amount`, `closedate`, `hs_is_closed_won`.

## Gotchas

| Symptom | Cause | Fix | Observed |
|---|---|---|---|
| 403 on owner lookups | missing owners scope | add `crm.objects.owners.read` | 2026-06 |
| Search returns nothing right after create | index lag | use the ID from the create response | 2026-05 |
| Whole batch 400s | one unknown dropdown value | create property options first, validate locally | 2026-05 |
| Duplicate contacts | matched on name | match contacts on email, companies on `domain`, email-less leads on `hs_linkedin_url` | 2026-05 |
| Numbers rejected | typed as JSON numbers | send property values as strings; the API coerces | 2026-05 |
| Lost deals counted as open | stage label heuristics | read pipeline stage metadata for closed-won and closed-lost flags | 2026-04 |
| Historical analysis uses today's enrichment | enrichment values are current, not deal-time | label them as current attributes, never as deal-time evidence | 2026-06 |

## What the gtm CLI does with it

- `gtm sync crm` inspects properties and pipelines on first run and exits with status 2 until `field_maps.hubspot` is confirmed. On later runs it pulls companies, contacts, and deals and upserts them into your store on `(provider, provider_id)`.
- `gtm review pipeline` reports won, lost, and open separately from the store.
- The CLI ships no HubSpot write path. Writes need a plan and apply workflow that does not exist yet by design.

## Verify before coding

Confirm scopes on the private app page and the property names on the schema endpoint before adding a property to a pull. Fetch the docs page for any endpoint you have not used in the last month.
