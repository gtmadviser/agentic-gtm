# Mailbox and domain providers reference

The sending fleet is a set of secondary domains, each hosting a few mailboxes, warmed up and rotated. This page covers the vendors that provision that fleet. Numbers here are operating defaults from real fleets; tune them to your volume.

## Fleet rules that apply regardless of vendor

| Rule | Value | Why |
|---|---|---|
| Never send from the primary company domain | always | a burned primary domain breaks the business, a burned secondary domain costs a few euros |
| Secondary domains | lookalike names on `.com` or the local TLD, with a root and `www` A record and a redirect to the main site | domains that resolve to nothing look like spam infrastructure |
| Mailboxes per domain | 2 (max 3 for grandfathered fleets) | limits blast radius when one mailbox goes bad |
| Sends per mailbox per day | 20 to 30 cold sends | size the fleet by dividing the daily target by 20 |
| Warm-up before first cold send | 2 to 3 weeks, never less than 10 to 14 days | reputation is built, not bought |
| DNS on every domain | SPF, DKIM, DMARC, and a custom tracking domain | alignment failures show up as placement failures |
| Provider mix | at least two vendors, ideally Google and Microsoft backed | provider-level incidents then hit only part of the fleet |
| After every export to the sequencer | verify signature non-empty, daily limit set, warm-up enabled | exports routinely land with one of the three missing |
| Reconcile counts | vendor count versus sequencer count after every wave | silent drops happen |

Before launch, every mailbox in the campaign passes three filters: not on a burned domain, present in your usable-mailbox registry, and warm-up score above your threshold. Keep that registry in your store, not in the vendor UI; the vendor UI has reported dead infrastructure as healthy (observed 2026-08).

## Zapmail

Public docs: https://docs.zapmail.ai/ (verify). Provisions Google and Microsoft mailboxes on domains you own, manages DNS through its own nameservers, and exports mailboxes to sequencers.

| Item | Value |
|---|---|
| Env var | `ZAPMAIL_API_KEY` |
| Header | `x-auth-zapmail: <key>`, plus `x-service-provider: MICROSOFT` for Microsoft endpoints |
| Base URL | `https://api.zapmail.ai/api` |
| Rate limit | about 5 per second and 20 per minute on most routes; domain search much lower; sleep 250 to 400 ms |

Key endpoints observed 2026-04 to 2026-08 (verify against current docs):

| Purpose | Method | Path | Notes |
|---|---|---|---|
| Connect domains | POST | `/v2/domains/connect-domain` | body `domainNames` (plural array); singular returns 422 |
| Connection status | GET | `/v2/domains/connection-requests` | statuses walk from registration check to zone creation to SUCCESS |
| List domains | GET | `/v2/domains` | nested `mailboxes` array; `nextPage` never nulls, stop on empty page |
| Create mailboxes | POST | `/v2/mailboxes` | max 5 per domain per call; 202 means queued success |
| List mailboxes | GET | `/v2/mailboxes/list?page=&limit=50` | the older `/v2/mailboxes` GET returned 500 for months |
| Add DNS records | POST | `/v2/dns` | for tracking domains and extra records |
| Export to sequencer | POST | `/v2/exports/mailboxes` | needs a healthy third-party account ID; poll `/v2/exports/status` |
| Scheduled removal | PUT | `/v2/mailboxes/scheduled-removal` | the only removal API; per-mailbox delete is UI-only |

Gotchas:

