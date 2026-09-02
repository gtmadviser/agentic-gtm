# ICP template

Copy the block below into `market/icp.md`. Keep the four sections and their order. Replace bracketed prompts; leave a prompt in place if the fact is unknown so the gap stays visible.

```markdown
# Working ICP

Status: draft
Version: 1
Approved by: [name and role, or empty]
Approved on: [YYYY-MM-DD, or empty]
Supersedes: [version, or none]

## Declared belief

Written on [YYYY-MM-DD] before evidence was reviewed. Do not edit; append dated entries.

| Dimension | Belief | Source | Confidence | Disqualifier |
|---|---|---|---|---|
| Geography | | | | |
| Industry or subvertical | | | | |
| Company size | | | | |
| Technical or operating precondition | | | | |
| Trigger (why now) | | | | |
| Buyer and champion | | | | |
| Minimum economic value | | | | |

## Observed evidence

Aggregates only. One row per material pattern. Types: CRM evidence, stakeholder judgment, unvalidated assumption.

| ID | Claim | Type | Cohort and n | Deal-level result | Account-level result | Coverage | Confidence | Source |
|---|---|---|---|---|---|---|---|---|
| E-001 | | | | | | | | |

Contradictions with the declared belief:

- [belief] vs [evidence ID]: [proposed change], decision owner [name], status [open or decided on date]

## Exclusions and anti-ICP

Hard exclusions (each maps to a filter or suppression list):

| Pattern | Failure mode observed | Evidence ID | Filter or list |
|---|---|---|---|
| | | | |

Worth testing before excluding:

| Pattern | Why it might fail | Proposed test |
|---|---|---|
| | | |

## Approved working definition

Inclusion rules (every line carries confidence and evidence IDs):

| Criterion | Rule | Confidence | Evidence |
|---|---|---|---|
| Company | | | |
| Problem | | | |
| Trigger | | | |
| Stakeholder | | | |
| Buying constraints | | | |

Disqualifiers: [list, each with evidence ID]

Unresolved hypotheses (not part of the definition):

- [hypothesis], test via [experiment name or "none yet"]

## Sourcing filters

The literal filter set implied by the approved definition. `source-tam` uses this verbatim.

- Employee band: [ ]
- Geography: [ ]
- Industry codes or keywords: [ ]
- Technical precondition: [ ]
- Trigger signal and window: [ ]
- Titles: [ ]
- Suppress: existing customers, competitors, [lists]
```

## Editing rules

- Bump `Version` on every approved change; write the supersession in `strategy/decisions.md`.
- Keep the declared belief table frozen; append dated rows for new beliefs.
- Evidence IDs are never reused. Retire a row by adding `retired on [date]` to its claim.
- Customer names appear here only if approved for Git as public references.
