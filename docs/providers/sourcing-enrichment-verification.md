# Sourcing, enrichment, and verification providers reference

## The waterfall rule

Cheap and precise first, expensive last, verify every find, stop when confident. A typical email waterfall:

1. Existing records in your store and CRM (free).
2. A bulk database search such as AI Ark or Blitz (credits per row).
3. Pattern inference from a known company pattern, then verification (cheap).
4. Finder and verifier services in ascending price order.
5. A manual or Clay-assisted pass for the high-value leftovers.

Every address that reaches a campaign passes a verifier first. Unverified lists run 7 to 29 percent bounce and burn domains (observed across fleets 2026). Keep verification results append-only with provider and date so re-runs never re-buy the same answer.

Before any credit-consuming run: print the row count, the estimated credits, the remaining balance, and the cap. Get approval. Run a probe of 5 to 25 rows and inspect false positives before scaling.

## AI Ark

Public docs: https://docs.ai-ark.com/ (agent index at https://docs.ai-ark.com/llms.txt)

| Item | Value |
|---|---|
| Env var | `AI_ARK_API_KEY` |
| Header | `X-TOKEN: <key>` |
| Base URL | `https://api.ai-ark.com/api/developer-portal` |
| Rate limit | about 5 per second, 300 per minute |
| Credits | check `GET /v1/credit` before batch runs |

| Purpose | Method | Path | Notes |
|---|---|---|---|
| People search | POST | `/v1/people` | `account` filters plus `contact` filters; `page` is zero-based; `size` max 100 |
| Company search | POST | `/v1/companies` | account filters only |
| Export with email | POST | export endpoints keyed by `trackId` | bulk up to 10,000; credits per found email |
| Lists | POST | list endpoints | exclude already-sourced people on re-runs |

Response shape: `content[]`, `totalElements`, `totalPages`, `trackId`. Keep the `trackId`; it drives export for the same result set. Matching modes `SMART`, `WORD`, `STRICT`: start SMART, tighten when noisy. 404 means no rows for the filter combination, not an auth failure. Emails from search are found, not verified.

Also exposes a remote MCP server for interactive sourcing; use REST for reproducible batch pulls.

## Blitz

Public docs: https://docs.blitz-api.ai

| Item | Value |
|---|---|
| Env var | `BLITZAPI_API_KEY` |
| Header | `x-api-key: <key>` |
| Base URL | `https://api.blitz-api.ai/v2` |
| Rate limit | plan-dependent, about 5 per second; read `/account/key-info` |

| Purpose | Method | Path | Notes |
|---|---|---|---|
| Key info | GET | `/account/key-info` | credits, rate limit, allowed APIs |
| Company search | POST | `/search/companies` | cursor pagination; `max_results` up to 25 |
| People search | POST | `/search/people` | company plus person filters; `max_results` up to 50 |
| Waterfall by company | POST | `/search/waterfall-icp-keyword` | decision-maker by keyword per company LinkedIn URL |
| Email enrichment | POST | `/enrichment/email` | needs a person LinkedIn URL |

Cursor pagination: pass `cursor` from the previous response until it is empty. Employee range values are fixed strings such as `"1-10"` and `"11-50"`. Company `type` filters let you exclude non-profits and self-employed.

## Email verification providers

Any of Kitt, MailTester, MillionVerifier, or a comparable verifier works. The contract the engine expects:

| Verdict | Action |
|---|---|
| valid | eligible to send |
| catch-all or risky | send only to high-fit leads, cap the share per campaign, watch bounce on day one |
| invalid | never send; keep the lead for LinkedIn-only outreach |
| unknown | re-verify with a second provider before deciding |

Provider notes (observed 2026, verify against current docs):

- Kitt: `x-api-key` header, `POST /job/verify_email` with `realtime: true` for synchronous results, `POST /job/find_email` for name plus domain. Concurrency cap around 15. Credits at `GET /credit`.
- MillionVerifier and MailTester: batch upload and poll patterns; results include catch-all detection. Cheap enough to run on every list.
- Skip personal mailbox domains; B2B finders return almost nothing there and the credits are wasted.

Store `email_status` and `verified_at` with the provider name next to every contact. A verdict older than 90 days is stale.

## LinkedIn signal providers

Public post search and engagement APIs (for example Harvest) find people publicly writing about the problem you solve. Rules:

- Browser-like `User-Agent` required or Cloudflare blocks the call.
- Result caps around 1,000 per query; narrow with filters until the set fits.
- No emails in LinkedIn data; email resolution is a separate step.
- Recency is the signal: prefer posts from the last 60 days.
- Never quote a post back at someone; reference the theme.
- Anonymised profiles are unusable as leads; ICP-narrowed queries surface more named ones.
- Engagers of a relevant post are often warmer than its author. Run every engager's company through your competitor and customer exclusions before keeping them.

## Clay

Public docs: https://docs.clay.com

Clay is the enrichment hub when you need waterfalls across many vendors and a spreadsheet-like review surface. Rules:

- Tables ingest rows through a per-table webhook URL. Treat the URL as a secret.
- Keep tables under about 50,000 rows; split by segment.
- Prefer a direct provider call for one-off lookups; Clay is for workflows.
- Export naming convention: `YYMMDD_<segment>_<source>_{Safe,Risky}Emails.csv`. Safe means verified valid; Risky means catch-all or unknown. Load them separately and cap the Risky share.

## Signals and deduplication

When you build a signal feed (job posts, funding, hiring, tech changes, website visits), give every signal a deterministic ID such as `sha1(signal_type | entity_key | natural_key)` and insert with conflict-ignore. Stage signals in your store before they touch the CRM. Route by ownership: owned account, notify the owner; unassigned account, eligible for a campaign; customer or open opportunity, notify only.

## What the gtm CLI does with it

- `gtm source accounts|contacts --query <file>` runs the explicitly configured sourcing provider, normalises results into the shared `Account` and `Contact` contracts, deduplicates on domain or LinkedIn URL, and upserts with provenance into your store.
- Verification has no adapter yet. Run your verifier, then import verdicts as contact attributes. The `source-tam` skill requires verification before any campaign draft references the list.

## Verify before coding

Filter vocabularies change often on sourcing APIs. Fetch the search reference page before composing an unusual query rather than guessing field names.
