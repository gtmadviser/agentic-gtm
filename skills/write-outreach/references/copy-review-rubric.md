# Copy review rubric

Run this on every step and every variant before `stage-campaign`. Hard gates first. Any failed gate ends the review; fix and rerun. Then score 0-100.

| Score | Verdict |
|---|---|
| 85 or above | ship |
| 70-84 | one more pass on the lowest-scoring dimensions |
| below 70 | restart from the angle, not from the wording |

## Hard gates

A single failure fails the review. No partial credit.

| Gate | Check |
|---|---|
| G1 | No em dash (U+2014) or en dash (U+2013) anywhere; no hyphen as punctuation if the voice override forbids it |
| G2 | No link, no attachment, no brand domain in touch 1 |
| G3 | Every `{{variable}}` is a column that exists in the store with 100 percent fill on the pool, or has a written fallback |
| G4 | Word count 40-70 per email (up to 90 only with a written justification in the copy file); LinkedIn messages under 40 |
| G5 | Every number has a source the recipient could ask for |
| G6 | One address form per message and per pool; formal pools have a filled salutation column |
| G7 | Explicit opt-out path present, one word to use it |
| G8 | Subject: 6 words or fewer, no `Re:`, no `Fwd:`, no emoji, no capitals-only words |
| G9 | Line 1 could not be true for 10,000 other recipients |
| G10 | No feature list (three or more features in one sentence) |
| G11 | Follow-up does not restate step 1's features or pain |
| G12 | No placeholder text (`TODO`, `TBD`, `[insert`, `lorem`, `xxx`) |
| G13 | Slop gate: the nine-step check in `anti-slop-writing.md` passes with zero hits (no substitute kickers, no triads, no "not just", no forced contrasts, no pivot pairs, no hook questions, no abstract noun stacks, no adjective spirals, no intensifiers, no opener or sign-off clichés, one claim per sentence, every specific claim verified) |

## Scoring dimensions

| # | Dimension | Weight | 0 | half | full |
|---|---|---|---|---|---|
| 1 | Relevance of line 1 | 15 | generic pain opener | company-specific but interchangeable within the segment | verifiable, rare detail about this recipient |
| 2 | What-it-is clarity | 10 | reader cannot say what you sell | product named but with jargon | one plain verb-first sentence |
| 3 | One angle | 10 | two or more angles | one angle with a second hinted | one angle, one why-now |
| 4 | Length and structure | 10 | over 90 words or more than 3 paragraphs | inside the band but dense | 40-70 words, three scannable paragraphs or fewer |
| 5 | Subject line | 10 | product hook or newsletter syntax | acceptable fragment, weak fit with body | internal note or intrigue, matches line 1 |
| 6 | CTA friction | 10 | calendar link or vague "let me know" | clear ask, still costs a sentence | one word or one letter answers it, and the ask explains itself |
| 7 | Proof quality | 5 | famous logo or unsourced figure | relevant but distant proof | local or same-trade proof, one point, verifiable |
| 8 | Voice and naturalness | 10 | translated or corporate | mostly natural, one business word | reads like a chat message from a peer; native |
| 9 | Variable safety | 5 | can render empty | fallback exists but reads clumsy | fallback reads as well as the filled version |
| 10 | Follow-up independence | 5 | needs step 1 to make sense | stands alone, same angle | stands alone, new angle, passes 3-D |
| 11 | Deliverability hygiene | 5 | spam vocabulary, symbols, multiple links | clean but spintax stitched | clean, sentence-level spintax at most, plain text |
| 12 | Variant hypothesis | 5 | no hypothesis or wording-only difference | hypothesis stated, weakly testable | one change on purpose, hypothesis names the metric |

Total: 100.

## Worked example

Fictional. Harbor Metrics (harbormetrics.example) flags failed deliveries for online shops before the customer complains. Recipient: owner of Juniper Bikes (juniperbikes.example), an online bike shop with 4.7 stars and 412 reviews. Pool fill: `firstName` 100 percent, `rating` 96 percent with fallback, `reviewCount` 96 percent with fallback.

### Draft before review

Subject: `Improve your delivery experience at Juniper Bikes`

> Hi Mara,
>
> I hope this finds you well! I noticed Juniper Bikes is growing fast, congrats. Many e-commerce brands struggle with failed deliveries, damaged parcels and slow refunds, which hurts customer satisfaction and revenue.
>
> Harbor Metrics is the leading delivery-intelligence platform that helps brands like yours reduce WISMO tickets by up to 43%, improve NPS and boost repeat purchases through seamless carrier integrations.
>
> Do you have 15 minutes next week for a quick call? Here is my calendar: https://harbormetrics.example/book
>
> Best, Sam

Gates: G2 fails (link, brand domain). G5 fails ("up to 43%" has no source). G8 fails (8 words, product hook). G9 fails (line 1 fits anyone). G10 fails (feature list). G13 fails (opener cliché, adjective spiral, "brands like yours"). Review ends. Word count 88.

### Rewrite

Subject: `mara, saturday orders`

> Mara, one of your reviews from March says the bike arrived "boxed up fine, but ten days late and nobody told me". At 412 reviews that probably is not the only one.
>
> We built a tool that spots a stuck parcel the day it stalls and messages the customer before they ask.
>
> Want the list of your last month's late ones? Reply "list". Or "no" and I stop.
>
> Sam

Fallback for `rating` and `reviewCount`: "With that many reviews that probably is not the only one."

Gates: all pass. 63 words. Scores: 1: 15, 2: 10, 3: 10, 4: 10, 5: 9, 6: 10, 7: 4 (the review is the proof; no peer yet), 8: 9, 9: 5, 10: n/a for step 1 (award 5), 11: 5, 12: 4 (hypothesis: "verbatim review opener beats scenario opener on positive replies", control is variant B). Total 96. Ship.

### The variant set

| Variant | Change | Hypothesis |
|---|---|---|
| A (above) | verbatim review opener | rare verifiable detail lifts positive reply rate over the scenario opener |
| B (control) | scenario opener: "Saturday order, Monday dispatch, Thursday the customer emails 'where is it'" | the control from the last campaign |
| C | ultra-short, 22 words: "Mara, ten-day delivery in a March review. We flag stuck parcels the day they stall. Want last month's list? Reply 'list'." | brevity as pattern interrupt on this segment |

Step 2, day 3, same thread, empty subject, angle 1 (one-line question):

> Wrong person, or wrong problem? If someone else looks after shipping at Juniper Bikes, a name is enough.

## Review log

Record in the copy file header: `rubric_score`, `reviewed_by`, date, and which gates were fixed during review. The learning log gets one line only if the review changed the angle.
