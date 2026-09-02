# Pre-launch checklist

Two parts. The filters run in the CLI or a script before the draft exists. The launch checklist runs in the provider UI by the human who launches.

## Filters (mandatory, in this order)

Run each, record the count after each, in `campaigns/<slug>.md`.

| # | Filter | Source of truth | Why it exists |
|---|---|---|---|
| 1 | Remove burned sender domains from the sender set | the burned-domain list in the store | burned domains kept re-entering builds until the filter became mandatory |
| 2 | Keep only healthy, verified mailboxes | provider API: warm-up running, warm-up score 90 or above, 14 days or more of warm-up, not flagged | dashboards have reported dead mailboxes as warm and active; in one build, over half the senders were dead infrastructure |
| 3 | Remove recipients who ever bounced | the sending log, not a status column | a status column that is null for a whole pool passes every bounced address silently |
| 4 | Remove recipients contacted within 60 days, and every replier | the sending log, plus date prefixes in campaign names | re-approach window; repliers get a human, not a sequence |
| 5 | Cross-campaign domain dedupe | all active campaigns | one company, one campaign at a time; otherwise two people at the same firm get two pitches in a week |
| 6 | Apply suppression lists | store: unsubscribes, hostile replies, customers, open deals, competitors, legal exclusions, personal addresses | opt-outs are honoured the same day; customers and open deals are never cold-emailed |
| 7 | Verify 100 percent of remaining addresses | verification provider result stored per contact | unverified lists have bounced 7-29 percent and killed domains |
| 8 | Check variable fill on the final pool | store columns | fill rate can change after filters; below 100 percent needs the fallback from the copy file |

A pool that loses more than 30 percent at filter 3 or 4 is a sourcing problem. Stop, fix sourcing, rebuild.

## Draft checks

- [ ] Copy passed the slop gate (`write-outreach/references/anti-slop-writing.md`) and the rubric at 85 or above
- [ ] Draft steps equal the copy file byte for byte
- [ ] `status` is `paused`
- [ ] Name has the date prefix
- [ ] Schedule: recipient timezone, working days, sending window
- [ ] Suppression list names listed in the draft
- [ ] Plan created; hash and expiry shown to the operator
- [ ] Operator approved by plan ID
- [ ] Dry-run passed
- [ ] Applied once; result `paused` or `draft`

## Launch checklist (UI, by the launching human)

The CLI cannot do any of these. That is the design.

- [ ] Provider shows the campaign as draft or paused
- [ ] Senders assigned in the UI; the API creates campaigns with no senders on purpose
- [ ] Sender count matches the sizing; A/B arms within one sender of each other
- [ ] Schedule and timezone match the draft
- [ ] Step delays render as intended (conditional delays do not always render the way the API set them)
- [ ] Preview with a test lead: every variable filled, every fallback reads well, signature present, no brand domain in touch 1
- [ ] Daily cap per sender set to the ramp start (about 25 percent of the cap)
- [ ] Tracking: open tracking off if the provider allows, custom tracking domain set per sending domain
- [ ] Unsubscribe handling active and tested with one address
- [ ] Recipient count in the provider equals the count after filter 8
- [ ] Launch owner, date, and decision logged in `strategy/decisions.md`

## Day 1 monitoring (after launch)

| Check | Threshold | Action |
|---|---|---|
| Bounce, whole campaign | above 2 percent | pause campaign; re-verify; find the bad source |
| Bounce, one sender | above 5 percent | remove sender same day; check its domain |
| Replies, one sender | zero after 100 sends while peers reply | rotate sender out; run a placement test |
| Unsubscribe or hostile replies | above 2 percent unsubscribes or 0.3 percent hostile | pause; review copy and pool |
| Variable rendered empty | any | pause; fix copy file; re-stage |

First-day bounce spikes have appeared in every set we have run. Make this table a gate, not a report.
