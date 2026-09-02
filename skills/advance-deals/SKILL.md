---
name: advance-deals
description: Prepare for and follow up on active deals by pulling CRM, meeting, email, and chat context in parallel, separating customer statements from seller interpretation, and drafting evidence-gap questions and a follow-up with mutual next steps. Use for meeting preparation, deal reviews, next-step drafts, and risk analysis; do not use to send messages, change stages, or create tasks automatically.
---

# Advance Deals

> Deals are where the engine's Reach step becomes revenue. This skill gives the seller a grounded picture of one account before a conversation and a draft after it. It reads every source it is allowed to read, in parallel, resolves conflicts with a fixed priority order, and keeps the customer's words separate from the seller's reading of them. It never writes to the CRM, never sends, and never invents context.

## When to use / when not to

Use when:
- A meeting with an existing opportunity is scheduled and the seller needs preparation.
- A deal review needs a one-page status with evidence and gaps.
- A follow-up needs drafting after a call.
- A pipeline needs a stale-deal and risk sweep.

Do not use when:
- The account has no opportunity. That is `research-accounts`.
- Someone wants a stage moved, a task created, or a message sent. This skill produces drafts and evidence only.
- Meeting records are unavailable and the request depends on what the customer said. Say so; do not reconstruct.

## Inputs

| Input | Where | What you take from it |
|---|---|---|
| Opportunities and activities | store tables `opportunities`, `activities`, or `gtm --json sync crm` output | stage, amount, close date, owner, last activity, stage entry date |
| Contacts | store table `contacts` | roles on the buying side, last touch |
| Meeting records | `meetings/` and any connected recording or notes source | what the customer said, when, who was there |
| Email and chat threads | connected sources where available | commitments, objections, internal assessments |
| Account brief | `market/accounts/<slug>.md` | prior research, signals |
| Company context | `context/company.md` | product, proof, next-step options |
| Competitor notes | `market/*.md` | alternatives named by the customer |

## Procedure

1. **Detect the mode.** Individual contributor preparing their own deal, or leader reviewing a team's pipeline. Explicit language decides; otherwise the number of open deals owned by the requester decides; otherwise ask one clarifying question. Mode sets depth and format.
2. **Pull every source in parallel.** CRM record, meeting records, email threads, chat threads. Do not wait for one before starting the next. Note any source that is unavailable and continue.
3. **Resolve conflicts by priority.** Customer's own words in a recording or written message beat seller notes. Seller notes beat CRM fields. CRM fields beat internal chat opinions. Newer beats older within the same tier. Record the conflict when two top-tier sources disagree.
4. **Extract the deal picture with evidence tags.** Business problem, desired outcome, timeline, decision process, economic buyer, champion, metrics, competition, paper process, commitments made by each side, unknowns. Each item is tagged `[customer]`, `[seller]`, `[crm]`, or `[internal]` with a date. Empty is a valid value; write `not found in any source`.
5. **Separate statements from interpretation.** Two columns: what the customer said, what we think it means. Nothing crosses the line without a label.
6. **Write the evidence-gap questions.** For each empty or weak element, one question that would close it, phrased for this account. No generic discovery lists. See `references/evidence-gap-questions.md`.
7. **Flag risks.** Stale (no activity in 14 days), past-due next step, single-threaded (one contact), no economic buyer identified, competitor named without a response, close date moved more than twice.
8. **Draft the follow-up.** Mutual next steps with owner and date on both sides, a summary of what was agreed in the customer's words, and one ask. Mark it `DRAFT - human review required`. See `references/follow-up-template.md`.
9. **Write the preparation file.** `meetings/<YYYY-MM-DD>-<slug>-prep.md` using `references/meeting-prep-template.md`, redacted. Raw contact details, transcript text, and activity ids stay in the store or the source system.
10. **Hand back.** Present the prep, the questions, the risks, and the draft. Stop. Sending, stage changes, and tasks are human actions or a future plan/apply workflow.

## Hard rules

1. No CRM writes, no messages sent, no tasks created, no stage changes. Ever, from this skill.
2. Every extracted element carries a source tag and a date.
3. Customer statements and seller interpretation are never merged into one sentence.
4. Quote only from supplied or accessible source material. No reconstructed quotes.
5. An element not found in any checked source is written as `not found`, never guessed.
6. A source that is unavailable is named as unavailable in the output.
7. Stale threshold is 14 days without a logged activity.
8. Follow-up drafts are marked as drafts and contain mutual next steps with owners and dates on both sides.
9. Preparation files in `meetings/` are redacted: roles not names where possible, no emails, no phone numbers, no transcript text.
10. Internal assessments from chat are labelled `[internal]` and never surface in customer-facing drafts.

## Checklist

- [ ] Mode detected and stated
- [ ] All sources pulled in parallel; unavailable ones named
- [ ] Conflict priority applied; conflicts recorded
- [ ] Every element tagged with source and date
- [ ] Statements and interpretation in separate columns
- [ ] Evidence-gap questions specific to this account
- [ ] Risks flagged with the rule that fired
- [ ] Follow-up drafted with mutual next steps, marked draft
- [ ] Prep file written to `meetings/` and redacted
- [ ] Nothing sent, changed, or created in any external system

## Output contract

| Artifact | Location | Tracked in Git | Content |
|---|---|---|---|
| Meeting preparation | `meetings/<date>-<slug>-prep.md` | yes, redacted | deal picture, gaps, questions, risks |
| Follow-up draft | `meetings/<date>-<slug>-followup.md` | yes, redacted | draft marked for human review |
| Pipeline review | `reports/pipeline-<date>.md` | yes | stage table, stale and risk flags, aggregates |
| Structured block for other skills | returned inline | no | company, stage, amount, close, owner, last contact, element status |

Structured block shape when another skill calls this one:

```
Company: <name>
Opportunity: <name> | Stage: <stage> | Amount: <amount> | Close: <date>
Owner: <name> | Last contact: <n> days ago
Elements: problem=<status>, outcome=<status>, timeline=<status>, decision=<status>, buyer=<status>, champion=<status>, metrics=<status>, competition=<status>
Sources checked: <list> | Unavailable: <list>
Risks: <list>
```

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Prep reads confident but the call contradicts it | seller interpretation recorded as customer statement | re-tag, move to the interpretation column, add the case to the run log |
| Empty picture despite many activities | CRM fields empty, meeting records not searched | search recordings and notes for each element before concluding |
| Follow-up lists only our next steps | one-sided draft | add the customer's commitments with owner and date, or write `no customer commitment obtained` |
| Leader asks for pipeline and gets one deal | mode not detected | apply the detection steps, then group by owner and stage |
| A source timed out and the output looks complete | unavailability not surfaced | list unavailable sources at the top of the output every time |

## References

- `references/meeting-prep-template.md` - the preparation page
- `references/follow-up-template.md` - the draft follow-up
- `references/evidence-gap-questions.md` - questions per missing element

Licensed CC BY 4.0 by GTM Adviser.
