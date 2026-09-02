# Won / lost / open analysis

This is the outline `gtm review pipeline` follows and the shape of the tables it writes to `reports/pipeline-<date>.md`. Use it to read the report correctly and to know what is missing when a section is empty.

## Order of sections

1. Coverage
2. Cohorts
3. Value and velocity
4. Cuts by dimension
5. Unique-account view
6. Loss reasons
7. Open pipeline
8. Limitations
9. Interpretation (human-written)
10. Owners and next actions (human-written)

Read them in this order. Coverage before patterns, always.

## 1. Coverage

| Field | Semantic | Fill rate | Notes |
|---|---|---:|---|
| amount | deal value | 96 % | |
| closedate | close date | 100 % won, 71 % lost | lost deals often closed without a date |
| industry | company industry | 63 % | two overlapping picklists |

Rule of thumb: a dimension under 70 percent fill is directional whatever its n.

## 2. Cohorts

| Cohort | Deals | Unique accounts | Total value | Median value |
|---|---:|---:|---:|---:|
| Won | | | | |
| Lost | | | | |
| Open | | | | |

Only won and lost are closed. Open is reported for health, never for fit.

## 3. Value and velocity (won deals)

| Metric | Value |
|---|---:|
| Median deal value | |
| P25 / P75 deal value | |
| Median cycle (create to close, days) | |
| P25 / P75 cycle | |
| Win rate (won / closed) | |

State the reporting currency and the conversion rule if more than one currency exists.

## 4. Cuts by dimension

One table per confirmed dimension, bands fixed across versions.

| Band | Won | Lost | n_closed | Win rate | Won value share | Median cycle | Label |
|---|---:|---:|---:|---:|---:|---:|---|

Label by `n_closed`: under 10 `insufficient`, 10 to 19 `directional`, 20 or more `supported`. Dimensions to expect when the fields exist: employee band, country, industry, deal source, owner, previous tool, buyer title band, funding stage and founding year if enriched.

## 5. Unique-account view

Repeat the cohort and top-dimension tables with one row per account. Note the rule used to pick the account's outcome (first closed deal by default). A pattern is repeatable only if it holds here too.

## 6. Loss reasons

| Reason bucket | Lost deals | Lost value | Share of lost value |
|---|---:|---:|---:|

At most eight buckets. Keep the free-text mapping in the store, not in Git.

## 7. Open pipeline

| Stage | Deals | Value | Median age (days) | Oldest (days) |
|---|---:|---:|---:|---:|

Flag stages where median age exceeds twice the won median cycle. This is a hygiene signal, not ICP evidence.

## 8. Limitations

Bullet list. Every excluded pipeline, unconfirmed field, short window, missing enrichment, and known data-entry habit. Written by the skill, not by the CLI.

## 9. Interpretation

Human-written. Separate observation from causal reading. Every claim cites a table and its label. No claim built on an `insufficient` cut.

## 10. Owners and next actions

One owner and one due date per action. Typical actions: confirm an ambiguous stage, backfill loss reasons, enrich a dimension, run `refine-icp`.

## Reading rules

- A high win rate with few lost deals means lost deals are not recorded, not that the team never loses.
- A segment that only wins small deals may be a self-serve segment. Check value share, not only win rate.
- A short median cycle in one geography often reflects language and reference density, which is a causal story worth writing down.
- Open pipeline concentrated in one stage means a process gap. Report it to the operator; do not include it in fit evidence.
