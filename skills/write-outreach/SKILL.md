---
name: write-outreach
description: Write and review cold outreach copy (email and LinkedIn) that passes hard quality gates before it enters a campaign draft. Use for first touches, follow-ups, variants, and copy reviews; do not use to stage, plan, send, or activate anything.
---

# Write Outreach

> Turns an approved ICP, an approved experiment, and account evidence into 2-3 copy variants per step that a real person could have typed. This is the Personalize stage of the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate). The output is a reviewed copy set with a stated hypothesis per variant. `stage-campaign` places it into a `CampaignDraft`; this skill never touches a provider.

## When to use / when not to

Use this skill to:
- write touch 1, follow-ups, LinkedIn invites and LinkedIn messages for an approved experiment
- produce 2-3 meaningfully different variants per step, each with a hypothesis
- review copy someone else wrote against the rubric before a plan is created
- adapt copy to a new market or language (native rewrite, never translation)

Do not use it:
- before `market/icp.md` has an approved working definition and `experiments/` has an approved experiment
- to invent personalisation the store cannot fill for the whole pool
- to stage, plan, apply, or activate campaigns (that is `stage-campaign`)
- to write nurture, newsletter, or inbound copy

## Inputs

| Source | What you take from it |
|---|---|
| `context/company.md` | one-sentence product description, allowed proof points, voice override block, forbidden claims |
| `market/icp.md` | approved working definition, exclusions, trigger, likely problem owner |
| `experiments/<id>.json` | audience, trigger, channel, hypothesis, decision rule, safeguards |
| store tables `accounts`, `contacts` | fill rate per personalisation variable in the exact pool |
| `reports/*.md`, learning log in `strategy/decisions.md` | angles already burned, anti-patterns, winning openers |
| `gtm --json next` | confirms the workspace is at stage `copy` |

## Procedure

1. **Confirm the stage.** Run `gtm --json next`. If `next.stage` is not `copy`, stop and route to the skill it names. Copy written before the ICP and experiment are approved is rewritten later, every time.
2. **Load the voice override.** Read the voice block in `context/company.md`: formal or informal address, forbidden punctuation, spelling variant, which step the founder writes personally. If the block is missing, write it first with the operator and record it in `strategy/decisions.md`.
3. **Pick one angle per message.** The experiment names the trigger. Choose the single angle that follows from it (a loss the recipient can feel, a task they are trying to staff, a season, a visible workaround). Two angles in one message is the most common reason copy underperforms.
4. **Pick 2-3 levers, not 13.** From `references/copy-rules.md` section "Levers", choose the two or three that fit the audience. Stacking more dilutes each one.
5. **Check variable fill rates.** For every `{{variable}}` you intend to use, count how many records in the pool have it filled. Below 80 percent: drop it from step 1, or split the pool and run two variants, or define a fallback sentence. An empty variable is worse than no personalisation.
6. **Write the opener.** Line 1 is the reason this recipient, today. Test: could this line be true for 10,000 other people? If yes, rewrite. Prefer an observation the recipient can verify in 30 seconds (their own website, their own phone line, a public review, a public job post).
7. **Write the body.** Structure is hook → one sentence that says what the product is → one conversation CTA. 40-70 words, at most 3 short paragraphs. A scenario the recipient recognises beats a statistic. No links and no brand domain in touch 1.
8. **Write the CTA.** One ask, answerable in one word or one letter. No calendar links in touch 1. The CTA sentence must explain what happens when they say yes.
9. **Write follow-ups.** Each follow-up passes the 3-D test in `references/follow-ups.md`: Different angle, Disarming tone, Direct ask. Never restate features from step 1. Every step must stand alone for a reader who never saw the previous one.
10. **Write subject lines.** At most 6 words, lowercase fragment or internal-looking note, or deliberately over-intriguing. Never `Re:` or `Fwd:`. See `references/subject-lines.md`.
11. **Write 2-3 variants per step.** Each variant changes one thing on purpose (opener type, CTA shape, proof type) and carries a one-line hypothesis. Variants without a hypothesis are noise.
12. **Choose the channel shape.** If the experiment channel includes LinkedIn, default to a bare connection invite with no note, and treat the messaged invite as the challenger variant. See `references/copy-rules.md` section "LinkedIn-first sequences".
13. **Run the slop check, then the rubric.** Run the detect pass from `references/anti-slop-writing.md` on every variant (name each pattern, quote the line, state the fix), then the nine-step pre-send check; a single hit fails the review. Confirm with the pass/fail list in `references/anti-slop-eval.md`. Score with `references/copy-review-rubric.md`. Any hard gate failed: fix before scoring. Score 85 or above ships, 70-84 gets one more pass, below 70 restart from step 3.
14. **Write the output** to `campaigns/<experiment-slug>-copy.md` using the output contract below. Log the angle, levers, and variant hypotheses in `strategy/decisions.md`. Hand off to `stage-campaign`.

## Hard rules

