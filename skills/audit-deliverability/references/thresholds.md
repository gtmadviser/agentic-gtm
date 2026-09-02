# Deliverability thresholds

Every number the audit compares against, in one place. Treat them as defaults for B2B cold email from secondary domains. Tighten them for regulated markets; never loosen them without a written decision in `strategy/decisions.md`.

## Fleet and domains

| Item | Threshold | Why |
|---|---|---|
| Sending domain | Never the primary company domain | One bad week must not damage sales, support, or product email |
| TLD | `.com` only | Cheap TLDs (`.xyz`, `.click`, `.top`) are spam-scored on arrival |
| Domain name | Lookalike of the brand, not random words | Recipients and filters read it |
| Mailboxes per domain | Max 2 for new provisioning | Limits blast radius when one mailbox goes bad |
| Domains per persona | 3 to 5 at the start | Diversity before scale |
| Redirect | Every sending domain 301s to the real website | Unresolvable domains look fake and hurt placement |
| DNS | SPF, DKIM, DMARC, custom tracking domain, root and www A record on every domain | Missing auth is the most common fixable cause of spam placement |
| Domain cooldown | Some providers block new mailboxes on a domain for 24 h after a create or delete | Create a domain's full batch in one request |

## Mailboxes and sending

| Item | Threshold |
|---|---|
| Daily sends per mailbox | 20 to 30; size the fleet at 20 |
| Sending gap | 8 to 12 minutes between sends per mailbox |
| Warm-up before first cold send | 14 to 21 days; 21 preferred; never under 10 |
| Warm-up ramp | Start about 5 a day, add 2 to 5 a day, cap about 40 a day of warm-up traffic |
| Warm-up reply rate setting | About 30% |
| Warm-up score to stay in a campaign | 90 or higher; drop under 90 before a build |
| Warm-up status | Verified active by re-reading the provider, not by the enable call's response |
| Signature | Non-empty on every campaign mailbox, matching the persona |
| Mailboxes per campaign | Each mailbox in exactly one campaign; split evenly across A/B siblings |
| Ramp on launch | About 25% of daily cap on day 0, full cap over about 10 days |

## Lists and bounces

| Item | Threshold |
|---|---|
| Verification | 100% of the list verified before send |
| Bounce, campaign level | Above 2%: pause, re-verify, resume with ramp |
| Bounce, single sender | Above 5%: remove the sender from campaigns, check auth and listing |
| Bounce at T+1 after launch | Under 3% or hold the ramp |
| Suppression | Unsubscribes and hostile replies suppressed in the CRM the same day and excluded from every future build |
| Duplicate domains | One contact per company domain across all active campaigns |

## Replies and rotation

| Item | Threshold |
|---|---|
| Healthy mailbox | At least 1% reply rate after about 200 sends |
| Reply-rate rotation, stage 1 | 50 sends and 0 human replies: watch |
| Reply-rate rotation, stage 2 | 100 sends and 0 human replies: flag and rotate out |
| Performance rotation | Bottom 10% of senders by bounce rate rotated weekly |
| Hostile replies | Above 0.3% of sent: pause and review copy and list |
| Unsubscribe rate | Above 2% of sent: pause and review list fit |

## Placement

| Item | Threshold |
|---|---|
| Cadence | Weekly, one test per provider group |
| Pass bar | 80% or higher inbox on the primary consumer ESP per group |
| Fail bar | Any provider group in spam majority |
| Freshness at launch | Passing test under 7 days old |
| Auth in test | 100% SPF, DKIM, DMARC pass; any failure is a fixable misconfiguration |

## Burn

| Item | Threshold |
|---|---|
| Unit of judgement | Domain, never a single mailbox |
| Minimum judged sends | 80 per domain; below that, "insufficient" |
| Burn test | Domain reply rate 0% and P(0 replies given the provider baseline) under 0.02 |
| Provider baseline | Reply rate of the provider family in the same window; the family itself must be at least 1% |
| Cross-check | Live inbox read for every candidate before it is reported |
| Retraction | Any verdict is re-judged when the window grows; recovered domains are un-flagged and the retraction recorded |

## Monitoring cadence

| When | Check |
|---|---|
| Daily | Health check: any campaign mailbox under the score threshold or with the wrong persona is swapped from the spare pool |
| Weekly, start of week | Performance check (bottom 10% by bounce); placement test per provider group |
| Weekly, mid-week | Reply-rate rotation (two stages); fleet snapshot |
| Weekly, end of week | Deliverability report feeding `weekly-gtm-review` |
| Weekly, weekend | Cleanup of completed and no-reply leads into a queue; large deletes need approval and a store backup first |
| After any OS or scheduler change | Confirm the last log timestamp is fresh; a scheduler can die silently |
