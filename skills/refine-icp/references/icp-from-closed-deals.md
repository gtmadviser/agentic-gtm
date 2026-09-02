# ICP from closed deals

The most reliable ICP evidence a startup owns is its own closed deals. This method turns a CRM export into ranked, labelled patterns without inventing scoring weights. It is the analytical core of `refine-icp` and reads the output of `gtm review pipeline`.

## 1. Cohorts

Build three cohorts and never mix them:

| Cohort | Definition | Used for |
|---|---|---|
| Won | deals in a confirmed won stage, closed after `analysis_start_date` | fit patterns |
| Lost | deals in a confirmed lost stage, closed after `analysis_start_date` | failure patterns and loss reasons |
| Open | every other deal in scope | pipeline health only; never fit evidence |

The stage IDs come from the confirmed field map (`inspect-crm`). If the CRM has more than one pipeline, decide per pipeline whether it is in scope. Self-serve and sales-assisted pipelines usually need separate cuts.

## 2. Two views

Compute every cut twice:

- **Deal view**: one row per deal.
- **Unique-account view**: one row per account, using the account's first closed outcome (or its best outcome, stated explicitly).

A pattern that appears only in the deal view is usually one customer buying many times. Report both and call a pattern repeatable only when it holds in both.

## 3. Dimensions to cut

| Dimension | Typical field | Why it might be causal |
|---|---|---|
| Employee band | company employees | buying committee size, procurement complexity |
| Geography | company country | market maturity, language, legal constraints |
| Industry or subvertical | company industry | whether the pain exists at all |
| Funding stage | enrichment | budget freedom, urgency to build |
| Founding year | enrichment | greenfield stack versus entrenched tooling |
| Tech signals | enrichment, website | the product's technical precondition |
| Social following | enrichment | a cheap maturity proxy: larger followings tend to mean longer cycles |
| Deal source | CRM source field | which channel produces winnable deals |
| Buyer title | contact title | who actually decides |
| Previous tool | CRM free text | the switching trigger |

Use bands, not raw values. Suggested employee bands: 1 to 10, 11 to 50, 51 to 200, 201 to 500, 501 to 2,000, over 2,000. Adjust to the business, then keep the bands fixed across versions so results stay comparable.

## 4. Per-cut metrics

For every band within a dimension:

- `n_closed` = won + lost
- `win_rate` = won / n_closed
- `revenue_share` = won value in band / total won value
- `median_cycle_days` (create date to close date, won deals only)
- `coverage` = share of closed deals with a non-empty value for this dimension

Confidence label by `n_closed`:

| n_closed | Label | Allowed use |
|---|---|---|
| under 10 | insufficient | note only |
| 10 to 19 | directional | needs a second source before it becomes a rule |
| 20 or more | supported | can support a rule on its own |

Report coverage next to every table. A dimension with coverage under 70 percent is directional at best, whatever the n.

## 5. Ranking predictors

1. For each dimension, compute the spread: best band win rate minus worst band win rate, considering only bands with `n_closed` of 10 or more.
2. Sort dimensions by spread.
3. For the top three, write the causal sentence: "Companies with X win more often because Y." If the sentence does not survive a sceptical reading, the dimension is a proxy.
4. Check observability: can a sourcing provider filter on it, or does it need enrichment, or is it only knowable in a call?

A single strong, observable, causal predictor beats five weak ones. Prefer it as the primary filter and keep the others as tie-breakers.

## 6. Loss reasons and previous tools

Group the loss-reason field into at most eight buckets. Report each bucket with n and the share of lost value. Do the same for the "previous tool" or "current solution" field on won deals; this is the raw material for triggers and copy angles.

## 7. Fictional worked table

Company: Northstar Relay (`northstar-relay.example`), a workflow-coordination tool for engineering teams. Analysis start 2024-01-01. 62 won, 48 lost, 110 closed, 39 open. All figures invented.

**Employee band (coverage 91 percent)**

| Band | Won | Lost | n_closed | Win rate | Revenue share | Label |
|---|---:|---:|---:|---:|---:|---|
| 1 to 10 | 9 | 4 | 13 | 69 % | 6 % | directional |
| 11 to 50 | 31 | 12 | 43 | 72 % | 41 % | supported |
| 51 to 200 | 16 | 13 | 29 | 55 % | 34 % | supported |
| 201 to 500 | 4 | 9 | 13 | 31 % | 12 % | directional |
| over 500 | 2 | 10 | 12 | 17 % | 7 % | directional |

**Geography (coverage 98 percent)**

| Band | Won | Lost | n_closed | Win rate | Revenue share | Label |
|---|---:|---:|---:|---:|---:|---|
| Home market | 40 | 14 | 54 | 74 % | 58 % | supported |
| Neighbouring markets | 15 | 12 | 27 | 56 % | 27 % | supported |
| Overseas | 7 | 22 | 29 | 24 % | 15 % | supported |

**Reading**: the declared belief said "200 to 2,000 employees, overseas first". The data says 11 to 200 employees in the home and neighbouring markets. Spread for employee band is 55 points; for geography 50 points. Both have a causal story (committee size; language and reference density). Both are observable at sourcing time. Decision proposed: adopt the observed bands, keep "over 500 employees overseas" as a transfer hypothesis for a later experiment.

**Unique-account check**: 110 closed deals map to 97 accounts. The 11 to 50 band keeps a 70 percent win rate at account level; the 1 to 10 band drops to 58 percent because two accounts bought three times each. The 1 to 10 band is therefore not promoted.

## 8. What goes where

- Git (`market/icp.md`, `reports/`): the tables above, the reading, the decision.
- Store: the underlying `opportunities` and `accounts` rows.
- Nowhere: customer names next to outcomes, unless approved for Git as public references.
