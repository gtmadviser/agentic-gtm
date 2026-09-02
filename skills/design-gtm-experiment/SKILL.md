---
name: design-gtm-experiment
description: Preregister one falsifiable GTM experiment with audience, trigger, channel, hypothesis, denominator, minimum sample, safeguards, owner, and a continue/change/stop rule written before launch. Use before any new message, channel, offer, segment, or timing test; do not use for unmeasured activity lists or to backfill a rule after results exist.
---

# Design GTM Experiment

> This skill sits between ICP and Reach in the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate). It turns a belief into a test that can lose. Every campaign the engine stages belongs to exactly one experiment, and every experiment states its decision rule before the first send. Without this step, reviews become opinions and learnings become folklore.

## When to use / when not to

Use when:

- A new angle, opener, call to action, channel, segment, offer, sequence shape, or send timing is proposed.
- A learning in `strategy/learnings.md` is about to be contradicted. The contradiction needs a counter-hypothesis, not an exception.
- A winner is replicated into a new segment or country. Replication is an experiment with a tighter prior.
- The monthly review seeds next month's hypotheses.

Do not use when:

- Results already exist and someone wants a rule to fit them. Record the observation in the learnings log as "open question" instead.
- The proposal changes two or more variables at once. Split it.
- The audience cannot be sourced or the channel cannot be measured. Fix that first with `source-tam` or the metrics import.
- The request is a list of activities with no metric. That is a plan, not an experiment.

## Inputs

| Source | What it provides |
|---|---|
| `context/company.md` | Product, constraints, owners, what is already believed |
| `market/icp.md` | Approved working ICP and anti-ICP, exclusions |
| `strategy/learnings.md` | Validated learnings and anti-learnings the design must respect or explicitly challenge |
| `experiments/README.md` and `experiments/*.json` | Register of open and running experiments to avoid duplicate tests on the same audience |
| `reports/outreach-*.md`, `reports/retro/*.json` | Prior results, winners, anti-patterns, open ledger entries |
| `gtm --json review outreach` | Current baselines per channel for the decision rule |
| `gtm --json next` | Confirms the ICP stage is done before an experiment is drafted |

## Procedure

1. **Read before writing.** Load the company context, the approved ICP, the learnings log, and the register. If the proposal contradicts a validated learning, label the file a counter-hypothesis and cite the learning it challenges. If a running experiment already tests the same variable on the same audience, stop and extend that one.
2. **Name the belief.** Write one sentence describing what the team currently believes and where that belief came from (declared, observed, or inherited). The experiment exists to test this belief, not to confirm it.
3. **Write the hypothesis.** One sentence in the form "If we [change] for [audience], then [metric] will [move by amount] within [window], because [mechanism]." Reject any hypothesis that cannot lose.
4. **Fix the audience.** Define inclusion criteria that `source-tam` can execute, plus exclusions: anti-ICP, suppressed domains, contacts touched within the re-approach window, current customers, open opportunities, competitors.
5. **Fix trigger, channel, and unit of analysis.** State the trigger that puts a contact into scope, the single channel or fixed channel sequence, and whether the unit is the send, the contact, or the account.
6. **Choose the metric from the hierarchy.** Primary metric is the highest available in `review-outreach/references/kpi-hierarchy.md`: opportunities per 1k, then meetings per 1k, then positives per 1k. Reply rate is a primary metric only for deliverability tests. Opens are never a metric. Write the numerator, the denominator, and the attribution window.
7. **Compute the minimum sample.** Use `references/sample-sizes.md`. Record the number per arm and the total. If the audience cannot supply it within the window, shrink the claim or widen the audience; do not shrink the sample.
8. **Isolate one variable.** List everything that must stay constant: list source, sender pool, schedule, sequence length, call to action, personalization tier, and step position. Name the confounders you cannot control and how you will read the result in their presence.
9. **Set safeguards.** Daily new-contact cap, bounce and hostile thresholds, suppression sources, opt-out text, re-approach window, and any channel-specific limit. Each safeguard names the action taken when it trips.
10. **Write the decision rule.** Three explicit branches: continue if, change if, stop if, each with a metric, a value, a certainty tier, and a date. Write it before any campaign exists.
11. **Assign the owner and the review date.** One human owner. The review date is the earlier of the window end or the date the minimum sample is expected.
12. **Save and register.** Write `experiments/<id>.json` with the contract fields and status `draft`, plus the Markdown twin with the full design, using `references/experiment-template.md`. Add a line to `experiments/README.md`. Obtain the operator's approval and set status `approved` with the date in `strategy/decisions.md`. Only an approved experiment may proceed to `write-outreach` and `stage-campaign`.

