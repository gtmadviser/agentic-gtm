# Routing table

`gtm --json next` returns `stages[]` in this order. The first stage with `done: false` is current. Supporting skills run at any time.

## The chain

| Stage | Skill | Inputs that must exist | Done looks like | Typical trap |
|---|---|---|---|---|
| context | `onboard-company-brain` | a person who knows the company | `context/company.md` with product, customers, positioning, constraints, stack, owners, missing evidence, each statement labelled | writing beliefs as facts |
| icp | `refine-icp` | `context/company.md`, best and worst customers, any CRM evidence | `market/icp.md` with declared belief, observed evidence, anti-ICP, and an approved working definition with confidence per criterion | proxy criteria such as headcount with no causal link |
| crm (optional) | `inspect-crm` | `providers.crm` in `gtm.yaml`, credentials | field map confirmed by a human, `gtm sync crm` completed, won, lost, and open analysed separately | analysing before the field map is confirmed |
| experiment | `design-gtm-experiment` | approved ICP, evidence | `experiments/<slug>.json` with hypothesis, audience, trigger, channel, denominator, minimum sample, safeguards, decision rule, owner, status `approved` | writing the decision rule after seeing results |
| audience | `source-tam` then `research-accounts` | approved experiment, suppressions | `usable` list in the store, `market/tam.md`, `reports/sourcing-<date>.md`, priority list with fit and urgency | expanding a query before a 25-row probe passes |
| copy | `write-outreach` then `stage-campaign` (draft) | priority list, personalization variables, approved angle | `campaigns/<slug>.json` draft with steps, variants each with a hypothesis, suppressions, `status: paused` | more than one angle per message |
| plan | `stage-campaign` (plan) | draft file | `gtm campaign plan` returns a plan id, hash, expiry; operator has reviewed targets and payload summary | treating the plan as approval |
| applied | `stage-campaign` (apply) | reviewed plan id, explicit approval | `gtm campaign apply --plan <id>` verified paused in the provider; plan and result reference recorded | anyone activating in the provider UI |
| review | `review-outreach`, `weekly-gtm-review` | synced campaigns or imported metrics, the preregistered decision rule | `reports/outreach-<date>.md` comparing results with the unchanged rule; decisions with owners | judging on opens or on a changed denominator |

## Supporting skills

| Skill | When | Gate |
|---|---|---|
| `map-market` | before or during ICP work, or when positioning is questioned | none, research only |
| `audit-deliverability` | before the first list is built and before every launch | none, read-only; findings can block a launch |
| `advance-deals` | any active opportunity | none, drafts only |
| `handover-gtm-engine` | when an operator changes or an engagement ends | none, documentation |

## Approval gates, in order of appearance

1. Field-map confirmation before any CRM pull.
2. Credit plan before any paid sourcing or enrichment call.
3. Experiment approval before any audience is built.
4. Campaign plan review before apply.
5. Explicit apply command with the exact plan id.
6. Report publication approval before any Slack post.

Kickoff names the gate, then stops. The operator's reply is the approval.
