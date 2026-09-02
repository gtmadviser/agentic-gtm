# Weekly review template

Copy the template, replace every bracket, delete nothing else. A fictional filled example follows.

## Template

```markdown
# Weekly GTM review, week [NN] ([YYYY-MM-DD] to [YYYY-MM-DD])

Data refreshed: [timestamp]. Store: [supabase | files]. Prior window: [dates].

## What changed
- [launch / pause / kill / list / infrastructure / team change, one line each]

## Evidence

### Volume and quality (window: [dates]; prior: [dates])
| Metric | This window | Prior | Delta | Certainty |
|---|---:|---:|---:|---|
| Sent | | | | |
| Delivered | | | | |
| Bounce rate | | | | |
| Positive replies | | | | |
| Positives per 1k sent | | | | |
| Positive reply rate | | | | |
| Meetings | | | | [process gap flag if triggered] |
| Opportunities | | | | |

### Pipeline (CRM, as of [date])
| Status | Count | Amount |
|---|---:|---:|
| Won | | |
| Lost | | |
| Open | | |

### Owners (positives per 1k sent, window: [dates]; team median: [value])
| Owner | Sent | Positives | Per 1k | vs median |
|---|---:|---:|---:|---|

### Hypothesis progress
| ID | Status | Sample / minimum | Metric | Decision |
|---|---|---:|---|---|

### Data quality
- [definitions used, conflicts, unresolved items]

## Decisions needed
- [decision] by [date], depends on [evidence]

## Risks
- [safeguard, process gap, capacity, list expiry]

## Next actions
- [owner], [date]: [action]
```

## Filled example (fictional)

```markdown
# Weekly GTM review, week 31 (2026-07-27 to 2026-08-02)

Data refreshed: 2026-08-03 08:10 UTC. Store: supabase. Prior window: 2026-07-20 to 2026-07-26.

## What changed
- Launched "2026-07 Quiet Harbor Systems partner angle" (replication of the Copper Finch winner) on 2026-07-28.
- Paused "2026-06 Northstar Relay reminder follow-up" after the Friday retro (zero positives at 1,900 sends).
- 12 new senders finished warm-up; 4 remain below the floor and are not assigned.

## Evidence

### Volume and quality (window: 07-27 to 08-02; prior: 07-20 to 07-26)
| Metric | This window | Prior | Delta | Certainty |
|---|---:|---:|---:|---|
| Sent | 6,420 | 5,880 | +9% | solid |
| Delivered | 6,301 | 5,742 | +10% | solid |
| Bounce rate | 1.9% | 2.3% | -0.4 pts | solid |
| Positive replies | 61 | 44 | +39% | usable |
| Positives per 1k sent | 9.5 | 7.5 | +2.0 | usable |
| Positive reply rate | 0.97% | 0.77% | +0.20 pts | usable |
| Meetings | 0 | 0 | 0 | process gap |
| Opportunities | 3 | 2 | +1 | too early |

### Pipeline (CRM, as of 2026-08-03)
| Status | Count | Amount |
|---|---:|---:|
| Won | 2 | 14,400 |
| Lost | 5 | 31,000 |
| Open | 11 | 88,500 |

### Owners (positives per 1k sent; team median: 8.1)
| Owner | Sent | Positives | Per 1k | vs median |
|---|---:|---:|---:|---|
| Owner A | 2,410 | 31 | 12.9 | above |
| Owner B | 2,050 | 17 | 8.3 | at |
| Owner C | 1,960 | 13 | 6.6 | below |

### Hypothesis progress
| ID | Status | Sample / minimum | Metric | Decision |
|---|---|---:|---|---|
| exp-2026-07-cost-framing | running | 2,438 / 2,000 | 11.3 vs 7.5 per 1k | crossed; routed to review-outreach |
| exp-2026-07-partner-replication | running | 620 / 1,000 | 9.7 per 1k | extend, re-check 08-14 |

### Data quality
- Provider reply rate uses unique leads; this report uses sends. Both stated, sends used.
- Meetings field has never been set by any owner; process gap, not a copy problem.

## Decisions needed
- Scale "Copper Finch partner angle" from 40 to 80 new contacts per day by 2026-08-06, depends on bounce staying below 2% for one more week.
- Retire the reminder follow-up permanently by 2026-08-06, depends on nothing; evidence in reports/outreach-2026-07-31.md.

## Risks
- Meetings at zero for three weeks with 61 positives this week: interested-to-meeting handoff has no owner.
- 4 senders below warm-up floor; capacity is 20% under plan.

## Next actions
- Owner B, 2026-08-05: define the interested-to-meeting handoff and how meetings are recorded.
- Operator, 2026-08-06: decide the partner-angle scale-up.
- Owner A, 2026-08-08: write the counter-hypothesis for scenario openers in the second paragraph.
```
