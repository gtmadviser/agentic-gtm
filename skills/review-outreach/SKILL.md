---
name: review-outreach
description: Turn synced or imported campaign results into evidence, classify replies, and judge each experiment only against its preregistered decision rule. Use after an experiment window or minimum sample is reached and before any scale, iterate, or kill decision; do not use to declare success from opens, tiny samples, or a changed denominator.
---

# Review Outreach

> This is the Measure stage of the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate). It converts provider counts and reply text into approved aggregates, compares them with the rule the experiment wrote down before launch, and records the outcome so the next campaign starts from evidence instead of memory. It never touches campaign state.

## When to use / when not to

Use when:

- An experiment has reached its preregistered minimum sample or its time window closed.
- A safeguard may have tripped (bounce, hostile replies, unsubscribes) and the operator needs a verdict.
- The weekly review needs campaign evidence, or a campaign is up for a scale, iterate, or kill call.

Do not use when:

- Fewer than 200 sends exist for the unit under review. Report "too early" and stop.
- The only signal is open rate. Opens are not a metric in this system.
- Someone wants to change the denominator, window, or decision rule after seeing results. That requires a new experiment version via `design-gtm-experiment`.
- The request is to activate, expand, or edit a campaign. This skill is read-only toward providers.

## Inputs

| Source | What it provides |
|---|---|
| `experiments/<id>.json` and `.md` twin | Denominator, minimum sample, window, safeguards, decision rule, linked campaign names |
| `campaigns/*.json` | Which variants exist and which experiment each campaign belongs to |
| `gtm --json sync campaigns` | Campaign state plus `campaign_metrics` rows where the provider exposes analytics |
| `gtm --json metrics import --file <csv>` | Counts for providers without analytics, LinkedIn steps, calls, or manual channels |
| `gtm --json review outreach` | Computed rates, per-1k values, certainty tier, bounce flag, Markdown report skeleton |
| Reply exports (store or `.gtm/`) | Text for reply classification; never copied into Git |
| `strategy/learnings.md` | Existing validated and anti-learnings to check the result against |

## Procedure

1. **Freeze the rule first.** Open the experiment file. Copy its denominator, minimum sample, window, safeguards, and continue/change/stop rule verbatim into the top of the review draft before reading any number. If any of these is missing, stop and route to `design-gtm-experiment`; a review without a preregistered rule is an observation, not a verdict.
2. **Refresh the data.** Run `gtm --json sync campaigns`. For channels the provider does not report (LinkedIn touches, calls, a sequencer without an analytics adapter), build a CSV in the format in `references/metrics-csv.md` and run `gtm --json metrics import --file <csv>`. One row per provider, campaign, variant, and window.
3. **Verify before interpreting.** Check that the window in the data equals the window in the experiment, that each campaign and variant appears once per window, that `sent` is the denominator the experiment named, and that the provider's "replied" definition is known (some providers count auto-replies inside reply rate, some report them separately). Write the checks and any gaps into a "Data quality" section. Missing data lowers confidence; it never becomes a zero.
4. **Compute.** Run `gtm --json review outreach --output reports/outreach-<YYYY-MM-DD>.md`. Read bounce rate, reply rate, positive reply rate, positives per 1k sent, meetings per 1k, opportunities per 1k, and the certainty tier per campaign and variant. Rank by the KPI hierarchy in `references/kpi-hierarchy.md`, never by reply rate.
5. **Classify replies.** Where reply text is available, label every reply with exactly one of the ten labels in `references/reply-taxonomy.md`. Remove out-of-office and bounce from reply denominators. Store labels in the store or `.gtm/`, and report only counts.
6. **Attribute correctly.** Attribute each campaign to its owner using the owner or creator field from the provider API. Never derive ownership from a campaign name. Exclude shared or template campaigns and service accounts from per-owner metrics, and mark campaigns without an owner field as unattributed.
7. **Check safeguards.** Apply the thresholds in Hard rules. A tripped safeguard produces a "pause and investigate" recommendation regardless of performance.
8. **Judge against the rule.** Produce exactly one of: continue, change, stop, or "inconclusive, extend" when the sample is below the minimum and no safeguard tripped. Quote the rule, the observed value, the certainty tier, and the sample next to the verdict.
9. **Run the retro.** Fill the A/B ledger, anti-pattern register, and winners list in `references/retro-method.md`. Treat every unexpected finding as a new hypothesis, not a conclusion.
10. **Record.** Update the experiment file (status, result, decision, date, owner). Append one dated line per closed finding to `strategy/learnings.md`. Save the aggregate report under `reports/`. Present the verdict to the operator; the operator decides what happens to the campaign.

## Hard rules

