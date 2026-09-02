# The composite context variable

One labelled text blob per lead, composed from the store, capped at 3,000 characters, used as the single input for any AI personalization step. It makes the prompt small, auditable, and identical across tools.

## Shape

```
PERSON
name: <first_name_clean> <last_name_clean>
title: <title_clean>
role_start: <YYYY-MM> (tenure <n> months)
headline: <headline>
recent_post_theme: <theme> (<date>)

COMPANY
name: <company_name_clean>
one_liner: <what they do>
sells_to: <customer type>
size_band: <band>
country: <country>
tools_on_site: <tool>, <tool>
hiring: <function> (<count> open roles, <date>)
signal: <signal_type> - <summary> (<date>)

SEGMENT
segment: <segment>
angle: <angle>
pain_line: <one sentence>
proof_point: <one sentence, sourced>
cta_angle: <one sentence>
```

Empty fields are omitted, not filled with "unknown". The prompt that consumes the blob is told: use only facts in the blob; if a section is missing, do not mention it.

## Segment derivation

Segments come from observed facts, not from guesses. Example rule set for a company that sells into a tooling category:

| Segment | Rule | Copy angle |
|---|---|---|
| `aware` | already uses the open standard or adjacent approach the product builds on | friction with the current backend |
| `cost_pain` | runs a commercial tool in the category, no self-hosted alternative | bill shock, consolidation |
| `mixed` | runs both commercial and self-hosted tools | lock-in, consolidation |
| `diy_pain` | only self-hosted tools | operational burden |
| `unknown` | no signal detected | generic scenario opener |

Write your own table in `market/segments.md` with one rule and one angle per segment. Rules must be testable from columns in the store.

## Openers vary, follow-ups do not

Openers are chosen by segment and may reference the signal. Follow-ups shift the angle and stay segment-agnostic. Restating the pain in a follow-up is the most common way to produce replies with no opportunities.

## Guardrails for the AI step

1. Input is the blob and the segment's approved angle. Nothing else.
2. Output is one opener line and one pain line, each under 25 words.
3. No numbers unless they are inside the blob with a source.
4. No mention of the recipient's post content verbatim.
5. Output is validated: length, no forbidden phrases, no invented entity names. Failures fall back to the segment's generic opener.
6. A 20-row sample is read by a human before any pool is loaded.
