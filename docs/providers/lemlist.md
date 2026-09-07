# lemlist reference

Public docs: https://developer.lemlist.com/ (agent index at https://developer.lemlist.com/llms.txt). Sequence-step CRUD is only partly documented; the shapes below were confirmed by use and can change without notice.

## Role in the engine

lemlist is the multichannel sequencer: LinkedIn visits, invites, and messages plus email, with lemwarm for mailbox warm-up. The engine uses it for execution only. Lead state of record lives in your CRM and your store.

## Auth

| Item | Value |
|---|---|
| Env var | `LEMLIST_API_KEY` |
| Scheme | HTTP Basic, empty username, key as password |
| Header | `Authorization: Basic base64(":" + key)` |
| Also send | `Content-Type: application/json` and a browser-like `User-Agent` |
| Base URL | `https://api.lemlist.com/api` |

A default library user agent gets a Cloudflare 403 with error 1010 (observed 2026-05, verify against current docs). Always set one.

## Rate limits and retries

About 20 requests per 2 seconds. Sleep 150 to 200 ms between calls. Retry safe reads on 429 and 5xx with backoff; do not automatically repeat mutations.

## Pagination

`GET /campaigns?offset=0&limit=100` uses offset paging and returns a flat array. `GET /activities` takes `campaignId`, `createdAtFrom`, and `createdAtTo`. `GET /campaigns/{id}/sequences` returns the whole tree in one response.

## Key endpoints

| Purpose | Method | Path | Notes |
|---|---|---|---|
| List campaigns | GET | `/campaigns` | `_id`, `name`, `status`, `senders[]`, `createdAt` |
| Read campaign | GET | `/campaigns/{id}` | status reads as draft, paused, or running |
| Create campaign | POST | `/campaigns` | body `{"name": "..."}`; returns `_id` and `sequenceId` |
| Pause campaign | PATCH | `/campaigns/{id}` | `{"state": "paused"}`; there is also a pause route the adapter uses |
| Read sequence tree | GET | `/campaigns/{id}/sequences` | keyed by sequence ID, each with `steps[]` |
| Create step | POST | `/sequences/{sequenceId}/steps` | at the sequence level, not under the campaign |
| Update step | PATCH | `/sequences/{sequenceId}/steps/{stepId}` | must include `type` |
| Delete step | DELETE | `/sequences/{sequenceId}/steps/{stepId}` | |
| Add lead | POST | `/campaigns/{id}/leads/{email}?deduplicate=true` | LinkedIn-only leads are allowed |
| Remove lead | DELETE | `/campaigns/{id}/leads/{leadId}?action=remove` | without `action=remove` nothing is removed physically |
| Activities | GET | `/activities?campaignId=...` | sends, opens, replies |
| Campaign stats | GET | `/v2/campaigns/{id}/stats?startDate=...&endDate=...` | both dates required |
| Team and users | GET | `/team`, `/users/{id}` | user mailboxes with `usm_*` IDs |
| Warm-up | POST | `/lemwarm/{usm}/start`, `/lemwarm/{usm}/pause` | score via `GET /lemwarm/{usm}/settings` |

### Step bodies

All steps need `type` and `delay` (integer days). Do not send `title`, `index`, or `sequenceStep`.

```json
{"type": "linkedinInvite", "delay": 0, "message": ""}
{"type": "linkedinSend",   "delay": 2, "message": "{{firstName}}, ..."}
{"type": "email",          "delay": 3, "subject": "...", "message": "<div>...</div>"}
{"type": "manual",         "delay": 1, "title": "Call", "message": "..."}
```

The email body field is `message`, not `body`. Bodies are HTML. Invite notes cap at about 300 characters. An empty invite message sends a bare invite, which performs at least as well as a note in every test we have seen.

Conditionals: `{"type": "conditional", "conditionKey": "linkedinInviteAccepted", "delayType": "within", "delay": 3}` creates the branch and its two child sequences. `delayType` must be `within` with a delay of at least 1; `waitUntil` blocks the fallback branch forever.

Template variables: `{{firstName}}`, `{{lastName}}`, `{{companyName}}`, `{{accountSignature}}`. Fallback syntax is `{{a|b}}` with no spaces around the pipe. End emails with `{{accountSignature}}`; never hard-code a signature block.

## Gotchas

| Symptom | Cause | Fix | Observed |
|---|---|---|---|
| New campaign shows `running` | create returns state running with 0 senders | pause immediately after create; the adapter does | 2026-05 |
| 405 on `/campaigns/{id}/sequences/.../steps` | steps are addressed by sequence ID | use `/sequences/{seqId}/steps` | 2026-05 |
| 400 "message is required" | used `body` | use `message` | 2026-05 |
| 400 "Type is required" on PATCH | PATCH is a typed partial write | always include `type` | 2026-05 |
| 400 on POST with `title` on email or LinkedIn steps | title not settable | omit it; only `manual` steps take a title | 2026-06 |
| 500 on PATCH of a populated conditional | not updatable in place | delete and recreate | 2026-06 |
| Cannot add steps to fallback branch | conditional created with `waitUntil` | recreate with `delayType: "within"` | 2026-06 |
| Folder or sender PATCH returns 200 but nothing changes | UI-only operations | assign senders and file campaigns in the UI | 2026-07 |
| No `DELETE /campaigns/{id}` | not exposed | pause and rename via API, delete in the UI | 2026-06 |
| Lead still listed after removal | plain DELETE does not remove | add `?action=remove` on the lead ID | 2026-05 |
| Campaign-scoped lead list is stale after state change | classic vs new campaign views differ | verify on `GET /leads/{email}` | 2026-06 |
| 400 "email in the graveyard" | address previously unsubscribed or suppressed | treat as skip, keep the suppression | 2026-05 |
| Gmail mailbox will not connect via API | Google requires OAuth | connect in the UI | 2026-04 |
| Microsoft mailbox flips to ERROR hours after connect | IMAP basic auth is disabled by Microsoft | connect via OAuth in the UI; do not trust the 201 | 2026-07 |
| Warm-up "started" but nothing warms | seat cap overrun fails silently | re-fetch and check `mailboxes[].lemwarm.active` | 2026-06 |
| Warm-up score not on the user object | lives in lemwarm settings | `GET /lemwarm/{usm}/settings` and read `deliverability.score` | 2026-06 |
| Rep attribution wrong in reports | campaign-name regex | resolve `createdBy` through the team API | 2026-05 |

Seat rule: lemlist caps mailboxes per user at about five, and an OAuth-connected primary mailbox counts toward it. Plan burner allocation accordingly.

## What the gtm CLI does with it

- `gtm campaign apply --plan <id>` creates the shell, pauses it, verifies `paused` or `draft`, posts steps to the root `sequenceId`, then verifies again. It normalises step bodies so `body` becomes `message` and every step carries `type` and `delay`.
- `gtm sync campaigns` pulls campaign records. Campaign stats need a date range; import them with `gtm metrics import` if the adapter cannot fetch them for your plan.
- The CLI never assigns senders, adds leads, or changes state to running.

## Verify before coding

Fetch https://developer.lemlist.com/llms.txt and the specific page before writing new calls. Sequence endpoints are undocumented; probe against a throwaway paused campaign and record what you find here with a date.

HTTP retry policy: automatic retries are limited to safe reads. Mutations are attempted once; ambiguous outcomes require provider reconciliation before another write. See [reliability upgrade notes](../reliability-upgrade.md).
