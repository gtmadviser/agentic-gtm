# Competitor profile template

One file per alternative under `market/competitors/<slug>.md`. The profile compares on six dimensions and always contains an honest strengths section. Feature lists are not a dimension; features change every quarter, structure does not.

```markdown
# <Alternative name>

Last verified: YYYY-MM-DD
Priority: primary | secondary | watch | adjacent
Bucket: direct competitor | substitute | internal workaround | do nothing
Sources: S-nnn, S-nnn (see market/sources.md)

## Quick take

Two sentences. Who they are for and why they win when they win.

## Strengths

Written as their best seller would write it. Three to five lines. Each with a source.

## Comparison

| Dimension | Them | Us | Evidence (source, date, claim or observation) |
|---|---|---|---|
| Buyer | who signs and who champions | | |
| Job | the job the buyer hires the product for | | |
| Workflow | how it fits the day-to-day; setup effort; what it replaces | | |
| Proof | public references, benchmarks, certifications | | |
| Commercial model | pricing basis, contract terms, minimums, trial | | |
| Tradeoffs | what a buyer gives up choosing them; what they give up choosing us | | |

## Structural differences

Two or three differences that do not change quarter to quarter (architecture, data ownership, delivery model, market focus). Each with a source.

## Where they win against us

From loss reasons in aggregate. Cohort and n from the pipeline report.

## Where we win against them

From won-deal previous-tool patterns in aggregate. Cohort and n.

## Questions a seller can ask

Four questions that surface the tradeoffs without naming the competitor unprompted.

## What to avoid

Framings that lose (for example price-only comparisons, feature-count arguments, unprompted attacks).

## Open questions

| Question | Owner | Due |
|---|---|---|
```

## Fictional example (abridged)

```markdown
# Harbor Sync

Last verified: 2026-09-01
Priority: primary
Bucket: direct competitor
Sources: S-011, S-012, S-014

## Quick take

Harbor Sync sells on-call coordination to platform teams at companies with more than 500 engineers. It wins on breadth and on procurement comfort.

## Strengths

- Broadest integration catalogue in the category (pricing page and docs, S-011, 2026-09-01, observation).
- Enterprise references on the public customers page (S-012, 2026-09-01, observation).
- Annual contracts with volume discounts, which large buyers prefer (S-011, claim).

## Comparison

| Dimension | Them | Us | Evidence |
|---|---|---|---|
| Buyer | VP Platform, procurement involved | engineering lead, owner-led decision | S-012 observation; own pipeline report 2026-08-22 |
| Job | standardise on-call across many teams | fix handoffs inside one or two teams | S-011 claim; own won-deal notes aggregate |
| Workflow | weeks of rollout, admin-managed | same-day setup by the team itself | S-014 review with date, observation |
| Proof | large logos | small-team references, none public yet | S-012; decision D-002 |
| Commercial model | annual, seat minimums | monthly, no minimum | S-011 observation |
| Tradeoffs | slow to start, admin overhead | fewer integrations | S-014; own limitations |
```

All names, sources, and facts are invented.

## Rules

- `Last verified` is the date someone looked at the sources, not the date the file was edited.
- A profile older than 12 months is `stale` until re-verified.
- Aggregates from your own pipeline may appear (cohort and n). Customer names may not.
- Anything learned under confidentiality stays out of the file.
