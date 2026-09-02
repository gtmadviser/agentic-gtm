# Weekly rhythm

Three fixed checkpoints. Each is short, has a threshold, and produces a decision. All three write into the same weekly report file so Friday's document is complete without a rewrite.

## Monday: deliverability audit (15 minutes)

Inputs: `gtm --json sync campaigns`, `gtm --json review outreach`, mailbox health from the sequencer or `audit-deliverability`.

| Check | Threshold | Decision |
|---|---|---|
| Fleet positive reply rate, trailing 7 days | below 1% with 500 or more delivered | run the incident path in `audit-deliverability` before any copy change |
| Bounce rate per campaign, trailing 7 days | above 2% | pause recommendation for that campaign, list verification required |
| Bounce rate per sender | above 5% | remove the sender from rotation until verified |
| Senders below the warm-up floor the fleet uses | any | do not assign to campaigns this week |
| Campaigns with zero sends for 7 days while active | any | ask the owner: retire or restart |

Log the result as "clean", "watch", or "incident" with the affected campaign names. Close the checkpoint.

## Wednesday: positive-reply sweep (30 to 60 minutes)

Inputs: reply classification from `review-outreach` for the trailing 7 days.

| Check | Threshold | Decision |
|---|---|---|
| `positive_interested` replies without a human response | any older than one business day | respond today; interested leads decay within days |
| `positive_referral` replies | any | contact the referred person within 24 hours; store them with provenance |
| `negative_hostile` and `unsubscribe` | any | suppress contact and, for decision makers, the domain across all campaigns within 24 hours |
| Weekly positive replies per responder | above 50 | handoff needed; add a decision to split responders |
| Positives without a logged meeting or next step | above 30% of positives | process gap candidate; note for Friday |

Report counts by label and by campaign. Reply text never enters the report.

## Friday: campaign retrospectives (20 minutes per campaign)

Inputs: campaigns that reached 21 days since first send this week, their experiment files, and `review-outreach` verdicts.

Baseline is the fleet's positives per 1k for the same channel over the trailing 90 days, or the experiment's own preregistered floor when one exists.

| Result at day 21 | Verdict | Action |
|---|---|---|
| positives per 1k at 2 times baseline or better, usable certainty | keep and scale | scale-up is a decision for the operator; record it in `strategy/decisions.md` |
| within 50% to 200% of baseline | iterate | change one variable, new experiment version |
| below 50% of baseline, usable certainty | kill | mark `complete` with result `lost`, log the anti-learning |
| below 200 sends | too early | extend; set a date to re-check |
| safeguard tripped | pause | investigate first, judge later |

Log each verdict to the experiment file with the date and the report reference.

## The weekly document

By Friday the report holds:

1. What changed: launches, pauses, kills, list additions, infrastructure changes, team changes.
2. Evidence: window-labelled tables for volume, quality, pipeline, owners, and hypothesis progress.
3. Decisions needed: each with a deadline and the evidence it depends on.
4. Risks: safeguards, process gaps, capacity limits, expiring lists.
5. Next actions: one owner and a date each.

## Cadence hygiene

- Archive the raw snapshot the review used (store or `.gtm/snapshots/<date>/`) so next week's delta is computed against a fixed baseline, not a re-pulled one.
- Post the review only after the operator reads it. Plan, then apply.
- Reviews are never edited after publication. A correction is a new file that names the one it supersedes.
