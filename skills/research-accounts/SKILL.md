---
name: research-accounts
description: Research and prioritize sourced accounts using public signals, evidence-tagged pain, stakeholder maps, and separate fit and urgency scores, then prepare the personalization inputs that copy will use. Use for account qualification and preparation after sourcing; do not use to fabricate personalization, infer sensitive traits, or enrich without an approved credit plan.
---

# Research Accounts

> This is the Personalize step of the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate). It turns a usable list into accounts worth a message now, with the one fact per account that earns a relevant first line. Every claim carries a source and a date. Inference is labelled inference. Missing evidence lowers confidence; it never becomes a fact or a zero.

## When to use / when not to

Use when:
- A `usable` list exists from `source-tam` and an experiment names the audience.
- You need to rank accounts, build stakeholder maps, or prepare personalization variables before `write-outreach`.
- A single account needs a decision-ready brief before a first conversation.

Do not use when:
- The list has not passed the mandatory filters. Research on a dirty list is wasted spend.
- The goal is to research a live deal. That is `advance-deals`.
- The research would require inferring protected or sensitive traits about a person. Stop.

## Inputs

| Input | Where | What you take from it |
|---|---|---|
| Approved ICP | `market/icp.md` | fit criteria, persona ladder, disqualifiers |
| Active experiment | `experiments/*.json` | audience, hypothesis, which signal the experiment tests |
| Market map | `market/*.md` | competitors, substitutes, positioning hypotheses |
| Accounts and contacts | store tables `accounts`, `contacts` | who is in scope, provenance |
| Existing signals | store table `signals` if present, `.gtm/signals/` | what was already observed |
| Company context | `context/company.md` | the product, the pain it removes, the realistic next step |

## Procedure

1. **Fix the rules before the first search.** Write the allowed sources (company site, public profiles, job boards, press, filings, review sites, public posts), the freshness window (default 180 days for signals, 30 days for posts), and the time budget per account (default 3 minutes at list scale, 20 minutes for a single brief). Put them at the top of the run log.
2. **Confirm the entity.** Website, public company page, normalized domain. Watch for same-name companies, wrong country, parent versus subsidiary.
3. **Record firmographics as facts.** One line on what they do, who they sell to, size band, locations, ownership or funding stage. Each with a url and an observed date.
4. **Hunt for the why-now.** Work through `references/signal-playbooks.md`. For each signal found, record type, url, date, and the one sentence it earns in copy. No signal found is a valid result; write it down and score urgency low.
5. **Label inference.** Any pain, priority, or budget statement that is not quoted from a source is prefixed `inferred:` with the reasoning.
6. **Map stakeholders only with evidence.** Problem owner, users, approver, blocker, internal alternative. Public role plus url where available. Do not guess names.
7. **Score fit and urgency separately.** Fit from ICP criteria with transparent components. Urgency from signal recency and relevance. Disqualifiers override to zero. See the scoring section.
8. **Assign a segment and an angle.** Derive the segment from observed facts (for example, which category of tool they run, which trigger fired) and map it to one copy angle. Openers vary by segment; follow-ups do not.
9. **Build the personalization inputs.** Fill the tiered variables that exist in the store, then compose the composite context variable. See `references/personalization-tiers.md` and `references/context-variable-pattern.md`.
10. **Write the outputs.** Person-level facts to the store. Approved account briefs, in redacted form, to `market/accounts/<slug>.md` only when a human approves them for Git. Aggregate priority rules to `reports/research-<date>.md`.

## Scoring

Fit and urgency are two numbers. Never blend them before ranking.

**Fit (0 to 100).** Sum of ICP criteria met, each weighted as declared in `market/icp.md`. A disqualifier sets fit to 0 and moves the account to `excluded` with the reason.

**Urgency (0 to 100).** For each signal: `raw = recency × relevance`.

| Recency | Points |
|---|---|
| within 30 days | 3 |
| 30 to 90 days | 2 |
| older or undated | 1 |

