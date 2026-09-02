# KPI hierarchy and denominators

Rank campaigns, variants, and owners by the highest metric in this list that has enough sample to be trusted. Never rank by a lower metric when a higher one is available.

## The hierarchy

| Rank | Metric | Formula | What it tells you |
|---|---|---|---|
| 1 | Opportunities per 1k sent | opportunities / sent × 1,000 | Revenue intent per unit of outreach. The only metric that pays. |
| 2 | Meetings per 1k sent | meetings / sent × 1,000 | Pipeline progression. Drops to zero when the handoff process is broken, not when copy is bad. |
| 3 | Positives per 1k sent | positive replies / sent × 1,000 | Best early proxy for rank 1 and 2 when deals take weeks to appear. |
| 4 | Positive reply rate | positive replies / delivered | Same signal, different denominator. Use for cross-provider comparison. |
| 5 | Positives per reply | positive replies / human replies | Reply quality. Separates curiosity from intent. |
| 6 | Reply rate | human replies / delivered | Engagement only. Easy to inflate with curiosity hooks and breakup emails. |
| 7 | Open rate | not used | Pixel blocking and privacy proxies make it noise. Deliverability hint at best. |

## Denominator rules

- `sent` counts every message delivered to the provider for sending, including follow-up steps.
- `delivered` = `sent` minus `bounced`.
- `contacted` (unique leads first touched) is a different denominator. Some provider UIs use it for reply rate, which inflates the rate relative to `sent`. State which one you use and never mix them in one table.
- Out-of-office and automatic replies are never in the reply numerator. If the provider reports human and automatic replies separately, use the human count. If it reports one blended number, classify the replies yourself before computing a rate.
- Bounces are removed from reply denominators and counted in their own rate.
- Per-1k values always use `sent`, so a campaign cannot improve its score by bouncing more.

## Why reply rate is not the goal

Reply rate rewards messages that provoke a response of any kind. Three patterns inflate it without producing revenue:

1. Reminder-style follow-ups that restate an earlier message. They earn polite replies and near-zero opportunities.
2. Curiosity openers with no context. They earn "what is this?" replies that end after one exchange.
3. Breakup emails. They earn "not now" replies that count as engagement and convert at the lowest rate of any step.

A campaign with a reply rate well above the fleet average and zero positives at usable certainty is not a copy-iteration candidate. It is a stop.

## Silent conversions

Some calls to action convert outside the reply channel, for example a phone number or a self-serve link. Those variants show lower reply and positive rates while producing opportunities. Judge them on rank 1 and 2 only, and instrument the channel (a dedicated number or link per variant) so the conversion can be attributed. Until that exists, label the comparison "not comparable".

## Certainty tiers

| Sends per unit | Tier | Allowed claim |
|---|---|---|
| below 200 | too early | none; report the count only |
| 200 to 499 | directional | "looks better/worse", no decision unless a safeguard tripped |
| 500 to 1,999 | usable | continue/change/stop against the rule |
| 2,000 or more | solid | may be promoted to a validated learning |

Opportunity and meeting rates need more sample than reply rates because base rates are ten times smaller. Expect 1,000 or more sends per arm before comparing opportunities per 1k between variants.

## Reading a ranking

1. Sort by opportunities per 1k where every row is at least usable.
2. Break ties by positives per 1k.
3. Show reply rate as context, never as the sort key.
4. Show the certainty tier in the row. A directional row never outranks a usable row in a decision.
