# Retro method

A retro turns one review into durable evidence. It produces three registers: the A/B ledger, the anti-pattern register, and the winners list. All three are JSON in `reports/retro/` and are referenced from the review report.

## Metric philosophy

- Primary: opportunities per 1k sent inside the attribution window. Define the window before the retro (for example "CRM signal within 30 days of the last touch").
- Secondary: positives per 1k sent. Use it as the early proxy when deals lag.
- Context: reply rate. Never a ranking key.
- A finding becomes a rule only if it holds under both the primary and the secondary metric and reaches solid certainty, or holds within a matched pair of campaigns at usable certainty.

## Attribution window tiers

| Tier | Definition | Weight in sensitivity view |
|---|---|---|
| in window | CRM signal within the window after a touch | 1.0 |
| unknown | signal exists, touch date missing | 0.5 |
| out of window | signal after the window | 0.3 |

Report the in-window view as the primary. Report the sensitivity view once to show the finding is not an artifact of the window.

## Step 1: A/B ledger

One entry per comparison. A comparison is valid only when both arms share list, window, sender pool, and step position, and each arm has 500 or more sends.

```json
{
  "ledger_version": 1,
  "entries": [
    {
      "id": "ab-2026-07-northstar-cost-vs-scenario",
      "experiment": "exp-2026-07-cost-framing",
      "campaign": "2026-07 Northstar Relay engineering leads",
      "arms": [
        {"variant": "A cost framing", "sent": 1240, "delivered": 1216, "positives": 14, "meetings": 5, "opportunities": 2},
        {"variant": "B scenario opener", "sent": 1198, "delivered": 1177, "positives": 9, "meetings": 2, "opportunities": 1}
      ],
      "primary_metric": "opportunities_per_1k",
      "certainty": "usable",
      "verdict": "directional for A on positives; opportunities too sparse to call",
      "status": "open",
      "decided_on": null,
      "evidence": "reports/outreach-2026-07-28.md"
    }
  ]
}
```

Status values: `open`, `closed_a`, `closed_b`, `closed_no_difference`, `not_comparable`. Closing requires the certainty tier the rule demands. Never delete an entry; supersede it with a new one that names the old id.

## Step 2: Anti-pattern register

One entry per pattern that reached usable certainty with a clearly worse result. Anti-patterns are written as prohibitions with the evidence that created them.

```json
{
  "register_version": 1,
  "anti_patterns": [
    {
      "id": "ap-reminder-followups",
      "statement": "Follow-ups that restate the first email earn replies and no opportunities.",
      "evidence": "reports/outreach-2026-06-30.md",
      "sends": 4200,
      "reply_rate": 0.061,
      "opportunities": 0,
      "certainty": "solid",
      "status": "active",
      "counter_hypothesis": null
    }
  ]
}
```

An anti-pattern can only be retired by a counter-hypothesis that closes as won. Record its id in `counter_hypothesis` and move the status to `superseded`.

## Step 3: Winners

The list of campaigns and variants that are safe to replicate. Replication of a winner into a new segment or country beats writing new copy; record each replication as its own ledger entry.

```json
{
  "winners_version": 1,
  "winners": [
    {
      "campaign": "2026-05 Copper Finch Labs partner angle",
      "variant": "partner revenue share, either/or CTA",
      "sent": 2610,
      "positives_per_1k": 9.6,
      "opportunities_per_1k": 1.5,
      "certainty": "solid",
      "replicated_to": ["2026-07 Quiet Harbor Systems partner angle"],
      "notes": "Holds in both attribution views."
    }
  ]
}
```

## Step 4: New hypotheses

Every unexpected finding becomes a line in the "Next hypotheses" section of the review, phrased as "If we X, then Y, because Z", with the metric and minimum sample. `design-gtm-experiment` turns those lines into files.

## Worked example

Northstar Relay ran two variants to 2,400 engineering leads over three weeks. Variant A framed the cost of the problem in the opener. Variant B opened with a scenario. Both used the same either/or call to action and the same sender pool.

1. Rule frozen: "Continue if positives per 1k is at least 8 on 1,000 or more sends per arm; stop if below 4; otherwise change one variable."
2. Data verified: window matched, one row per arm, delivered excludes 47 bounces, provider counts auto-replies separately.
3. Computed: A 11.3 positives per 1k, B 7.5 positives per 1k, both usable. Bounce 1.9%, hostile 0%, unsubscribe 0.3%.
4. Replies classified: A had 14 positives out of 39 human replies (36% positives per reply); B had 9 out of 41 (22%).
5. Verdict: continue with A. B is above the stop line, so B is "change", not "stop".
6. Ledger entry recorded as directional for A on positives; opportunities too sparse to close.
7. Learnings line: "2026-07-28: cost framing in the opener beat a scenario opener on positives per reply in a matched pair at usable certainty. Evidence: reports/outreach-2026-07-28.md."
8. Next hypothesis: "If we keep A and move the scenario into the second paragraph, positives per 1k stays at 10 or more, because the cost hook is doing the work."

## What a retro never does

- It never rewrites a winner into "more professional" copy without a ledger entry. Polishing has destroyed working variants before.
- It never promotes a finding from a single campaign to a fleet rule.
- It never changes the window after the deals are counted.
