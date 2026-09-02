# Company brief template

Copy the block into `context/company.md`. Every line carries a label in square brackets, a source ID from `context/sources.md`, and a date. Keep bracketed prompts in place when a fact is unknown.

Labels: `[belief]` declared belief, `[evidence]` observed evidence, `[hypothesis]`, `[decision]`.

```markdown
# Company context

Status: draft | reviewed
Last reviewed: [YYYY-MM-DD]
Owner: [role]

## Product

- What it is, in one sentence: [text] [label] (S-001, YYYY-MM-DD)
- What changes for the customer: [outcome] [label] (S-, date)
- Technical or operational precondition to use it: [text] [label] (S-, date)

## Who it is for

- Declared target: [segment, size band, geography] [belief] (S-, date)
- Buying committee: [decides, uses, blocks] [label] (S-, date)
- Link: `market/icp.md`

## Business model

- Pricing model: [text] [label] (S-, date)
- Typical contract value and term: [value or [unknown]] [label] (S-, date)
- Sales motion: [self-serve, sales-assisted, partner] [label] (S-, date)

## Current customers

- Count and segment mix: [figure or [unknown]] [label] (S-, date)
- Public references approved for Git: [names or none] [decision] (S-, date)
- Churn or expansion pattern: [text or [unknown]] [label] (S-, date)

## Positioning

- One-line positioning: [text] [belief] (S-, date)
- Alternatives customers compare against: [list] [label] (S-, date)
- Proof available (case studies, benchmarks, certifications): [list] [evidence] (S-, date)

## Constraints

- Legal, compliance, regional: [text] [label] (S-, date)
- Budget and time: [text] [label] (S-, date)
- Brand and tone limits: [text] [decision] (S-, date)

## GTM stack and owners

| Function | Tool | Owner (role) | Configured in gtm.yaml |
|---|---|---|---|
| CRM | | | yes / no |
| Sourcing | | | yes / no |
| Sequencer | | | yes / no |
| Collaboration | | | yes / no |
| Data store | | | yes / no |

## Goals

- Next 90 days: [measurable goal] [decision] (S-, date)
- Owner of the goal: [role]

## Missing evidence

| Fact | Why it matters | Next action | Owner | Due |
|---|---|---|---|---|
| | | | | |
```

## Fictional filled fragment

```markdown
## Product

- What it is, in one sentence: Northstar Relay coordinates handoffs between engineering teams that share on-call duty. [evidence] (S-001, 2026-08-20)
- What changes for the customer: fewer missed handoffs; the founders quote "half the pages" but no customer figure exists yet. [belief] (S-002, 2026-08-20)
- Technical precondition: teams already run a paging tool with an API. [evidence] (S-001, 2026-08-20)

## Current customers

- Count and segment mix: 14 paying teams, mostly 11 to 50 engineers, home market. [evidence] (S-003, 2026-08-22)
- Public references approved for Git: none yet. [decision] (S-004, 2026-08-22)
```

## Writing rules

- One fact per line. Long explanations go into a linked file.
- A number without a source is written `[unknown]`, not estimated.
- When a fact changes, keep the old line, prefix it with `superseded YYYY-MM-DD:` and add the new line below.
- The stack table must match `providers` in `gtm.yaml`, or the mismatch is listed under missing evidence.
