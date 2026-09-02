---
name: onboard-company-brain
description: Capture or refresh a startup's product, customers, positioning, constraints, GTM stack, owners, decisions, and missing evidence, with every statement labelled as belief, evidence, hypothesis, or decision. Use for initial onboarding, company-context interviews, or when repository context is stale; do not use for market research or CRM analysis on their own.
---

# Onboard Company Brain

> Every other skill reads `context/company.md` first. If that file mixes what the founders hope with what the data shows, every downstream artifact inherits the confusion. This skill runs at the very start of the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate) and again whenever context goes stale. It interviews only for what is missing, labels every statement, keeps conflicts visible, and never invents a number.

## When to use / when not to

Use when:

- `gtm next` reports stage `context` as not done.
- A new workspace was created with `gtm init` and `context/company.md` still holds the template.
- A stakeholder decision changed scope, positioning, pricing, or ownership.
- The brief is older than 90 days, or a downstream skill found a contradiction it could not resolve.

Do not use when:

- The question is about competitors or category. That is `map-market`.
- The question is about which customers actually convert. That is `inspect-crm` and `refine-icp`.
- Someone wants marketing copy. This skill writes context, not copy.

## Inputs

| Input | Where | What you take from it |
|---|---|---|
| Operating contract | `OPERATING-CONTRACT.md` | evidence labels, Git versus store boundary |
| Existing brief | `context/company.md` | what is already known and dated |
| Sources | `context/sources.md` | which documents and people said what, when |
| Decisions | `strategy/decisions.md` | decisions, working assumptions, conflicts, unresolved items |
| ICP | `market/icp.md` | the declared belief, if any |
| Meetings | `meetings/*.md` | redacted notes with dates |
| Config | `gtm.yaml` | `company.name`, selected providers (the stack as configured) |
| Stage | `gtm --json next` | whether context is the blocking stage |

## Procedure

1. **Read everything that exists.** Load the files above. Build a gap list against the brief sections in `references/company-brief-template.md`: which sections are empty, which hold an unsourced number, which are older than 90 days.
2. **Interview only the gaps.** One question per gap, plain language, in the order of the template. Accept "unknown" and "we disagree" as answers; write them down as such. Never ask for a fact that is already sourced in the brief.
3. **Label every statement.** Use the four labels from `references/evidence-labels.md`: declared belief, observed evidence, hypothesis, decision. Every line in the brief carries a label, a source, and a date.
4. **Register the sources.** Every document, dashboard, person, or meeting used becomes a row in `context/sources.md` with a date and what it is authoritative for. Follow `references/source-register.md`.
5. **Record conflicts as conflicts.** When two sources disagree, write both statements, both sources, and the person who must resolve it into the `Conflicts` table of `strategy/decisions.md`. The latest explicit stakeholder decision wins by default; the older statement stays visible with its date. Never pick one silently.
6. **Write the brief.** Fill `context/company.md` from the template. Keep bracketed prompts where a fact is unknown so the gap stays visible. Keep the brief under roughly 150 lines; detail belongs in linked files.
7. **Update the decision register.** Material choices (positioning, target segment, pricing model, stack, ownership) go into `strategy/decisions.md` with owner and date. Working assumptions go into their own table and are not decisions until a stakeholder confirms them. Follow `references/decision-register.md`.
8. **Write the missing-evidence register.** In the last section of the brief, list every material fact that has no evidence, and name the next three evidence actions with an owner and a due date. Typical actions: confirm the CRM field map, pull closed deals, interview three customers, read the last quarter's churn reasons.
9. **Extract knowledge.** For every raw source read this session (transcript, thread, proposal, post), extract three to eight insight files into `context/knowledge/` using `references/knowledge-layer.md`: one claim per file, labelled, with source, date, confidence and status `emergent`. Check for near-duplicates first. Raw sources stay outside Git.
10. **Load context.** Walk `context/knowledge/`, report counts per category and status, load canonical and validated files, list emergent ones as unverified. Every downstream skill repeats this step before it writes anything.
11. **Check the stack.** Compare the tools the team named with `providers` in `gtm.yaml`. Note mismatches. Do not change `gtm.yaml` without the operator.
12. **Close the loop.** Run `gtm --json next`. Stage `context` should now be done. Summarise in ten bullets or fewer: product and value, business model, declared ICP, buying committee, motion, channels, proof, systems, constraints, ownership. Name the contradictions and the missing inputs that matter most for the next stage.

### Refresh procedure

Trigger a refresh when the brief is older than 90 days, when a stakeholder decision changes, or when a downstream skill flags a contradiction. Diff the current brief against the new information, re-interview only the changed areas, add the new source and date to `context/sources.md`, update the decision register first, then the brief, then any affected ICP entry.