| Relevance | Points |
|---|---|
| direct statement of the pain your product removes | 5 |
| active use of a tool your product replaces or extends | 4 |
| buying trigger (funding, new leader, relevant hire, lost capacity) | 4 |
| general interest in the topic | 2 |
| firmographic match only | 1 |

The strongest signal type for this ICP gets a 1.5 multiplier. Normalize by the theoretical maximum for the number of signal types checked. Cap at 100.

| Urgency | Timing |
|---|---|
| 80 to 100 | this week |
| 60 to 79 | next two weeks |
| 40 to 59 | next wave |
| 20 to 39 | monitor, re-scan in 30 days |
| below 20 | hold |

## Hard rules

1. Every fact has a url and an observed date. No url, no fact.
2. Inference is written as `inferred:` with the reasoning. It never appears in copy as a claim.
3. Never invent a trigger, quote, technology, relationship, or event.
4. Do not infer or record protected characteristics, health, politics, religion, or private life.
5. Missing evidence lowers confidence. It is not a zero and not a fact.
6. Fit and urgency stay separate through ranking. A disqualifier overrides both.
7. Freshness window default is 180 days for company signals and 30 days for posts. Older signals score 1 on recency and are never used as a why-now in copy.
8. Time budget per account at list scale is 3 minutes. Stop and score low when it runs out.
9. Person-level research lives in the store. Git gets approved account briefs and aggregate rules only.
10. Paid enrichment follows the credit-approval rule from `source-tam`.
11. Openers are tailored by segment. Follow-ups are segment-agnostic.
12. The composite context variable is capped at 3,000 characters and contains only facts from the store.

## Checklist

- [ ] Allowed sources, freshness window, and time budget written at the top of the run log
- [ ] Entity confirmed with domain and public page
- [ ] Firmographics recorded with url and date
- [ ] Signal playbooks worked through; absence of signals recorded explicitly
- [ ] Every inference prefixed `inferred:`
- [ ] Stakeholder map has a url for every named role
- [ ] Fit and urgency scored separately with components visible
- [ ] Disqualifiers applied before ranking
- [ ] Segment and angle assigned per account
- [ ] Tiered variables filled only from columns that exist
- [ ] Composite context variable built, under 3,000 characters
- [ ] Nothing person-level written to Git

## Output contract

| Artifact | Location | Tracked in Git | Content |
|---|---|---|---|
| Account facts and signals | store tables `accounts.attributes`, `signals` | no | facts with url and date, inferences labelled |
| Personalization variables | store table `contacts.attributes` | no | tiered variables plus `context_blob` |
| Priority list | `.gtm/research/<experiment>-priority.csv` | no | account, fit, urgency, timing, segment, angle |
| Account brief (single account) | `market/accounts/<slug>.md` | yes, after human approval | redacted brief per `references/account-brief-template.md` |
| Aggregate rules and findings | `reports/research-<date>.md` | yes | which signals were found at what rate, segment distribution, rule changes |

Status per account: `researched`, `prioritized`, `excluded` with reason, `stale` after 90 days.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Every account scores high urgency | relevance points given to firmographic matches | re-score with the table; only direct pain and triggers score 4 or 5 |
| Copy reads generic despite research | variables filled from list-level tiers only | check whether tier 2 or 3 facts exist; if not, use a segment opener, not a fake personal one |
| A fact turns out wrong in a reply | inference recorded as fact | find the missing `inferred:` label, fix the record, add the case to the run log |
| Research takes hours per account | no time budget | set 3 minutes at scale; 20 for a brief |
| Signals older than the window used in copy | freshness not enforced | filter by `occurred_at` before composing variables |
| Same person researched twice | no dedupe on slug | key research by LinkedIn slug or normalized email |

## References

- `references/signal-playbooks.md` - each signal, how to observe it, the sentence it earns
- `references/personalization-tiers.md` - variables by effort and impact, and what not to pursue
- `references/account-brief-template.md` - the single-account decision brief
- `references/context-variable-pattern.md` - the composite context blob and segment-to-angle map

Licensed CC BY 4.0 by GTM Adviser.
