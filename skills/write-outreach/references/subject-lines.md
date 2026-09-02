# Subject lines

Two strategies work. The middle does not.

## Strategy A: unsexy, internal-looking

Looks like an internal note, a task, an update. Lowercase fragment. No sell.

- `{{firstName}}, quick idea`
- `{{firstName}}, this morning`
- `callbacks`
- `q4 planning`
- `quick one`
- `{{companyName}} phone line`

Why it works: it does not trigger the sales filter before the open, and the preview text (line 1) carries the personalisation.

## Strategy B: over-intriguing

So bold that opening is forced. Name or company plus a stake.

- `{{firstName}} vs {{competitorName}}`
- `{{firstName}}, the next {{marketLeader}}?`
- `what we heard when we called {{companyName}}`

Why it works: curiosity with a personal stake. Risk: bait and switch. The body must resolve the subject in the first line or you lose trust.

## Strategy C: hyper-specific plus disarm in the body

Subject uses a very personal detail. The body or P.S. immediately explains: "P.S. I wanted a subject that stands out in your inbox." Use rarely.

## The middle that fails

Product-hook subjects ("Answer every call at {{companyName}}"), newsletter syntax ("Wordplay | Brand @ Event"), company-name-only subjects as the default. They telegraph sales before the open. Company-name subjects feel automated; test them against fragments, do not default to them.

## Universal rules

| Rule | Test |
|---|---|
| 6 words or fewer | word count |
| no selling in the subject (except strategy B) | no product name, no benefit claim |
| name or company name in it | contains `{{firstName}}` or `{{companyName}}` |
| tone matches the body | a reader is not surprised by line 1 |
| never `Re:` or `Fwd:` | immediate trust loss when discovered |
| no emoji, no capitals-only words, no brand domain | regex |
| lowercase fragments beat capitalised sentences | test it, do not assume it |
| follow-up in thread: empty subject | provider threads it as a reply |

## Testing subject lines

Subject lines are a variable in their own right. Test them explicitly: fragment vs question vs product hook, with the same body. Do not change subject and body at the same time and call it a variant.

## Examples by market

Fictional examples. Replace with your own.

| Market | A (internal) | B (intrigue) |
|---|---|---|
| en-GB, trades | `{{firstName}}, after 5pm` | `we rang {{companyName}} on tuesday` |
| en-US, software | `{{firstName}}, onboarding` | `{{firstName}} vs {{competitorName}}` |
| de-DE, formal | `Rückrufe` | `{{companyName}} um 18:10` |
| de-DE, trades | `{{firstName}}, kurze Idee` | `{{firstName}}, heute Morgen` |
