# Account brief

One page a person can act on in two minutes. Every claim has a source or is marked as an assumption. If no trigger exists, say so and score lower. Do not invent one.

Write to `market/accounts/<slug>.md` only after a human approves the redacted version. Person-level detail stays in the store.

```markdown
# <Company> account brief
Fit: <0-100> · Urgency: <0-100> · Timing: <this week | next two weeks | next wave | monitor | hold> · Researched: <YYYY-MM-DD>

## What they do
<one or two lines: product, who they sell to, size band, geography, stage>
Sources: <url>, <url>

## Why now
- <signal type>: <one line> (<url>, <date>)
- <signal type>: <one line> (<url>, <date>)
- No further signals found within 180 days.

## Where we fit
<the one use case that matters for this account, and the likely pain in their terms>
inferred: <reasoning for anything not quoted from a source>

## Who to reach
| Role | Function | Evidence | Open with |
|---|---|---|---|
| Problem owner | <title> | <url> | yes, because <reason> |
| Approver | <title> | <url> | later |
| Blocker or internal alternative | <title or team> | <url> | no |

## Fit and disqualifiers
Fit components: <criterion: met/not met> ...
Disqualifiers checked: <list>. None triggered. | Triggered: <which>, account excluded.

## Recommended next action
<one action, one owner, one date>

## Draft opener (for write-outreach, not for sending)
> <two to three lines, scenario-first, one soft question, no claims without a source>
```

## Redaction before Git

Remove names of people, direct emails, phone numbers, and any private detail. Keep roles, company facts, and public urls. If the brief cannot be redacted without losing its point, it stays in the store.
