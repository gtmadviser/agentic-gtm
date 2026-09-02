---
name: refine-icp
description: Turn declared ICP beliefs and observed commercial evidence into an approved working ICP and anti-ICP with confidence levels and evidence references. Use after onboarding, CRM analysis, interviews, or a finished experiment; do not use to source contacts before exclusions, confidence, and a named approval exist.
---

# Refine ICP

> The ICP is the contract between research and sourcing. This skill sits between Research and Source in the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate). It keeps four things apart that teams habitually blend: what the team believes, what the data shows, whom to exclude, and what has actually been approved for targeting. Every later stage (sourcing filters, copy angles, experiment audiences) may only read the approved definition.

## When to use / when not to

Use when:

- `context/company.md` exists and `market/icp.md` is empty, stale, or still a declared belief.
- `gtm review pipeline` produced a new report, or an experiment closed with a decision.
- A stakeholder proposes a new segment, geography, or persona.
- `gtm next` reports stage `icp` as not done.

Do not use when:

- No company context exists yet. Run `onboard-company-brain` first.
- You only want to source contacts. The approved definition already exists; run `source-tam`.
- You are asked to "quickly widen the ICP" to fill a campaign. That is a hypothesis, and it goes through `design-gtm-experiment`.

## Inputs

| Input | Where | What you take from it |
|---|---|---|
| Company brief | `context/company.md` | product, buyer, constraints, declared ICP |
| Current ICP file | `market/icp.md` | version, status, declared belief, prior evidence IDs |
| Pipeline review | `reports/pipeline-<date>.md`, `gtm --json review pipeline` | won / lost / open cuts, sample sizes, missingness |
| Market map | `market/*.md` | substitutes, competitor customers, category boundaries |
| Experiments | `experiments/*.json` | audience definitions and outcomes that already tested a criterion |
| Decisions | `strategy/decisions.md` | earlier approvals, supersessions, owners |
| Store | `opportunities`, `accounts` tables (Supabase or `.gtm/store/`) | aggregate cuts only; never copy rows into Git |

Run `gtm --json next` first. If stage `context` is not done, stop and route to `onboard-company-brain`.

## Procedure

1. **Freeze the declared belief before reading data.** If the `Declared belief` section of `market/icp.md` is empty, fill it from `context/company.md` and the stakeholder interview now. Date it. Once written, never edit it in place; add a new dated entry below it. The declared belief is a baseline, not a target.
2. **Collect observed evidence.** With a CRM connected, run `gtm --json review pipeline` and read the report. Without a CRM, gather interview notes, support tickets, churn reasons, and closed experiments. Label each item `CRM evidence`, `stakeholder judgment`, or `unvalidated assumption`. Give every item an ID (`E-001`, `E-002`, ...).
3. **Run the closed-deals cut.** Follow `references/icp-from-closed-deals.md`. Keep won, lost, and open separate. Cut by employee band, geography, industry, funding stage, founding year, tech signals, social following, deal source, and buyer title. For every cut, record n, win rate, revenue share, and the unique-account view. Attach a confidence label: fewer than 10 closed deals is `insufficient`, 10 to 19 is `directional`, 20 or more is `supported`.
4. **Find the strongest predictor.** Rank cuts by the spread between the best and worst band. For the top candidates, write one sentence explaining why the criterion would cause faster or more frequent wins. If you cannot write that sentence, the criterion is a proxy and stays a hypothesis. Check that the criterion is observable at sourcing time; a predictor you cannot filter on is a qualification question, not an ICP rule.
5. **Run the best/worst-customer trick.** Follow `references/best-worst-customer.md`. List three best-fit and three worst-fit customers. Describe the gap in plain language. Sharpen it to a WHO (company shape and role) plus a TRIGGER (the "why now" event). With no customers yet, borrow a competitor's most-loved public customers and mark the result `hypothesis`.
6. **Write exclusions and anti-ICP.** Separate hard exclusions (evidence-backed failure patterns, legal or compliance limits, existing customers, competitors) from segments worth testing. Every hard exclusion must be checkable with a sourcing filter or a suppression list.
7. **Draft the approved working definition.** Express fit across company, problem, trigger, stakeholder, buying constraints, and disqualifiers. Every material criterion carries a confidence level and at least one evidence ID. List unresolved hypotheses in their own block, outside the definition.
8. **Reconcile belief and evidence.** Where the data contradicts the declared belief, say so in one line, propose the change, and record it as a decision with an owner. Data wins by default, but the decision is a human's.
9. **Get approval.** Ask the accountable stakeholder to approve the definition. Write the approver, date, version, and the superseded version into `strategy/decisions.md`. Update `Status:` and `Version:` at the top of `market/icp.md`.
10. **Hand off.** Tell the operator which sourcing filters follow from the approved definition and which hypotheses need an experiment first. Run `gtm --json next`; the next stage should now read `crm` or `experiment`.