| Symptom | Cause | Fix | Observed |
|---|---|---|---|
| Email DNS vanishes | registrar forwarding set on a Zapmail domain | never use registrar `set_forwarding`; configure redirects in Zapmail | 2026-05 |
| Connect request frozen with empty nameservers | NS check ran before propagation | delete the connection request and re-POST; check registry NS with `dig @a.gtld-servers.net` first | 2026-07 |
| 202 accepted, zero mailboxes after hours | assignment queue dropped the job | re-POST the full set only while the domain still has 0 boxes | 2026-07 |
| 400 "not enough mailboxes" despite credit | provisioning lag after purchase | wait 15 minutes and retry | 2026-07 |
| Export "succeeded" but sequencer missing boxes | third-party account expired | check `error` on the third-party account, reconnect in the dashboard, re-export, reconcile | 2026-07 |
| Exported boxes have warm-up off | export carries config not the toggle | enable warm-up on the sequencer side after every export | 2026-07 |
| Tracking-domain record accepted but never live | record raced zone creation | verify with `dig +short TXT <domain> @<zapmail nameserver>`; fix in the UI | 2026-06 |
| Microsoft SMTP works, IMAP fails | Microsoft disabled IMAP basic auth | connect Microsoft boxes to the sequencer via OAuth in the UI only | 2026-07 |
| Microsoft box errors again after reconnect | Entra-side lock | open a vendor ticket; every retry resets warm-up | 2026-08 |
| Nameserver mismatch | old domains on Cloudflare, new on ClouDNS | do not mix; use what the vendor assigns per domain | 2026-04 |

Provision Google mailboxes first when you can. In one fleet, none of the Google mailboxes ever errored while every failure was a Microsoft seat (observed 2026-08, one fleet, not a law).

## Mission Inbox

Public docs: https://doc.v4.missioninbox.com (verify). SMTP-relay mailboxes on your domains, cheap per box, DNS set at your registrar.

| Item | Value |
|---|---|
| Env var | `MISSION_INBOX_API_KEY` |
| Header | `x-server-api-key: <key>`; bearer or api-key schemes return 401 |
| Base URL | `https://api.v4.missioninbox.com/api` |

| Purpose | Method | Path | Notes |
|---|---|---|---|
| Projects | GET | `/projects` | you need the project ID for creates |
| Bulk create domains | POST | `/domains/bulk-create` | returns a task ID; poll `/tasks/{id}` to COMPLETED |
| Domain with DNS records | GET | `/domains/{domainName}` | returns the exact SPF, DKIM, MX, DMARC records to set |
| Bulk create mailboxes | POST | `/mailboxes/bulk-create` | async; passwords cannot contain `#` |
| Push to sequencer | POST | `/mailboxes/bulk-connect-instantly` | max 500 emails per call; boxes arrive with warm-up off |
| Statistics | GET | `/mailboxes/statistic` | ready, warming, unused |

The API does not expose remaining capacity; check the dashboard before bulk creates. DNS auto-deploy exists only for a couple of registrars; otherwise set records yourself and re-send every existing record when you update, or MX and DKIM disappear.

## Registrars: Dynadot and Namecheap

Both expose list and DNS APIs. Rate limits are undocumented; one call per second is safe (observed 2026-05).

| Rule | Detail |
|---|---|
| Nameserver changes | `set_ns` style calls take up to 100 domains; propagation to the registry takes minutes to an hour |
| DNS record updates | re-send every record; partial updates drop the rest |
| Redirects | set at the mailbox vendor when it manages DNS, at the registrar only for domains it still serves; use the numeric redirect type the API expects |
| Forwarding | never on domains whose DNS lives at a mailbox vendor |
| Inventory | keep a domain registry in your store with registrar, status, provider, and mailbox count; registrar lists alone miss domains bought under another account |

## Warm-up tools

Sequencers ship their own warm-up (Instantly warm-up, lemwarm). Rules that hold across them:

- Verify warm-up actually started; both vendors have silent failure modes.
- Do not touch mailboxes that arrive pre-warmed from a vendor; their configuration is provider-specific.
- Read health scores from the analytics endpoint, not the account list.
- Warm-up score under your threshold means the mailbox leaves the campaign that day, not next week. Automate the daily check.
- Track the warm-up start date per mailbox so the 14-day gate is a query, not a memory.

## What the gtm CLI does with it

Nothing yet. Fleet provisioning stays in vendor-specific scripts outside this repository because every fleet differs. The `audit-deliverability` skill reads the rules above and the sequencer state; it never provisions, deletes, or changes DNS.

## Verify before coding

Every vendor in this file changed at least one endpoint in the last six months. Fetch the docs, then run one domain end to end and confirm with `dig` before batching.
