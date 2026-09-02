---
name: weekly-gtm-review
description: Run the weekly GTM operating review that combines pipeline, campaign evidence, experiments, risks, owners, and next actions, with an optional approval-gated Slack post and a deeper monthly sweep. Use for the recurring revenue-team review and its Monday, Wednesday, and Friday checkpoints; do not use as a raw dashboard dump or to post anything without an explicit apply.
---

# Weekly GTM Review

> This is the Iterate stage of the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate). It runs on a fixed rhythm, turns the week's evidence into decisions with named owners, and keeps the hypothesis register and learnings log alive. The review is a decision document, not a metrics export. Publishing to Slack goes through the same plan-then-apply gate as every other external write.

## When to use / when not to

Use when:

- It is the weekly review slot, or one of the three checkpoints (Monday deliverability, Wednesday replies, Friday retrospectives).
- The team needs a single page that says what changed, what the evidence shows, what needs a decision, and who owns each next step.
- Month end has passed and the monthly sweep is due.

Do not use when:

- Someone wants a number without a decision. Point them to `gtm --json review outreach` or `review pipeline`.
- The campaign data has not been refreshed this week. Refresh first; a review of stale data is a story, not a review.
- The goal is to post to Slack without the operator reading the report. There is no unattended publish path.

## Inputs

| Source | What it provides |
|---|---|
| `gtm --json sync campaigns` then `gtm --json review outreach` | Campaign counts, rates, certainty tiers, bounce flags |
| `gtm --json sync crm` then `gtm --json review pipeline` | Won, lost, and open opportunities kept apart |
| `gtm --json review weekly --output reports/weekly-<YYYY-MM-DD>.md` | The combined skeleton this skill fills in |
| `experiments/*.json` and `.md` twins | Running hypotheses, sample progress, decision rules |
| `strategy/learnings.md`, `strategy/decisions.md` | What is already known and decided |
| Previous `reports/weekly-*.md` | Prior-window values for deltas and open actions to close |
| `reports/outreach-*.md` from `review-outreach` | Verdicts and ledger entries closed this week |
| `gtm --json report slack plan|apply` | The publishing gate |

## Procedure

1. **Refresh only what is needed.** Run `gtm --json sync campaigns` and, if the CRM is configured, `gtm --json sync crm`. Import CSV metrics for channels the provider does not report. Note the refresh timestamp at the top of the review.
2. **Run the checkpoint for the day.** Follow `references/weekly-rhythm.md`: Monday is the 15-minute deliverability audit, Wednesday the positive-reply sweep, Friday the 21-day campaign retrospectives. Each checkpoint writes its findings into the same weekly report file so Friday's document is complete.
3. **Generate the skeleton.** Run `gtm --json review weekly --output reports/weekly-<YYYY-MM-DD>.md`. Keep the approved aggregates it writes; replace the placeholder interpretation with evidence.
4. **Compute deltas.** For sent, delivered, positives, meetings, opportunities, bounce rate, and positive reply rate, show this window against the prior window of equal length. State the window on every table.
5. **Keep pipeline in three columns.** Report won, lost, and open separately with counts and amounts where the CRM supplies them. Never sum them into one "pipeline" figure.
6. **Attribute by owner.** Use the provider's owner field. Show each owner against the team median for positives per 1k, and exclude shared campaigns and service accounts. Never derive ownership from campaign names.
7. **Check the process gap.** If positives exist and meetings booked stay at zero for two or more consecutive weeks, add the "process gap" flag to the meetings figure and assign an owner to the interested-to-meeting handoff. This is not a messaging problem and must not trigger copy changes.
8. **Sweep hypotheses.** For each experiment with status `running`, record sample progress against its minimum and whether its decision rule has been crossed. Route crossed rules to `review-outreach` for the verdict. Add the hypothesis progress table.
9. **Resolve or label conflicts.** Where two sources disagree (provider UI versus CLI, CRM versus sequencer), either resolve the definition and state it, or label the metric "unresolved" with both values. Never pick the friendlier number silently.
10. **Write decisions and actions.** Every decision needed has a deadline and an owner. Every next action has one human owner and a date. Actions without an owner are deleted, not carried.
11. **Publish only with approval.** If the operator approves publication, run `gtm --json report slack plan --report reports/weekly-<YYYY-MM-DD>.md`, present the plan (channel, summary, expiry, hash) and apply only with the exact returned ID via `gtm --json report slack apply --plan <id>`. Use `--dry-run` first when the channel changed. Webhook-only mode is unverified and must be labelled as such in the report.
12. **Monthly sweep.** On the first working day after month end, follow `references/monthly-review.md` in addition to the weekly steps: month-over-month trends, register sweep, learnings promotion, retirement of zero-return campaigns and never-launched drafts, and 2 to 4 seeded hypotheses for the next month.

## Hard rules