| # | Rule | Test |
|---|---|---|
| 1 | Line 1 is specific to this recipient | could not be true for 10,000 others |
| 2 | One sentence states what the product is | a reader can say what you sell after one read |
| 3 | 40-70 words per email, 3 paragraphs maximum | word count; 90 words only with a written justification |
| 4 | One angle per message | the message answers one "why now" |
| 5 | No em dashes, no en dashes as punctuation | a search for U+2014 and U+2013 returns nothing |
| 6 | Subject line 6 words or fewer, never `Re:` or `Fwd:`, no emoji, no capitals-only words | regex |
| 7 | No unsupported numbers | every figure has a source the recipient could ask for |
| 8 | No brand domain, no link, no attachment in touch 1 | search body for `http`, `www`, `.com`, `.de`, `.io` |
| 9 | Every `{{variable}}` has 100 percent fill or a fallback | fill-rate query on the exact pool |
| 10 | One consistent address form per message and per pool | no mix of formal and informal in one sequence |
| 11 | Follow-ups change the angle and never repeat features | diff against step 1 shows a new reason to reply |
| 12 | Explicit opt-out path that costs one word | a reader knows how to stop the sequence |
| 13 | 2-3 variants per step, each with a stated hypothesis | the copy file lists the hypothesis next to each variant |
| 14 | Native language, not translated | a native speaker would not spot a source language |
| 15 | No placeholder copy leaves this skill | search for `TODO`, `TBD`, `[insert`, `lorem` |
| 16 | Slop gate passes: no substitute kickers, triads, "not just", forced contrasts, pivots, hook questions, abstract noun stacks, adjective spirals, intensifiers, opener or sign-off clichés | nine-step check in `references/anti-slop-writing.md` returns zero hits |

## Checklist

- [ ] `gtm --json next` reports stage `copy`
- [ ] Voice override block read and applied
- [ ] One angle chosen and written down before drafting
- [ ] 2-3 levers chosen and named in the copy file header
- [ ] Fill rate checked for every variable in the exact pool
- [ ] Opener passes the 10,000-recipients test
- [ ] Product stated in one sentence
- [ ] 40-70 words, 3 paragraphs maximum, per email
- [ ] Subject lines 6 words or fewer, no `Re:`, no `Fwd:`
- [ ] No dashes as punctuation anywhere
- [ ] No links, no brand domain in touch 1
- [ ] Every number has a source
- [ ] Follow-ups pass Different, Disarming, Direct
- [ ] Opt-out sentence present and cheap
- [ ] 2-3 variants per step, each with a one-line hypothesis
- [ ] Slop check: zero hits
- [ ] Rubric score 85 or above, no hard gate failed
- [ ] Copy file written to `campaigns/`, decision logged

## Output contract

Write `campaigns/<experiment-slug>-copy.md` with this header, then one section per step, then one subsection per variant:

```markdown
# Copy set: <experiment-slug>
experiment: experiments/<id>.json
audience: <one line>
angle: <one line>
levers: relevance, curiosity, simplicity
address: formal | informal
language: de | en | fr
channel_shape: email-only | linkedin-first | multichannel
rubric_score: 91
reviewed_by: <operator name>, <date>

## Step 1 (day 0, email)
### Variant A (hypothesis: verifiable observation opener beats scenario opener)
subject: ...
body: ...
### Variant B (hypothesis: ...)
...
## Step 2 (day 3, email)
...
```

Rules for the file:
- Git holds the copy, the hypotheses, and the score. Git never holds recipient lists, emails, or phone numbers.
- Variable names must match the columns that exist in the store. List the fill rate for each variable under the header.
- `stage-campaign` copies the body text into the `CampaignDraft` JSON without edits. If you need to change copy after staging, change this file first, then re-stage.
- The learning log in `strategy/decisions.md` gets one line: date, experiment, angle, why this angle, which variant is the control.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| High reply rate, no positive replies | reminder-style or "did you see this" follow-ups, or a hook that provokes but carries no offer | rewrite follow-ups with a new angle; measure positive replies, not replies |
| Replies say "who are you" or "unsubscribe" | product never stated in one sentence, or sender reads like a call centre | add the what-it-is sentence; use a local sender identity and local number |
| Opens high, replies near zero | subject promised something the body did not deliver, or copy is a feature list | align subject and opener; cut to one angle |
| Native speakers call the copy stiff | translated from another language, superlatives, business words | rewrite from scratch in the target language with everyday words |
| Variant results identical | variants differ in wording, not in hypothesis | change opener type, CTA shape, or proof type, one at a time |
| Copy rejected by the operator as "not us" | voice override block missing or ignored | write the block first, then rewrite |
| Recipient received an empty variable | fill rate not checked on the exact pool | add fallback or split the pool; re-check before staging |
| Spam complaints from a formal vertical | informal address, pushy CTA, or two follow-ups in a week | switch to formal address, one follow-up, longer gap |

## References

- [copy-rules.md](./references/copy-rules.md): the full rule set, levers, structure, CTA shapes, LinkedIn-first sequences, voice override block
- [subject-lines.md](./references/subject-lines.md): the two strategies that work, the middle that fails, tests
- [follow-ups.md](./references/follow-ups.md): the 3-D test, nine follow-up angles, what never to send
- [variables-and-spintax.md](./references/variables-and-spintax.md): variable tiers, fill-rate rule, stacking, spintax convention
- [dach-pack.md](./references/dach-pack.md): formal and informal address, native German, burned phrases, local number rule, legal awareness note
- [anti-slop-writing.md](./references/anti-slop-writing.md): the register gate; edit and detect modes, banned words, rhythm and voice patterns, German patterns, nine-step pre-send check, before and after
- [anti-slop-eval.md](./references/anti-slop-eval.md): the pass/fail list run on every draft before it is returned
- [copy-review-rubric.md](./references/copy-review-rubric.md): hard gates, 12-point scoring, worked example

Licensed CC BY 4.0 by GTM Adviser.
