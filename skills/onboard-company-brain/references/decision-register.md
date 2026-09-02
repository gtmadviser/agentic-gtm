# Decision register

`strategy/decisions.md` is the living operational source of truth for choices. It separates four things that are usually mixed: decisions someone owns, assumptions the team works with, conflicts nobody has resolved, and items that are simply open. A working assumption is never treated as a decision without a stakeholder confirming it.

## File layout

```markdown
# Decisions

Last updated: YYYY-MM-DD

## Decisions

| ID | Date | Decision | Owner | Supersedes | Source |
|---|---|---|---|---|---|

## Working assumptions

| ID | Assumption | Why we work with it | To be confirmed by | Since |
|---|---|---|---|---|

## Conflicts

| ID | Statement A (source, date) | Statement B (source, date) | Resolver | Status |
|---|---|---|---|---|

## Unresolved

| ID | Question | Blocks | Owner | Due |
|---|---|---|---|---|
```

IDs: `D-001` decisions, `A-001` assumptions, `C-001` conflicts, `U-001` unresolved. Never reuse an ID.

## Rules

1. The latest explicit stakeholder decision outranks older notes, decks, and proposals. Write the date; the date settles precedence.
2. An assumption moves to Decisions only when the named confirmer says so. Record that as a new decision row with `Supersedes: A-nnn`.
3. A conflict stays in the Conflicts table until the resolver decides. Then a decision row is added and the conflict row gets `Status: resolved by D-nnn`.
4. Inconsistent numbers (two dashboards, two headcounts) are conflicts, not rounding errors. Log both.
5. Historical action items from old documents are not open items. If they were done, say when.
6. Every decision row has an owner who can be asked about it. "The team" is not an owner.
7. Decisions about the ICP also update `Status`, `Version`, and `Supersedes` in `market/icp.md`.

## Fictional example

```markdown
## Decisions

| ID | Date | Decision | Owner | Supersedes | Source |
|---|---|---|---|---|---|
| D-001 | 2026-08-22 | Target owner-led teams of 11 to 50 engineers in the home market for the first outbound experiment | Head of Growth | none | S-004 |
| D-002 | 2026-08-29 | No customer names in Git until the reference programme is signed | CEO | none | S-006 |

## Working assumptions

| ID | Assumption | Why we work with it | To be confirmed by | Since |
|---|---|---|---|---|
| A-001 | The paging-tool API is the technical precondition | Both founders say so; no lost deal has contradicted it | Head of Product | 2026-08-20 |

## Conflicts

| ID | Statement A (source, date) | Statement B (source, date) | Resolver | Status |
|---|---|---|---|---|
| C-001 | "We sell to platform teams" (S-002, 2026-08-20) | Closed deals are mostly product teams (S-003, 2026-08-22) | CEO | open, routed to refine-icp |

## Unresolved

| ID | Question | Blocks | Owner | Due |
|---|---|---|---|---|
| U-001 | Which pipeline holds self-serve deals? | inspect-crm | Revenue Ops | 2026-09-05 |
```

## Update procedure when a stakeholder decision changes

1. Add the decision row with date, owner, and what it supersedes.
2. Update `context/company.md` if the executive summary changes; mark the old line superseded.
3. Update `market/icp.md` if the decision touches targeting.
4. Add the new source and date to `context/sources.md`.