## Hard rules

1. `market/icp.md` keeps four separate sections: declared belief, observed evidence, exclusions and anti-ICP, approved working definition. Never merge them.
2. The declared belief is written before any evidence is read and is never edited retroactively.
3. Every criterion in the approved definition carries a confidence label and an evidence ID. A criterion without either is not allowed in the definition.
4. A cut with fewer than 10 closed deals never becomes a rule. Cuts with 10 to 19 are directional and need a second source. Cuts with 20 or more can support a rule on their own.
5. Won, lost, and open are never collapsed. Open pipeline is never evidence of fit.
6. A pattern must hold at deal level and at unique-account level. Repeat customers can fake a segment pattern.
7. Every criterion has a stated causal link to the problem the product solves. Headcount, industry, and funding stage are proxies until that link is written down.
8. Anti-ICP disqualifiers must be checkable at sourcing time (a filter, a list, or a field).
9. A hypothesis never becomes a targeting rule without either a closed experiment or a logged decision with an owner.
10. No numeric scoring weights before approval. Ranges and labels only.
11. A new geography, vertical, or persona starts as a transfer hypothesis. Historical patterns do not transfer by assumption.
12. Nothing person-level and no raw CRM rows go into Git. Aggregates, IDs of evidence items, and decisions only.

## Checklist

- [ ] `gtm --json next` shows stage `context` done.
- [ ] Declared belief section is filled and dated before evidence was read.
- [ ] Every evidence item has an ID, a type label, a source, a date, and n.
- [ ] Won / lost / open reported separately; unique-account view compared with deal view.
- [ ] Every cut carries `insufficient`, `directional`, or `supported`.
- [ ] Strongest predictor named, with its causal sentence and sourcing observability confirmed.
- [ ] Best/worst-customer gap written as WHO + TRIGGER.
- [ ] Hard exclusions separated from test-worthy exclusions; each hard exclusion maps to a filter or list.
- [ ] Approved definition: every criterion has confidence + evidence ID.
- [ ] Unresolved hypotheses listed outside the definition.
- [ ] Contradictions between belief and evidence stated as decisions with owners.
- [ ] Approver, date, version, superseded version logged in `strategy/decisions.md`.
- [ ] No customer names, contact data, or raw rows in Git.

## Output contract

| Artifact | Location | Rules |
|---|---|---|
| ICP file | `market/icp.md` | Header lines `Status: draft \| approved`, `Version: N`, `Approved by:`, `Approved on:`. Four fixed sections in the order above. Template in `references/icp-template.md`. |
| Decision entries | `strategy/decisions.md` | One line per approval or supersession: date, decision, owner, supersedes. |
| Evidence table | inside `market/icp.md`, section `Observed evidence` | Columns: ID, claim, type, cohort and n, deal-level result, account-level result, coverage, confidence, source. Aggregates only. |
| Cut tables | `reports/pipeline-<date>.md` (generated) | Read, do not edit. Reference by file name and section. |
| Sourcing handoff | last section of `market/icp.md`, `Sourcing filters` | The literal filter set the approved definition implies; used verbatim by `source-tam`. |
| Store | `evidence` table (optional) | Same rows as the evidence table, for teams that query across workspaces. |

Status semantics: `draft` means sourcing must not start. `approved` means `source-tam` may translate the `Sourcing filters` section into provider queries.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| The stated sweet spot has the worst win rate in the data | Declared belief came from aspiration or from the largest logo, not from closed deals | Record the contradiction as a decision; propose the observed band; keep the old band as a transfer hypothesis |
| A segment looks great with n = 6 | Small cohort or one repeat customer | Label `insufficient`; compare the unique-account view; wait for more closed deals or run an experiment |
| Industry field is 60 percent empty | CRM property never enforced | Report coverage; use a second source (enrichment, public data) for the cut; never impute |
| Criteria keep growing with each review | Adding every observed pattern as a rule | Keep the definition to the criteria with a causal link and `supported` confidence; park the rest as hypotheses |
| Sourcing returns nothing | Anti-ICP filters stacked with unverified criteria | Loosen one hypothesis-level criterion at a time; never drop a hard exclusion silently |
| Two stakeholders disagree on the target segment | Belief conflict, no evidence to settle it | Log the conflict in `strategy/decisions.md`; design an experiment; do not pick one silently |
| Open pipeline used to "prove" a segment works | Open deals mistaken for evidence | Remove from evidence; open deals inform only pipeline health |

## References

- [ICP from closed deals](./references/icp-from-closed-deals.md): the cut method, sample-size labels, and a fictional worked table.
- [Best/worst-customer trick](./references/best-worst-customer.md): the fastest way to a WHO + TRIGGER with few customers.
- [ICP template](./references/icp-template.md): the fill-in Markdown for `market/icp.md`.

Licensed CC BY 4.0 by GTM Adviser.
