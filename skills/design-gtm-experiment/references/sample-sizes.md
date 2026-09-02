# Sample sizes

Base rates in cold outbound are small, so samples must be large. These rules are floors, not targets.

## Floors by claim

| Claim | Floor | Why |
|---|---|---|
| "This reply rate is real" | 200 sends per unit | Below 200, one extra reply moves the rate by half a point |
| "Variant A beats variant B" | 500 sends per arm, same window and list | Variant differences are usually under 1 point |
| "This meeting or opportunity rate is real" | 50 replies, or 1,000 sends | Rates near 0.1% to 1% need more than a few events |
| "This is a rule for the fleet" | 2,000 sends and a matched pair or two campaigns agreeing | A single campaign carries its list and sender confounds |
| "This channel is worth testing further" | 25 to 50 leads per variant | Enough to see whether any signal exists at all; not enough to compare copy |

## Channel before copy

Run a small channel test first: 25 to 50 leads per variant on two or three channels or sequence shapes, same audience, same core message. Pick the channel with the most positives per lead. Then run the copy experiment at full sample on that channel. Copy tests on a channel the audience ignores waste the whole budget.

## Approximate per-arm samples for a two-arm comparison

Two-sided test, 5% significance, 80% power. Values are rounded; use them to size, not to prove.

| Baseline rate | Improvement you want to detect | Sends per arm |
|---|---|---|
| 0.5% | to 1.0% | 4,700 |
| 1.0% | to 1.5% | 8,900 |
| 1.0% | to 2.0% | 2,300 |
| 2.0% | to 3.0% | 3,900 |
| 2.0% | to 4.0% | 1,100 |
| 5.0% | to 7.5% | 1,400 |
| 5.0% | to 10.0% | 430 |
| 10.0% | to 15.0% | 690 |

Reading the table: a positive reply rate near 1% needs more than 2,000 sends per arm to detect a doubling with confidence, and nearly 9,000 to detect a 50% lift. Opportunity rates near 0.1% cannot be compared between variants at any practical sample; use positives per 1k as the primary metric and treat opportunities as supporting evidence.

## Directional reads

When the table's sample is out of reach, the experiment may still run with a directional decision rule, provided the rule says so: "directional at 500 per arm; a ratio above 2.0 is treated as a signal to extend, not as a win". Directional findings never enter the learnings log as validated.

## Time windows

- Reply windows: 90% of human replies to a step arrive within 7 days of that step. A two-step sequence with a 3-day gap needs at least 14 days after the last send before the reply count is stable.
- Opportunity windows: define the attribution window before launch, for example 30 days after the last touch, and hold it fixed.
- A window that ends before the minimum sample is reached produces "inconclusive, extend", not a verdict.

## Capacity check

Sample per day = active senders × sends per sender per day × share assigned to this experiment. Check that the minimum sample fits inside the window with the daily new-contact cap. If it does not, extend the window or widen the audience before approval.

## Stopping early

Only a safeguard trip stops an experiment early. A strong-looking result at 30% of the minimum sample is not a reason to stop; it is a reason to keep going.
