# Instantly reference

Public docs: https://developer.instantly.ai/ (v2). The v1 API still exists for a few operations and behaves differently.

## Role in the engine

Instantly is the email sequencer and the host of the sending fleet. It stores campaigns, sequences, leads, sending accounts, warm-up state, and inbox placement tests. The engine treats it as the execution layer. Copy, audience, and metrics of record live in your own store.

## Auth

| Item | Value |
|---|---|
| Env var | `INSTANTLY_API_KEY` |
| Header | `Authorization: Bearer <key>` |
| Also send | `Content-Type: application/json` and a real `User-Agent` string |
| Base URL | `https://api.instantly.ai/api/v2` |

Use the key exactly as issued. Do not decode or re-encode it. Do not send workspace override headers; they cause 401 (observed 2026-05, verify against current docs).

## Rate limits and retries

Rapid sequential calls return 429. Sleep 120 to 150 ms between requests and chunk batch operations in groups of about 100. Retry on 429 and 5xx with exponential backoff capped at a few seconds. The `gtm` HTTP client does this for every adapter.

## Pagination

List endpoints return `items` plus `next_starting_after`. Pass it back as `?starting_after=<value>`. Maximum `limit=100` per page. The cursor is a timestamp, not an ID.

Account listing is unreliable for a full inventory when many accounts share a creation timestamp, for example after a bulk import. Enumerate accounts by search terms or by tag and reconcile the union, and keep your own registry as the source of truth (observed 2026-05, verify against current docs).

## Key endpoints

| Purpose | Method | Path | Notes |
|---|---|---|---|
| List campaigns | GET | `/campaigns` | paginated; `status` is an integer code |
| Read one campaign | GET | `/campaigns/{id}` | full sequences array and schedule |
| Create campaign | POST | `/campaigns` | requires `name` and `campaign_schedule` |
| Pause campaign | POST | `/campaigns/{id}/pause` | the adapter calls this immediately after create |
| Update campaign | PATCH | `/campaigns/{id}` | sequences must be sent as the full array |
| Campaign analytics | GET | `/campaigns/analytics?id=<id>` | per-campaign counts, optional date range |
| List leads | POST | `/leads/list` | filter key is `campaign`, not `campaign_id` |
| Accounts | GET | `/accounts` | see pagination caveat |
| Warm-up analytics | POST | `/accounts/warmup-analytics` | batch of emails; health scores live here, not on `/accounts` |
| Enable warm-up | POST | `/accounts/warmup/enable` | `{"emails": [...]}`, max 100 per call, one job at a time |
| Placement tests | GET | `/inbox-placement-analytics` | plus `/inbox-placement-analytics/stats-by-test-id` |

### Create payload shape

`campaign_schedule` is mandatory. Minimal valid shape:

```json
{
  "name": "Experiment 12 draft",
  "campaign_schedule": {
    "schedules": [
      {
        "name": "Weekdays",
        "timing": {"from": "08:00", "to": "17:00"},
        "days": {"0": false, "1": true, "2": true, "3": true, "4": true, "5": true, "6": false},
        "timezone": "Europe/Berlin"
      }
    ]
  }
}
```

Day keys run `"0"` (Sunday) to `"6"` (Saturday). Sequences are optional on create:

```json
{"sequences": [{"steps": [{"type": "email", "delay": 0, "variants": [{"subject": "…", "body": "…"}]}]}]}
```

`delay` is in days by default. Variants are A/B alternatives picked per recipient. Bodies are HTML.

### Campaign status codes

| Code | Meaning |
|---|---|
| 0 | Draft |
| 1 | Active |
| 2 | Paused |
| 3 | Completed |
| 4 | Running subsequences |
| -1 | Accounts unhealthy |
| -2 | Bounce protect |
| -99 | Account suspended |

The adapter only accepts 0 or 2 after create and after pause. Anything else aborts before content is added.

### Analytics fields

`GET /campaigns/analytics` returns one object per campaign. Field names observed 2026-07 (verify against current docs): `campaign_id`, `campaign_name`, `leads_count`, `contacted_count`, `new_leads_contacted_count`, `emails_sent_count`, `open_count`, `reply_count`, `reply_count_automatic`, `bounced_count`, `unsubscribed_count`, `completed_count`, `total_opportunities`, `total_opportunity_value`.

Compute reply rate as `(reply_count + reply_count_automatic) / new_leads_contacted_count` if you want to match the Instantly dashboard. Positive replies are not in this endpoint; classify replies yourself or read the lead status.

## Gotchas

| Symptom | Cause | Fix | Observed |
|---|---|---|---|
| 400 on `POST /campaigns` | `campaign_schedule` missing | always send at least one schedule | 2026-09 |
| PATCH removes existing steps | PATCH replaces the whole `sequences` array | GET, merge, then PATCH the full array | 2026-05 |
| 403 with Cloudflare error 1010 on v1 | missing `User-Agent` | send a browser-like UA on every call | 2026-04 |
| 401 on some calls | workspace override header present | remove it | 2026-05 |
| 500 on PATCH with `custom_variables` | field not writable via API | set custom variables in the UI | 2026-05 |
| Timezone rejected | some IANA zones are not in the allowed list | use an allowed zone with the same offset; read the error body for the list | 2026-05 |
| Lead filter returns everything | `campaign_id` ignored on `/leads/list` | use `campaign` | 2026-04 |
| Bulk delete stops at about 50 | v1 delete caps per call | loop in chunks of 50, or delete in the UI for thousands | 2026-04 |
| Duplicate companies in a campaign | dedupe flags on lead add work by email only, not by domain | run a domain-overlap check across campaigns before upload | 2026-04 |
| Warm-up flag ignored on PATCH | `warmup_status` is read-only | call `/accounts/warmup/enable` | 2026-05 |
| 409 on warm-up enable | one warm-up job at a time per workspace | sleep 6 to 10 s and retry | 2026-05 |
| Health score missing from `/accounts` | scores live in warm-up analytics | POST `/accounts/warmup-analytics` with email batches | 2026-05 |
| Cloned campaign never sends | clones start in status 0 | activation is a human action in the UI | 2026-05 |
| Fleet exported from a mailbox vendor shows warm-up off | exports carry config, not the enable toggle | enable warm-up after every export and re-check | 2026-07 |
| Empty `signature` on accounts | vendor export or bulk import left it blank | verify every account's signature is non-empty before launch | 2026-06 |

## What the gtm CLI does with it

- `gtm campaign plan` validates a `CampaignDraft` and records an immutable plan.
- `gtm campaign apply --plan <id>` creates an empty shell with the schedule, pauses it, verifies status 0 or 2, then adds sequence steps, then verifies again. It never adds leads, never assigns sending accounts, never activates.
- `gtm sync campaigns` pulls campaign records and, where the adapter supports it, campaign analytics into your store so `gtm review outreach` can compute rates.
- Nothing in the CLI calls `/activate` or any send endpoint.

## Verify before coding

Fetch the endpoint page on https://developer.instantly.ai/ before adding a call. Check the required fields, the status vocabulary, and whether the response wraps results in `items`. Add new gotchas to the table with the date you saw them.
