# Knowledge layer

Raw sources (call transcripts, email threads, proposals, posts, internal docs) are never fed to a generating skill directly. They are too long, they mix fact with hope, and they carry names. Instead the agent extracts one discrete insight per file into `context/knowledge/`, and every skill that writes copy, prepares a meeting or answers a question loads that layer first. The layer is what makes output sound like this company instead of a template.

## Where it lives

```
context/
  company.md                  the brief (short, labelled)
  sources.md                  the source register
  knowledge/
    README.md
    objection-handling--already-use-a-spreadsheet.md
    pricing-framing--per-seat-with-usage-floor.md
    voice-style--short-sentences-no-superlatives.md
    proof-points--onboarding-time-band.md
```

File name: `<category>--<slug>.md`, lowercase, hyphens. One insight per file. Raw sources stay outside Git (a shared drive, the meeting tool, the mailbox); the source register records where.

## File format

```markdown
---
title: "Per-seat pricing with a usage floor"
category: pricing-framing
label: decision            # declared | observed | hypothesis | decision
status: validated          # emergent | validated | canonical
confidence: high           # low | medium | high
source: "Pricing call with the founders, 2026-08-12; proposal template v3"
date_extracted: 2026-08-14
tags: [pricing, proposals, seats]
references: [pricing-framing--annual-prepay-discount, objection-handling--too-expensive-for-five-seats]
---

# Per-seat pricing with a usage floor

**Claim.** Pricing is per seat with a minimum of five seats. Below five, the offer is the self-serve tier.

**Evidence.** Stated by both founders on the 2026-08-12 call. Matches the last three proposals.

**Use.** In copy, never quote a price in touch 1. In proposals, state the floor before the per-seat number. When a prospect asks for three seats, route to self-serve, do not discount.
```

Every file carries a one-line claim, the evidence, and how to use it. Keep files under 40 lines.

## Categories

| Category | Captures | Example slug |
|---|---|---|
| objection-handling | responses to recurring pushback | `already-have-an-agency` |
| pricing-framing | how pricing is structured and justified | `usage-floor` |
| sales-patterns | structures that recur in conversations that closed | `demo-before-pricing` |
| voice-style | tone, sentence length, words the founders use and avoid | `no-superlatives` |
| value-propositions | specific claims with the evidence behind them | `same-day-handoff` |
| proof-points | anonymised outcomes as ranges | `onboarding-under-two-weeks` |
| discovery-questions | questions that opened up a prospect | `who-owns-the-list` |
| automation-examples | workflows referenced in sales or delivery | `crm-dedup` |
| icp-signals | observable traits of best and worst customers | `first-revenue-hire` |

Let the taxonomy grow from what the sources contain. A new category needs three files before it earns a name.

## Extract procedure

1. Read the whole source once. Note the three to eight things that would change how you write to this company's buyers.
2. For each, check the category folder for a near-duplicate. If one exists, add the new source to its `source` line and raise `status` if the rule below allows.
3. Write one file per insight with the format above. The claim is one sentence. The evidence names the source and date. The use section says what to do with it in copy, calls or proposals.
4. Label it: `declared` if someone said it, `observed` if the data shows it, `hypothesis` if it is a guess worth testing, `decision` if a stakeholder decided it.
5. Set `status: emergent`. Set `confidence` from the quality of the source, not from how much you like the claim.
6. Add the source to `context/sources.md` if it is new.
7. Never write a customer name, a contact, or a quote that identifies a person. Proof points are ranges ("onboarding under two weeks for teams of 20 to 60"), never a named result.

## Load procedure

1. Walk `context/knowledge/`. Count files per category and per status.
2. Load `canonical` and `validated` files fully. List `emergent` files by title and mark them unverified.
3. Report in five lines: counts, which categories are empty, which insights conflict with `context/company.md`.
4. Only then write copy, prepare a meeting, or draft a proposal.

## Promotion rules

| From | To | When |
|---|---|---|
| emergent | validated | a second independent source agrees, or the operator confirms |
| validated | canonical | an explicit decision in `strategy/decisions.md` names the file |
| any | conflict | two files contradict each other; both stay, the conflict goes to the decision register |
| any | superseded | a newer decision replaces it; keep the file, add `superseded_by` |

A canonical file is ground truth for every skill until a decision changes it. A `hypothesis` label never reaches canonical; it becomes an experiment instead.

## Worked example

Source: a 40-minute discovery call with a fictional logistics software company, 2026-08-20.

Extracted files:

- `objection-handling--we-tried-outbound-before.md` (declared, emergent, medium): "The prior attempt used a bought list and one template." Use: open with the list quality, not the channel.
- `voice-style--founder-writes-in-fragments.md` (observed, emergent, high): the founder writes short fragments and dislikes exclamation marks. Use: mirror in step 1, which the founder writes anyway.
- `icp-signals--three-plus-warehouses.md` (hypothesis, emergent, low): "Companies with three or more sites feel the handoff problem." Use: test it as an experiment audience, do not target on it yet.
- `proof-points--handoff-time-band.md` (observed, validated, high): two customers report the handoff dropped from days to hours. Use: "customers of your size report handoffs in hours instead of days", no names.

After the call, the decision register gets one conflict: the brief says "mid-market first", the founder said "the three-site shops are where it hurts". Owner: the founder. Due: next Friday.
