# Experiment template

Two files per experiment. The JSON carries only the contract fields the CLI validates. The Markdown twin carries the full design and, later, the results.

## JSON: `experiments/<id>.json`

Fields match the `Experiment` contract exactly. No extra keys.

```json
{
  "name": "exp-2026-08-cost-framing-opener",
  "audience": "Engineering leaders at B2B software companies with 20 to 200 employees in DACH, excluding customers, open opportunities, competitors, and contacts touched in the last 60 days",
  "trigger": "Posted a platform or SRE role in the last 30 days",
  "channel": "email, two steps, 3-day gap",
  "hypothesis": "If the opener names the cost of the problem instead of describing a scenario, positives per 1k sent will be at least 1.5 times the scenario variant within 21 days, because cost framing gives the reader a reason to act now.",
  "denominator": "sent",
  "safeguards": [
    "maximum 40 new contacts per day",
    "pause if bounce rate exceeds 2% overall or 5% for any sender",
    "pause if hostile replies exceed 0.3% or unsubscribes exceed 2% of delivered",
    "suppress opt-outs, customers, open opportunities, competitors",
    "60-day re-approach window",
    "explicit opt-out line in every step"
  ],
  "decision_rule": "Continue with the cost opener if positives per 1k >= 1.5x scenario with >= 1,000 sends per arm by 2026-08-28; change one variable if between 0.75x and 1.5x; stop the cost opener if < 0.75x at usable certainty.",
  "owner": "Operator name",
  "status": "draft"
}
```

Status values: `draft` (written, not approved), `approved` (operator approved, not launched), `running` (campaign live), `complete` (closed by `review-outreach`).

## Markdown twin: `experiments/<id>.md`

```markdown
# exp-2026-08-cost-framing-opener, cost framing versus scenario opener

Status: draft | Result: pending | Owner: Operator name | Review date: 2026-08-28
Version: 1 | Supersedes: none | Counter-hypothesis to: none

## Belief tested
Declared belief that scenario openers outperform every other opener. Origin: inherited from an earlier engagement, never isolated here.

## Hypothesis
If the opener names the cost of the problem instead of describing a scenario, positives per 1k sent will be at least 1.5 times the scenario variant within 21 days, because cost framing gives the reader a reason to act now.

## Audience
Inclusion: engineering leaders, B2B software, 20 to 200 employees, DACH.
Exclusions: customers, open opportunities, competitors, contacts touched in the last 60 days, anti-ICP per market/icp.md.

## Trigger, channel, unit
Trigger: platform or SRE role posted in the last 30 days.
Channel: email, two steps, 3-day gap, same sender pool for both arms.
Unit of analysis: send.

## Metric
Primary: positives per 1k sent. Numerator: positive_interested + positive_soft + positive_referral. Denominator: sent.
Supporting: meetings per 1k, opportunities per 1k with a 30-day attribution window.
Not used: opens.

## Sample and window
Minimum 1,000 sends per arm (see sample-sizes.md, 1% vs 1.5% at directional power). Window: 2026-08-07 to 2026-08-28.

## Constants and confounders
Constant: list source, sender pool, schedule, step two, call to action, personalization tier.
Confounders: seasonal holiday period in week 2; read results per week as well as in total.

## Safeguards
See JSON. Trip action for each: pause the campaign and open an incident note in the weekly review.

## Decision rule
Continue if positives per 1k (cost) >= 1.5 x positives per 1k (scenario) with >= 1,000 sends per arm by 2026-08-28.
Change one variable if the ratio is between 0.75 and 1.5.
Stop the cost opener if the ratio is < 0.75 at usable certainty.

## Versions
v1 2026-08-05 initial.

## Results
Filled by review-outreach. Result label: won | lost | abandoned. Evidence: reports/outreach-<date>.md.
```

## Naming

`exp-<YYYY-MM>-<slug>`. Slug is lowercase, hyphenated, and names the variable, not the campaign. Versions append `-v2`. Replications append `-rep-<segment>`.
