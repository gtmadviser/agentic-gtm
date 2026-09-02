---
name: map-market
description: Build sourced market signals, competitor profiles, and positioning hypotheses for a B2B startup, with every claim dated and attributed. Use for market mapping, competitor research, category analysis, positioning exploration, or deal-room competitive questions; do not use for account-level prospect research or to publish unsourced market sizes.
---

# Map Market

> Positioning that ignores the alternatives a buyer actually weighs produces copy nobody answers. This skill runs at the Research stage of the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate) and feeds `refine-icp` (competitor customers to suppress, substitutes that define the category) and `write-outreach` (angles, proof, what never to say). It treats every vendor claim as a claim, dates every signal, and writes positioning as hypotheses with the evidence that would disprove them.

## When to use / when not to

Use when:

- `context/company.md` exists and `market/` is empty or older than six months.
- A deal, a lost-reason cluster, or a copy review names a competitor the workspace does not profile.
- The team is choosing a positioning line, a category name, or a wedge segment.
- A new alternative appears (launch, acquisition, price change).

Do not use when:

- The question is about one target account. That is `research-accounts`.
- Someone wants a market size for a deck and there is no source. This skill does not produce numbers it cannot cite.
- The company brief does not exist. Run `onboard-company-brain` first.

## Inputs

| Input | Where | What you take from it |
|---|---|---|
| Company brief | `context/company.md` | product, positioning belief, alternatives the founders name |
| ICP | `market/icp.md` | segment boundaries, previous-tool patterns from closed deals |
| Existing map | `market/*.md`, `market/competitors/*.md` | prior profiles, dates, open questions |
| Loss reasons | `reports/pipeline-<date>.md` | which alternatives win deals against you, in aggregate |
| Sources | `context/sources.md`, `market/sources.md` | what has already been read and when |
| Stage | `gtm --json next` | context must be done; map-market itself is optional |

## Procedure

1. **Route by use case.** Pick one: category map (all alternatives, one page), competitor profile (one alternative, full depth), positioning review (options and tests), competitor watch (what changed since the last date), deal-room question (talking points for one live deal). Each has its own output; do not mix them in one file.
2. **Define the question and the boundary.** Write one sentence: which decision this research informs. Set the time boundary (signals older than 12 months are flagged `stale`) and the geography. Write both at the top of the output file.
3. **Bucket the alternatives.** Four buckets, at least one entry each: direct competitors, substitutes (a different product solving the same job), internal workarounds (spreadsheets, scripts, an extra hire), and do nothing. The last two lose more deals than most founders admit; the loss-reason table says how many.
4. **Collect signals.** For every signal: source URL or document, observed date, what was directly observed (quote, screenshot description, pricing page state), whether it is a vendor claim or an observation, confidence. Use the source types in `references/market-signal-sources.md`. Log every source in `market/sources.md`.
5. **Profile each alternative.** Use `references/competitor-profile-template.md`. Compare on buyer, job, workflow, proof, commercial model, and tradeoffs. Feature counts are not a dimension. Every profile has an honest strengths section; a profile without one is not accepted.
6. **Write positioning options as hypotheses.** Use `references/positioning-hypothesis-template.md`. Each option states who it wins with, what evidence supports it, what evidence would disprove it, and the cheapest test. At most three options per review.
7. **Feed the other skills.** List competitor customers found in public sources as a suppression candidate for `refine-icp` (anti-ICP table). List the angles, proof points, and forbidden framings for `write-outreach` in one block at the end of the map.
8. **Date and file.** Write outputs under `market/` with the observed date in the file name. Mark stale signals. Add open questions with an owner. Run `gtm --json next`; map-market does not block a stage, but the operator should see it in the summary.

### Deal-room variant

For a live deal: read the profile, identify the buyer's likely reason (cost, migration, consolidation, a capability gap), pick two or three structural differences relevant to that reason, write four questions the seller can ask, and list the proof points with sources. Ten lines. Mark it as a draft for the seller; do not send anything.

## Hard rules