1. Minimum 200 sends per unit before any rate is reported as more than "too early".
2. Certainty tier by sends: below 200 too early, 200 to 499 directional, 500 to 1,999 usable, 2,000 or more solid. A rule is only "confirmed" at solid.
3. Denominators: bounce rate = bounced / sent. Reply rate = human replies / delivered, where delivered = sent minus bounced. Positive reply rate = positive replies / delivered. Positives per 1k = positive replies / sent × 1,000. Out-of-office and bounces are never replies.
4. The denominator, window, and decision rule are fixed at preregistration. Changing any of them after seeing results requires a new experiment version and a note in `strategy/decisions.md`.
5. Positive reply rate benchmarks for cold email: 1% or more is good, 2% or more is great. Below 0.5% at usable certainty means the list or the angle is wrong, not the subject line.
6. Safeguards: bounce above 2% overall or above 5% for any sender pauses the campaign. Hostile replies above 0.3% of delivered or unsubscribes above 2% of delivered pause the campaign and trigger an investigation.
7. A high reply rate with zero positives or zero opportunities at usable certainty is the reply-vanity trap. Verdict: stop. Do not iterate copy on a campaign that harvests curiosity without intent.
8. Attribution comes from the provider's owner field. Name-based attribution is prohibited.
9. Opens are excluded from every ranking and every verdict. They may appear only in the data quality section as a deliverability hint.
10. Variant comparisons require at least 500 sends per variant and the same window, list, and sender pool. Otherwise report "not comparable".
11. Nothing in this skill activates, expands, edits, or pauses a campaign through the API. Recommendations go to the operator.

## Checklist

- [ ] Experiment rule, denominator, window, and safeguards copied verbatim before reading data
- [ ] `gtm --json sync campaigns` run, or metrics imported from CSV for uncovered channels
- [ ] Window in data equals window in experiment
- [ ] One row per provider, campaign, variant, window
- [ ] Provider "replied" definition documented
- [ ] Replies classified with the ten-label taxonomy; OOO and bounces removed from reply denominators
- [ ] Attribution taken from provider owner field; shared campaigns excluded
- [ ] Safeguards checked against thresholds
- [ ] Certainty tier stated next to every rate
- [ ] Verdict is one of continue, change, stop, or inconclusive and quotes the rule
- [ ] A/B ledger, anti-patterns, and winners updated
- [ ] Experiment file, learnings log, and report written; no raw replies, emails, or lead rows in Git

## Output contract

| Artifact | Location | Content |
|---|---|---|
| Review report | `reports/outreach-<YYYY-MM-DD>.md` | Frozen rule, data quality, computed aggregates with certainty tier, safeguard status, verdict, ledger entries, next hypotheses |
| Experiment update | `experiments/<id>.json` (`status`) and `.md` twin (results, result label, decision, date, owner) | Status moves to `complete` only on a continue, change, or stop verdict |
| Learnings | `strategy/learnings.md` | One dated line per closed finding with an evidence pointer to the report |
| Metrics | store table `campaign_metrics` | Counts per provider, campaign, variant, window |
| Reply labels | store or `.gtm/replies/` | Per-reply label and provider ID; never in Git |
| Decision record | `strategy/decisions.md` | Only when the operator changes the rule, retires a campaign, or scales one |

Reports contain aggregates only. Contact names, email addresses, reply text, and provider IDs stay in the store.

## Verdict format

Every review ends with one block in this shape, placed directly under the frozen rule:

```
Rule (frozen 2026-07-07): continue if positives per 1k >= 8 on >= 1,000 sends per arm; stop if < 4.
Observed (2026-07-28): A 11.3 per 1k on 1,240 sends (usable); B 7.5 per 1k on 1,198 sends (usable).
Safeguards: bounce 1.9%, hostile 0.0%, unsubscribe 0.3%. None tripped.
Verdict: continue A; change B (one variable, new version).
Owner and date: operator name, decision due 2026-07-30.
```

A verdict without the observed sample and tier is incomplete and must not be sent to the operator.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Reply rate above 5% but zero positives at 500+ sends | Curiosity or reminder-style copy, or auto-replies counted as replies | Reclassify replies; if positives stay at zero, verdict is stop |
| Reply rate collapses to near zero on a campaign that used to work | Deliverability problem, not copy | Route to `audit-deliverability` before touching copy |
| Positives exist but meetings stay at zero for two or more reviews | Process gap in the interested-to-meeting handoff | Flag "process gap" in the review; do not blame messaging |
| Variant A beats variant B by a large margin on 80 sends each | Sample far below comparison minimum | Report "too early", extend, do not pick a winner |
| Totals differ between the provider UI and the CLI | Different denominators (unique leads vs sends) or auto-replies included | Document both definitions, pick the experiment's, label the other unresolved |
| A campaign shows no owner | Provider record lacks a creator field | Mark unattributed; never guess from the name |
| Numbers moved after the review was written | Provider recounted or window shifted | Re-run with the frozen window; supersede the report, do not edit it in place |
| Metrics import rejected | Column names or date formats wrong | Follow `references/metrics-csv.md` exactly; ISO dates, integers only |

## References

- [KPI hierarchy and denominators](./references/kpi-hierarchy.md)
- [Reply taxonomy and benchmarks](./references/reply-taxonomy.md)
- [Retro method, ledger schema, worked example](./references/retro-method.md)
- [Metrics CSV import format](./references/metrics-csv.md)

Licensed CC BY 4.0 by GTM Adviser.
