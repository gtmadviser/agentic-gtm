# Monthly review

Run on the first working day after month end, after the normal weekly steps. It is the strategic read; weekly reports carry the operational detail. Target length: one page.

## Step 1: Snapshot and archive

Refresh campaigns and CRM. Archive the snapshot before computing anything. The prior-month baseline is the snapshot closest to the previous month end.

## Step 2: Month-over-month trends

Compute deltas for:

- Sent, delivered, bounce rate
- Positive replies, positives per 1k sent, positive reply rate
- Meetings, opportunities, and the interested-to-meeting conversion
- Active campaigns, campaigns launched, campaigns ended, drafts never launched
- Owner movement against the team median: who moved up, who moved down, who went dormant
- Segment or tag performance: which angles, channels, and ICP slices produced, which stagnated

Show each as this month, last month, delta. Mark any row whose sample is below usable.

## Step 3: Hypothesis register sweep

For every experiment file:

| State | Rule |
|---|---|
| `draft` or `approved` for more than 30 days with no campaign | launch it this month or set result `abandoned` with a reason |
| `running` | check the decision rule; route crossed rules to `review-outreach` |
| closed this month | confirm one line exists in `strategy/learnings.md` |

## Step 4: Promote learnings

For each experiment closed this month, add one dated line to `strategy/learnings.md` under "Validated" or "Anti-learnings". The line states the finding, not the hypothesis wording, and links the experiment file as evidence.

## Step 5: Retire what does not work

- Campaigns with 500 or more sends and zero positives over the month: recommend retirement; record the decision with owner and date.
- Drafts older than 30 days that never launched: recommend deletion or a launch date.
- Senders that spent the month below the warm-up floor: route to `audit-deliverability`.

## Step 6: Seed next month

Open 2 to 4 new experiment files from this month's data and learnings. Each gets a hypothesis, metric, minimum sample, and decision rule before anyone builds a campaign for it. Register them in `experiments/README.md`.

## Step 7: Write the monthly report

`reports/monthly-<YYYY-MM>.md` with these sections:

1. Headline numbers with month-over-month deltas
2. Owner movement
3. Hypothesis scorecard: closed won, closed lost, abandoned, running, newly opened
4. Learnings added this month, copied from the learnings log diff
5. Recommendations for next month: 3 to 5 actions, each tied to a hypothesis or an infrastructure gap, each with an owner

## What the monthly review does not do

- It does not re-run copy-level A/B analysis; that belongs to `review-outreach`.
- It does not audit list quality; that belongs to `source-tam` and `refine-icp`.
- It does not change any campaign state.
