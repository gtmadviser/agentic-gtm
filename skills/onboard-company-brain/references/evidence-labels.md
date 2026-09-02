# Evidence labels

Four labels, applied to every statement in `context/company.md`, `market/icp.md`, and every report. They exist so that nobody downstream mistakes a hope for a fact.

| Label | Meaning | Test | Typical source |
|---|---|---|---|
| declared belief | What a stakeholder thinks is true | Would this person say it without looking at data? | founder interview, pitch deck, strategy memo |
| observed evidence | What a measured source shows | Can you point to the table, cohort, or document and its date? | CRM report, experiment result, support log, public filing |
| hypothesis | A claim proposed for testing | Is there a way to disconfirm it? | best/worst-customer trick, a new segment idea, a copy angle |
| decision | A choice someone owns | Is there an owner and a date? | decision register |

## Applying the labels

- One label per statement. A sentence that needs two labels is two statements.
- Evidence always carries n, coverage, and a date when it is quantitative.
- A belief held by the whole leadership team is still a belief.
- A hypothesis without a proposed test is a belief in disguise. Add the test or relabel.
- A decision without an owner is an assumption. Move it to the assumptions table.

## Promotion and demotion

| From | To | Requires |
|---|---|---|
| belief | hypothesis | a stated disconfirming test |
| hypothesis | evidence | a closed experiment or a measured cohort with a label of at least `directional` |
| evidence | decision | a named owner choosing to act on it, logged with a date |
| any | superseded | a newer dated statement; the old one stays visible |

Nothing is promoted by repetition or seniority.

## Wording

Write the label in square brackets at the end of the line, then the source ID and date:

`- Sales cycles are shorter in the home market. [evidence] (S-003, 2026-08-22)`

`- Platform teams are the buyer. [belief] (S-002, 2026-08-20)`

`- A new engineering hire in the deciding role is the trigger. [hypothesis] (S-005, 2026-08-25)`

`- First experiment targets the home market only. [decision] (D-001, 2026-08-22)`

## Common errors

- Labelling a customer quote as evidence for a market-wide claim. It is evidence that one customer said it.
- Labelling a competitor's marketing claim as evidence. It is a claim; see `map-market`.
- Labelling a CRM number as evidence when the field is under 70 percent filled. Say `directional` and give the coverage.
- Writing "we decided" without an owner. Ask who.