## Hard rules

1. One hypothesis per file. A second "if, then" clause is a second file.
2. The decision rule, denominator, window, and minimum sample are written before launch and never edited. Any change creates a new version file that names the old one and the reason.
3. Minimum samples: 200 sends per arm before any reply rate is trusted, 500 per arm before variants are compared, 50 replies before a meeting or opportunity rate is trusted, 2,000 sends before a finding is called solid.
4. Cheap channel tests run 25 to 50 leads per variant to pick the channel, then the copy test runs at full sample on the chosen channel. Channel before copy.
5. Exactly one variable changes between arms. Sender pool, list, schedule, and sequence shape are held constant or the test is labelled observational.
6. The primary metric comes from the KPI hierarchy. Opens are prohibited as a metric; reply rate is allowed only for deliverability experiments.
7. Every safeguard names a threshold and the action when it trips. Minimum set: bounce above 2% pauses; hostile above 0.3% pauses; unsubscribe above 2% pauses; suppression of opt-outs, customers, open opportunities, and competitors; a daily cap on new contacts.
8. Every experiment has one owner and a review date. Team ownership is not allowed.
9. A proposal that contradicts a validated learning is filed as a counter-hypothesis and cites the learning. Silent contradiction is prohibited.
10. Status follows the contract: `draft`, `approved`, `running`, `complete`. The result label `won`, `lost`, or `abandoned` lives in the Markdown twin and is set only by `review-outreach` or the monthly sweep.
11. Experiment files contain no contact data, no provider IDs, and no reply text.

## Checklist

- [ ] Learnings log and register read; contradictions filed as counter-hypotheses
- [ ] Belief stated with its origin
- [ ] Hypothesis in "if, then, because" form and able to lose
- [ ] Audience inclusion and exclusion criteria executable by `source-tam`
- [ ] Trigger, channel, unit of analysis fixed
- [ ] Primary metric from the hierarchy with numerator, denominator, attribution window
- [ ] Minimum sample per arm computed and achievable within the window
- [ ] One variable; constants and confounders listed
- [ ] Safeguards with thresholds and actions
- [ ] Continue, change, stop rule with values, tiers, and a date
- [ ] One owner, one review date
- [ ] JSON with contract fields plus Markdown twin saved; register updated; approval logged

## Output contract

| Artifact | Location | Content |
|---|---|---|
| Experiment record | `experiments/<id>.json` | Contract fields only: `name`, `audience`, `trigger`, `channel`, `hypothesis`, `denominator`, `safeguards`, `decision_rule`, `owner`, `status` |
| Design twin | `experiments/<id>.md` | Belief, exclusions, unit, numerator, minimum sample, window, constants, confounders, rule branches, versions, results |
| Register | `experiments/README.md` | One line per experiment: id, title, status, owner, review date |
| Approval | `strategy/decisions.md` | Approval with owner and date; later, any version change |
| Learnings | `strategy/learnings.md` | Nothing at design time; entries are added only when the experiment closes |

`<id>` is `exp-<YYYY-MM>-<slug>`. Versions append `-v2`, `-v3`.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Hypothesis reads "we will see what happens" | No metric or value | Rewrite with a number and a direction |
| Minimum sample larger than the reachable audience | Claim too fine for the audience | Widen audience, lengthen window, or test a coarser variable |
| Two arms differ in sender pool or list | Variable not isolated | Relabel as observational or fix the constants |
| Reviewer asks to move the goal line after results | Rule written too loosely | Refuse; open a new version and keep both on record |
| Experiment sits in `approved` for more than 30 days | No launch owner or blocked audience | Monthly sweep sets `abandoned` with a reason or assigns a launch date |
| Proposal repeats an anti-learning | Learnings log not read | File as counter-hypothesis or drop |
| Opportunity-rate comparison on 400 sends per arm | Base rate too low for the sample | Switch primary metric to positives per 1k and note opportunities as supporting |
| Two experiments running on the same audience | Register not checked | Merge or sequence them; never run overlapping tests on one list |

## References

- [Experiment template, JSON and Markdown](./references/experiment-template.md)
- [Sample sizes](./references/sample-sizes.md)
- [Hypothesis register](./references/hypothesis-register.md)
- [Learnings log](./references/learnings-log.md)

Licensed CC BY 4.0 by GTM Adviser.
