# Hypothesis register

`experiments/README.md` is the register. One line per experiment. The files hold the detail.

## Register format

```markdown
# Experiments

| ID | Title | Status | Result | Owner | Review date | Notes |
|---|---|---|---|---|---|---|
| exp-2026-08-cost-framing-opener | Cost framing vs scenario opener | running | pending | Operator | 2026-08-28 | matched arms, same senders |
| exp-2026-07-partner-replication | Replicate partner angle to new segment | complete | won | Operator | 2026-07-31 | reports/outreach-2026-07-31.md |
| exp-2026-06-reminder-followup | Reminder follow-up as step 2 | complete | lost | Operator | 2026-06-30 | anti-learning logged |
| exp-2026-05-event-bulk-email | Bulk email to an event list without a warm anchor | complete | abandoned | Operator | 2026-05-20 | audience unreachable |
```

## Lifecycle

| Contract status | Result label | Meaning |
|---|---|---|
| `draft` | pending | Written, not approved |
| `approved` | pending | Approved by the operator, no campaign yet |
| `running` | pending | Campaign live and accumulating sends |
| `complete` | `won` | Metric crossed the rule in the predicted direction at the required certainty; learning promoted |
| `complete` | `lost` | Metric crossed the rule in the opposite direction, or sample was sufficient and the effect was absent; anti-learning promoted |
| `complete` | `abandoned` | Never ran, or conditions changed; one-line reason recorded |

## Rules

1. One hypothesis per file. A second "if, then" is a second file.
2. The decision rule is written before results exist. "2 times positives per 1k with 500 or more sends per arm" is a rule. "We will see" is not.
3. Closing an experiment never edits its history. Add the results section, set the status and result, then add one line to the learnings log.
4. Any change to rule, denominator, window, or sample creates a new version file that names the old one. Both stay in the register.
5. A counter-hypothesis cites the learning it challenges in its header and in the register notes.
6. Experiments in `draft` or `approved` for more than 30 days are launched or abandoned at the monthly sweep.
7. No two running experiments share the same audience and variable.

## Seeding

At each monthly review, open 2 to 4 hypotheses from the strongest open questions in the learnings log and the "Next hypotheses" section of recent reviews. Prefer replications of winners into new segments, then single-variable copy tests on the best channel, then channel tests for untested segments.
