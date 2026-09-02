# Learnings log

`strategy/learnings.md` is the append-only record of what the team believes to be true about its outreach and the evidence behind each belief. Read it before writing copy, designing an experiment, or launching a campaign. If you are about to violate a learning, open a counter-hypothesis first.

## Format

One line per learning. Date, statement, evidence pointer.

```
- YYYY-MM-DD: <finding as a statement, not as the hypothesis wording>. Evidence: <experiment id or report path>.
```

Superseded learnings are struck through and link to the replacement:

```
- ~~2026-05-12: Scenario openers beat every other opener. Evidence: exp-2026-05-openers.~~ Superseded by 2026-08-28 entry.
- 2026-08-28: Cost framing in the opener beat a scenario opener on positives per reply in a matched pair. Evidence: exp-2026-08-cost-framing-opener.
```

## Sections

```markdown
# Learnings

## Validated
Findings from experiments closed as won and from baseline analyses at solid certainty.

## Anti-learnings
Things confirmed not to work. Each is a prohibition until a counter-hypothesis closes as won.

## Open questions
Observations that need data. Each names the data that would settle it.
```

## Entry rules

1. Only closed experiments, baseline analyses at solid certainty, and direct data observations produce entries. Opinions do not.
2. State the finding, not the hypothesis. "Reminder-style follow-ups earn replies and no opportunities" is a finding. "Test reminder follow-ups" is not.
3. Every entry has an evidence pointer that a reader can open.
4. Never delete. Supersede with strike-through and a link.
5. Anti-learnings are written as prohibitions with the condition under which they apply, for example "for cold email to a verified list".
6. Open questions name the missing data and, where possible, the cheapest way to get it.

## Example (fictional)

```markdown
## Validated
- 2026-07-31: Replicating a winning angle into an adjacent segment kept positives per 1k within 20% of the original. Evidence: exp-2026-07-partner-replication.
- 2026-07-28: Cost framing in the opener beat a scenario opener on positives per reply in a matched pair. Evidence: exp-2026-08-cost-framing-opener.

## Anti-learnings
- 2026-06-30: Follow-ups that restate the first email earn replies and zero opportunities for cold email to a verified list. Evidence: exp-2026-06-reminder-followup.
- 2026-05-20: Bulk email to an event attendee list without a warm anchor produced no positives at usable certainty. Evidence: exp-2026-05-event-bulk-email.

## Open questions
- Do afternoon sends convert better per send, or is the afternoon edge a campaign-mix artifact? Needs a single campaign split by send window with the same list. Cheapest path: two schedule blocks on one campaign for three weeks.
- Are meetings under-recorded because the meeting field is never set? Needs a spot check of ten positive threads against the CRM.
```

## Promotion path

Experiment closes in `review-outreach` → one line here → the weekly review cites the line → `refine-icp`, `write-outreach`, or `stage-campaign` update their rules with a pointer to the entry.