1. The review has exactly five sections in this order: what changed, evidence, decisions needed, risks, next actions. Metrics tables live inside evidence. Nothing else is a section.
2. Every metric shows its window and the prior-window delta. A number without a window is deleted.
3. Won, lost, and open pipeline are never combined.
4. Every next action has one named owner and a due date. Team-owned actions are not allowed.
5. Positives with zero meetings for two consecutive weeks produce the "process gap" flag and an owner for the handoff.
6. Bounce above 2% overall or above 5% for any sender appears in risks with a pause recommendation, even when the campaign is performing.
7. Owner rankings use the provider owner field and show the team median; campaigns without an owner are listed as unattributed.
8. Conflicting metrics are resolved with a stated definition or labelled unresolved. Silent selection is prohibited.
9. Campaign conclusions cite the experiment file they belong to. A campaign without an experiment gets the note "no preregistered rule; observation only".
10. A Slack post requires a plan ID from `report slack plan` and an explicit `report slack apply --plan <id>`. There is no other path.
11. The review contains aggregates only. No lead names, email addresses, reply text, or provider IDs.
12. Friday retrospectives apply the 21-day rule: keep a campaign at 2 times baseline or better, iterate one near baseline, kill one below 50% of baseline, and log each outcome to its experiment file.

## Checklist

- [ ] Data refreshed this week; timestamp at the top of the report
- [ ] Monday, Wednesday, and Friday checkpoint findings merged into one file
- [ ] Skeleton generated with `gtm --json review weekly`
- [ ] Every metric carries a window and a prior-window delta
- [ ] Pipeline shown as won, lost, open
- [ ] Owner table uses the provider owner field and shows the team median
- [ ] Process gap checked and flagged if triggered
- [ ] Hypothesis progress table filled for every running experiment
- [ ] Conflicts resolved with a definition or labelled unresolved
- [ ] Decisions have deadlines; actions have one owner and a date
- [ ] Slack publish, if any, went plan then apply with the exact ID
- [ ] No personal data in the report

## Checkpoint summary

| Day | Duration | Question answered | Output |
|---|---|---|---|
| Monday | 15 min | Is the fleet healthy enough to keep sending? | clean, watch, or incident, per campaign |
| Wednesday | 30 to 60 min | Has every positive reply been answered and every referral contacted? | counts by label, suppressions applied |
| Friday | 20 min per campaign | Which campaigns at day 21 are kept, iterated, or killed? | verdicts logged to experiment files |

The weekly document is finished when all three rows have an entry for the week.

## Output contract

| Artifact | Location | Content |
|---|---|---|
| Weekly review | `reports/weekly-<YYYY-MM-DD>.md` | Five sections, evidence tables with windows, hypothesis progress, owner-bound actions |
| Checkpoint notes | Same file, one subsection per checkpoint | Monday audit result, Wednesday sweep counts, Friday retro verdicts |
| Monthly review | `reports/monthly-<YYYY-MM>.md` | Headline numbers with month-over-month deltas, owner movement, hypothesis scorecard, learnings added, recommendations |
| Experiment updates | `experiments/<id>.json` and `.md` | Sample progress, status changes routed through `review-outreach` |
| Learnings | `strategy/learnings.md` | Closed findings promoted during the monthly sweep |
| Decisions | `strategy/decisions.md` | Retired campaigns, changed rules, approved scale-ups, each with owner and date |
| Slack plan and result | store tables `action_plans`, `apply_results` | Plan hash, channel, apply record; the report text itself stays in Git |

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Review is a list of numbers with no decisions | Skeleton was published as-is | Rewrite: each evidence table must end in a decision or a "no decision needed" line |
| Positives climb, meetings stay at zero | Handoff has no owner or the meeting field is never set | Process gap flag, assign the handoff owner, verify how meetings are recorded |
| Two reply rates for the same campaign | Unique-lead versus per-send denominator, or auto-replies included | State both definitions, use the experiment's, label the other unresolved |
| Owner leaderboard changes when campaigns are renamed | Name-based attribution slipped in | Rebuild from the owner field; delete the name-based table |
| Bounce spike on first send of a new campaign | List not verified before launch | Pause recommendation in risks; route to `audit-deliverability`; make verification a launch gate |
| Flagged campaign still running three weeks later | Pause recommendations have no owner or deadline | Escalate as a decision needed with a date; record in `strategy/decisions.md` |
| Slack apply rejected | Plan expired, changed, or already applied | Create a new plan from the final report; never edit the report after planning |
| Large share of drafts never launched | Campaign creation outpaces launch capacity | Monthly sweep retires drafts older than 30 days with a note |

## References

- [Weekly rhythm: Monday, Wednesday, Friday](./references/weekly-rhythm.md)
- [Monthly review](./references/monthly-review.md)
- [Report template with a fictional example](./references/report-template.md)

Licensed CC BY 4.0 by GTM Adviser.