1. No unsourced market sizes, growth rates, or share figures. If a figure appears, it has a URL or document, a date, and the publisher's method in one line.
2. Vendor claims are labelled `claim`. Only a directly observed fact (a pricing page on a date, a public filing, a review with a date) is `observation`.
3. Every signal carries a source and an observed date. Signals older than 12 months are marked `stale` and re-checked before use in copy.
4. Every competitor profile has a strengths section written as if the competitor's best seller reviewed it.
5. Comparison dimensions are buyer, job, workflow, proof, commercial model, tradeoffs. No feature matrices.
6. Positioning is written as hypotheses with disconfirming evidence. Never as a decided line unless `strategy/decisions.md` records the decision.
7. Never recommend positioning as "the cheaper version of X". It trains the market to see a discount, and it loses on breadth.
8. Competitor customers are named only from public sources with the URL and date. No private lists, no scraped gated content.
9. No client-confidential material about competitors (contracts, private pricing, insider statements) is written down anywhere in the workspace.
10. The active competitor set has at most 12 entries. Beyond that, the map is a directory, not a map.
11. Copy guidance from this skill includes the rule: do not name competitors unprompted in cold outreach; engage when the prospect names them.
12. No customer-specific material from your own customers enters a competitor profile.

## Checklist

- [ ] Use case chosen; question and decision written in one sentence.
- [ ] Time boundary and geography set at the top of the file.
- [ ] All four buckets have at least one entry.
- [ ] Every signal has source, observed date, claim/observation label, confidence.
- [ ] Every profile has buyer, job, workflow, proof, commercial model, tradeoffs, and an honest strengths section.
- [ ] Positioning options written as hypotheses with disconfirming evidence and a test; at most three.
- [ ] Suppression candidates listed for `refine-icp`; copy guidance block listed for `write-outreach`.
- [ ] No market-size figure without URL, date, and method.
- [ ] Stale signals marked; open questions have owners.
- [ ] `market/sources.md` updated.

## Output contract

| Artifact | Location | Rules |
|---|---|---|
| Category map | `market/map-<YYYY-MM-DD>.md` | Question, boundary, four buckets, one line per alternative, links to profiles, suppression candidates, copy guidance block, open questions. |
| Competitor profile | `market/competitors/<slug>.md` | Template in references. Header: `Last verified: date`, `Priority: primary / secondary / watch / adjacent`. |
| Positioning hypotheses | `market/positioning-hypotheses.md` | One section per option: statement, wins with, evidence for, disconfirming evidence, test, status. |
| Signals and sources | `market/sources.md` | One row per source: ID, URL or document, observed date, what it supports, claim or observation. |
| Deal-room note | `meetings/<YYYY-MM-DD>-<account-slug>-competitive.md` | Ten lines, draft for the seller, redacted of contact data. |
| Decision | `strategy/decisions.md` | Only when the operator chooses a positioning line; owner and date. |

Priority semantics: `primary` appears in most deals, `secondary` appears sometimes, `watch` not yet a threat, `adjacent` appears alongside you, not instead of you.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| The map lists 25 competitors | No boundary, or directory thinking | Cut to the 12 that appear in deals or in the ICP segment; park the rest with a date |
| Profiles read like a takedown | Strengths section skipped | Rewrite strengths first; a seller who ignores a strength loses the room |
| Positioning was "decided" in the map | Hypothesis promoted without a decision | Move it to hypotheses; if the team did decide, record it in the decision register with an owner |
| A market-size figure has no source | Copied from a deck | Remove it or cite it with URL, date, and method |
| Copy team leads with a competitor name | Guidance block missing | Add the block: engage only when the prospect names the alternative |
| Signals older than a year drive the angles | No freshness window | Mark stale; re-verify the pricing page and positioning before use |
| Substitutes and do-nothing missing | Only vendors considered | Add both buckets; check loss reasons for "no decision" and "built in-house" |
| Competitor customer list from a scraped tool | Rule 8 broken | Delete it; keep only public-source names with URLs |

## References

- [Competitor profile template](./references/competitor-profile-template.md): the six dimensions, the strengths section, and a fictional example.
- [Market signal sources](./references/market-signal-sources.md): public source types, what each proves, freshness windows.
- [Positioning hypothesis template](./references/positioning-hypothesis-template.md): statement, evidence, disconfirmation, test.

Licensed CC BY 4.0 by GTM Adviser.
