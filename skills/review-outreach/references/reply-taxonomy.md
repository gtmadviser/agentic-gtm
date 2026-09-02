# Reply taxonomy and benchmarks

Label every reply with exactly one label. Counts, not text, go into reports.

## Labels

| Label | Definition | Numerator for | Denominator effect |
|---|---|---|---|
| `positive_interested` | Asks for a call, demo, pricing, trial, or says "yes, let's talk" | positive replies, interested | counted in delivered |
| `positive_soft` | Wants information, "send me details", "maybe next quarter, keep me posted" | positive replies | counted in delivered |
| `positive_referral` | Points to a better contact inside the company or a peer company | positive replies | counted in delivered |
| `neutral_question` | Asks a clarifying question without stated interest or rejection | human replies only | counted in delivered |
| `negative_not_now` | Timing rejection, "no budget this year", "we just signed" | human replies only | counted in delivered |
| `negative_not_fit` | Says the problem does not exist for them or they are the wrong company | human replies only | counted in delivered; feeds anti-ICP |
| `negative_hostile` | Anger, threat, spam accusation, legal reference | hostile | counted in delivered; safeguard input |
| `unsubscribe` | Any opt-out request, explicit or implied ("stop emailing me") | unsubscribes | counted in delivered; must be suppressed within 24 hours |
| `out_of_office` | Automatic absence reply | none | excluded from reply denominators |
| `bounce` | Delivery failure, hard or soft | bounces | excluded from reply denominators; in bounce rate |

Referral replies often carry a name and email of a third party. Store them in the store as a new contact with provenance "referral from reply"; never paste them into Git.

## Rates

- Positive reply rate = (`positive_interested` + `positive_soft` + `positive_referral`) / delivered.
- Human reply rate = every label except `out_of_office` and `bounce`, divided by delivered.
- Positives per reply = positive replies / human replies.
- Hostile rate = `negative_hostile` / delivered.
- Unsubscribe rate = `unsubscribe` / delivered.

## Benchmarks for cold email to a qualified list

| Metric | Good | Great | Investigate |
|---|---|---|---|
| Positive reply rate | 1% or more | 2% or more | below 0.5% at usable certainty |
| Positives per reply | 25% or more | 40% or more | below 10% (curiosity harvesting) |
| Bounce rate | below 2% | below 1% | above 2% overall or 5% per sender |
| Hostile rate | below 0.1% | 0% | above 0.3% |
| Unsubscribe rate | below 0.5% | below 0.2% | above 2% |

Benchmarks assume a verified list and warmed senders. LinkedIn messages and event follow-ups run several times higher on positive rate and are not comparable with cold email in the same table.

## Classification procedure

1. Pull reply text and the campaign, variant, and step it answered. Keep the export in the store or `.gtm/replies/`.
2. Read each reply in full. Label the whole thread, not the first line. A "not now" followed by "but send me details" is `positive_soft`.
3. Apply one label. When torn between positive and neutral, choose neutral. When torn between `negative_not_now` and `negative_not_fit`, choose `negative_not_fit` only if the reply states the problem does not apply.
4. Anything that mentions spam, law, or "how did you get my address" is `negative_hostile` even when polite.
5. Save labels with reply IDs. Report counts per campaign, variant, and label.
6. Suppress `unsubscribe` and `negative_hostile` contacts across all campaigns within 24 hours, and suppress the company domain when the reply came from a decision maker.

## Consistency check

Provider interest flags are set by hand and are usually incomplete. If the provider's "interested" count is lower than your `positive_interested` count, trust your labels and note the gap. If it is higher, find the replies you missed before reporting.

## Safeguard actions

| Trigger | Action |
|---|---|
| Hostile above 0.3% of delivered | Pause recommendation, review list source and copy for legal or tone problems |
| Unsubscribe above 2% of delivered | Pause recommendation, check for list-source mismatch and missing opt-out text |
| Positives at zero with 500 or more delivered and reply rate above 3% | Stop recommendation, reply-vanity trap |
| Referrals above 10% of positives | Persona is wrong; route to `refine-icp` with the referred titles |