## Hard rules

1. Every statement in the brief carries one of four labels, a source, and a date. No unlabelled lines.
2. No invented metrics, customer results, revenue figures, dates, headcounts, quotes, or case-study outcomes. A number without a source is written as `[unknown]`.
3. A declared ICP is never treated as observed evidence, whatever the seniority of the person who declared it.
4. A working assumption is not a decision until a named stakeholder confirms it. The register keeps them in separate tables.
5. Conflicts are recorded, never silently resolved. The resolver is named.
6. The latest explicit stakeholder decision outranks older notes, proposals, and decks. Historical action items are not open items.
7. Customer names appear in Git only when the operator confirms they are public references. Otherwise use segment descriptions.
8. Credentials, contact data, raw exports, provider IDs, and transcripts never enter Git. Meeting notes are redacted before they land in `meetings/`.
9. An NDA is not a data-processing agreement. Do not record third-party tools as approved for customer data because a contract exists.
10. The brief stays under roughly 150 lines. Detail goes into linked files under `context/` or `market/`.
11. Ask only for facts not already present. Re-asking a sourced fact is a defect.
12. Refresh, do not rewrite. Keep prior dated statements when a fact changes; mark them superseded.

## Checklist

- [ ] Gap list built against the template before the interview.
- [ ] Every brief line has a label, a source, and a date.
- [ ] `context/sources.md` lists every source used, with date and authority.
- [ ] Conflicts table updated with both statements and a resolver.
- [ ] Decisions table has owner and date on every row; assumptions kept separate.
- [ ] No number without a source; unknowns written as `[unknown]`.
- [ ] Missing-evidence register lists the next three actions with owners and dates.
- [ ] Stack in the brief compared with `providers` in `gtm.yaml`; mismatches noted.
- [ ] No customer names in Git without confirmation; no contact data, credentials, or transcripts.
- [ ] Ten-bullet summary delivered; contradictions and missing inputs named.
- [ ] `gtm --json next` shows stage `context` done.

## Output contract

| Artifact | Location | Rules |
|---|---|---|
| Company brief | `context/company.md` | Sections and order from `references/company-brief-template.md`. Header lines `Status`, `Last reviewed`, `Owner`. Labels on every line. |
| Knowledge layer | `context/knowledge/<category>--<slug>.md` | One insight per file with frontmatter (title, category, label, status, confidence, source, date_extracted, tags, references). Part of the Git-tracked company brain. Format in `references/knowledge-layer.md`. |
| Source register | `context/sources.md` | One row per source: ID, type, title, date, authoritative for, location (not the content). |
| Decision register | `strategy/decisions.md` | Four tables: Decisions, Working assumptions, Conflicts, Unresolved. Format in `references/decision-register.md`. |
| Missing-evidence register | last section of `context/company.md` | Fact, why it matters, next action, owner, due date. |
| Meeting notes | `meetings/<YYYY-MM-DD>-<topic>.md` | Redacted. Attendees by role. Decisions copied into the register the same day. |
| Config | `gtm.yaml` `company.name` | Only the company name; provider selection stays with the operator. |

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| The brief reads like a pitch deck | Beliefs written as facts | Relabel each line; move claims without evidence to hypotheses |
| Two ICPs in the brief | Founders disagree, nobody recorded it | Write the conflict with both owners; route to `refine-icp` for evidence |
| Numbers keep changing between sessions | No source register | Add the source and date to every number; keep the old value marked superseded |
| Downstream skill cites a stale constraint | No refresh after a decision changed | Update the decision register, then the brief; add the new source |
| Customer logos listed as proof | Public-reference status never confirmed | Ask; until confirmed, replace names with segment descriptions |
| The interview took two hours | Asking for facts already in the brief | Build the gap list first; ask only gaps |
| Tool listed in the brief is not in `gtm.yaml` | Stack changed or was never configured | Note the mismatch; the operator updates `gtm.yaml` |
| An old "send proposal" item is treated as open | Historical action items mistaken for current | Mark it closed with the date it was done; decisions register is the source of truth |

## References

- [Company brief template](./references/company-brief-template.md): the sections, the header, and a fictional filled example.
- [Decision register](./references/decision-register.md): decisions, assumptions, conflicts, unresolved, with a fictional example.
- [Evidence labels](./references/evidence-labels.md): the four labels and how to apply them.
- [Source register](./references/source-register.md): how to log where facts came from.
- [Knowledge layer](./references/knowledge-layer.md): one insight per file, categories, extract and load procedures, promotion rules, a worked example.

Licensed CC BY 4.0 by GTM Adviser.
