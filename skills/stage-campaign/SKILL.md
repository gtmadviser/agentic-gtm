---
name: stage-campaign
description: Turn reviewed copy and an approved audience into a CampaignDraft, run the mandatory pre-launch filters, create an immutable action plan, and apply it to lemlist or Instantly in paused state only. Use after write-outreach and the experiment are approved; never use to activate, send, add contacts, or bypass explicit apply approval.
---

# Stage Campaign

> Takes a reviewed copy set and an approved audience and produces a paused campaign shell in the sequencer, with an audit trail in Git and the store. This is the Reach stage of the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate), stopped one step before sending. The system creates campaigns paused and cannot activate them. A human launches from the provider UI after the pre-launch checklist, and only then.

## When to use / when not to

Use this skill to:
- assemble a `CampaignDraft` JSON from `campaigns/<slug>-copy.md` and the approved audience query
- run the mandatory pre-launch filters on the recipient pool
- create an immutable plan, present it, and apply it after explicit approval
- verify the provider reports the campaign as draft or paused

Do not use it:
- before `write-outreach` produced a copy file with a rubric score of 85 or above
- to activate, resume, schedule sends, add recipients, or assign senders (none of these exist in the CLI on purpose)
- to change a running campaign someone else owns
- to bypass a failed filter because the launch date is close

## Inputs

| Source | What you take from it |
|---|---|
| `campaigns/<slug>-copy.md` | steps, variants, hypotheses, variable fill rates, rubric score |
| `experiments/<id>.json` | audience, channel, safeguards, decision rule, status `approved` |
| store tables `accounts`, `contacts` | the candidate pool with provider IDs and verification status |
| store table `campaigns` and the sending log | previously contacted, bounced, replied recipients |
| suppression lists in the store | unsubscribes, hostile replies, customers, open deals, competitors, legal exclusions |
| mailbox inventory (provider API, not the dashboard) | healthy senders, warm-up state, burned domains |
| `gtm --json next` | workspace hint; verify this experiment directly |
| `OPERATING-CONTRACT.md` | plan-then-apply, paused-only, no recipients in Git |

## Procedure

1. **Check this experiment.** Use `gtm --json next` as a workspace hint. Verify the approved audience, experiment and reviewed copy directly. The CLI detects JSON drafts, so it can still report `copy` until step 6 creates the draft; that does not block this handoff.
2. **Size the campaign.** Daily target ÷ per-mailbox cap (20-30) = mailboxes needed. Check the inventory has that many healthy, dedicated senders. If not, cut the daily target; never raise the cap.
3. **Build the recipient pool** from the audience query in the experiment. Record the count.
4. **Run the mandatory filters** in `references/pre-launch-checklist.md` section "Filters", in order. Record the count after each filter. A pool that loses more than 30 percent to bounced or previously-contacted filters is a data problem; stop and fix sourcing.
5. **Verify every address.** 100 percent of the pool goes through an email verification provider. Only `valid` (or your provider's equivalent) enters the campaign. Store the result and the provider name per contact.
6. **Assemble the draft.** Write `campaigns/<slug>.json` as a `CampaignDraft`: provider, name with a date prefix (`YYMMDD_<market>_<segment>_<angle>`), audience query, steps with variants copied verbatim from the copy file, schedule, suppression list names, `status: "paused"`. See `references/draft-schema.md`.
7. **Check structure** against `references/campaign-structure.md`: steps, variants, gaps, sends per variant, senders per campaign.
8. **Create the plan.** `gtm --json campaign plan --draft campaigns/<slug>.json`. The CLI stores an immutable plan with targets, payload summary, idempotency key, SHA-256 hash, and a 24-hour expiry.
9. **Present the plan** to the operator: provider, campaign name, number of steps and variants, schedule, the payload summary, the hash, the expiry. Ask for explicit approval by plan ID.
10. **Dry-run first.** `gtm --json campaign apply --plan <id> --dry-run` validates the plan and prints what would be sent to the provider without calling it.
11. **Apply** only with the exact returned ID: `gtm --json campaign apply --plan <id>`. The adapter creates an empty shell, pauses it, verifies paused, adds sequence content, verifies paused again. It never adds recipients or senders.
12. **Verify** in the provider: status is draft or paused, steps and variants render, variables show in the preview with a test lead. Fix in the copy file and re-stage if anything is off; never edit copy in the provider UI.
13. **Record** the plan ID, apply result, provider campaign ID, and pool counts after each filter in `campaigns/<slug>.md`. No recipient data in Git.
14. **Hand off** the pre-launch checklist (`references/pre-launch-checklist.md`) to the human who launches. Launch is a UI action by the operator. Log the launch decision, owner, and date in `strategy/decisions.md`.

## Hard rules

| # | Rule | Test |
|---|---|---|
| 1 | Campaigns are created paused and stay paused until a human launches from the UI | apply result reports `paused` or `draft`; there is no activate command |
| 2 | No plan, no write | every provider write has a plan ID and a matching hash |
| 3 | The plan is applied with the exact returned ID, once | second apply returns `already_applied` |
| 4 | Steps per campaign: 2 default for direct SMB email, 3 maximum for email-led, 7 touches maximum for LinkedIn-first | count |
| 5 | Variants per step: 3-4 maximum | count |
| 6 | Sends per variant before reading results: 500 | pool ÷ variants ≥ 500 or the test is declared directional only |
| 7 | Gap between step 1 and step 2: 3 days default | schedule |
| 8 | Re-approach window: 60 days minimum since the last touch, non-repliers only | filter on the sending log |
| 9 | One mailbox in exactly one campaign; dedicated senders per campaign | inventory check |
| 10 | A/B campaigns split senders evenly | sender count per arm within 1 |
| 11 | Daily cap per mailbox: 20-30 after warm-up; ramp from about 25 percent to full over 10 days | schedule and provider settings |
| 12 | 100 percent of recipients verified before they enter the draft | verification result stored per contact |
| 13 | Bounced recipients never re-enter a pool; the sending log is the source of truth, not a status column that may be null | filter run against the log |
| 14 | Burned sender domains never re-enter a build | filter run against the burned list |
| 15 | Bounce above 2 percent overall or 5 percent on one sender after launch: pause that campaign or sender the same day | monitoring rule in the handoff |
| 16 | Recipients, emails, phone numbers, provider IDs of people stay in the store; Git gets counts and plan references | scan the campaign notes before committing |
| 17 | The copy in the draft equals the copy file byte for byte | diff |

## Checklist

- [ ] This experiment has an approved audience and reviewed copy; readiness checked directly
- [ ] Copy file rubric score 85 or above, slop gate passed
- [ ] Experiment status `approved`, decision rule written
- [ ] Sizing done: mailboxes = daily target ÷ per-mailbox cap
- [ ] Pool built, count recorded
- [ ] Burned sender domains filtered
- [ ] Healthy verified mailboxes only, checked via API
- [ ] Bounced recipients filtered against the sending log
- [ ] Contacted within 60 days filtered
- [ ] Cross-campaign domain dedupe applied
- [ ] Suppression lists applied
- [ ] 100 percent email verification, results stored
- [ ] Draft JSON written, `status: "paused"`, name with date prefix
- [ ] Structure rules pass (steps, variants, gap, sends per variant)
- [ ] Plan created, hash and expiry presented
- [ ] Operator approved by plan ID
- [ ] Dry-run passed
- [ ] Applied once; provider reports paused or draft
- [ ] Preview with a test lead renders every variable
- [ ] Plan ID, result, counts recorded in `campaigns/<slug>.md`
- [ ] Pre-launch checklist handed to the launching human

## Output contract

| Artifact | Location | Content |
|---|---|---|
| `campaigns/<slug>.json` | Git | the `CampaignDraft`; no recipients, only the audience query |
| `campaigns/<slug>.md` | Git | plan ID, apply result, provider campaign ID, pool counts after each filter, verification provider, sender count, launch owner |
| action plan | store `action_plans` | immutable; created by `gtm campaign plan` |
| apply result | store `apply_results` | created by `gtm campaign apply` |
| recipient pool with verification status | store `contacts` | never in Git |
| `strategy/decisions.md` | Git | one line: date, campaign, who approved the plan, who launches, when |

Naming: `YYMMDD_<market>_<segment>_<angle>` for the campaign, the same slug for the files. Date prefix first so the 60-day filter can read launch dates from names if the log is missing.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Apply fails after "created empty shell" | provider returned the shell as active and the pause call failed | the adapter stops before adding content; pause or delete the empty shell manually by the reported ID, then re-plan |
| Provider shows the campaign as active after apply | provider status mapping changed | pause in the UI immediately; report the status string; do not add recipients |
| First-day bounce above 2 percent | unverified list, stale verification, or a burned domain in the sender set | pause; re-verify; swap senders; re-stage |
| Senders show warm and active in the dashboard but bounce or land in spam | dashboard state lags the API; inventory checked from the wrong place | check via API; drop any mailbox with warm-up under 14 days or a warm-up score under 90 |
| Pool shrinks by more than 30 percent at the bounced filter | sourcing pulled from a pool already burned | fix sourcing; do not launch a thin pool |
| Same company hit by two campaigns in a week | no cross-campaign domain dedupe | dedupe on company domain across all active campaigns |
| Variables render empty in the preview | fill rate checked on the wrong pool | fix in the copy file with a fallback; re-stage |
| Plan expired | more than 24 hours between plan and apply | create a new plan; never extend expiry |
| Operator asks to "just launch it" | pressure | launching is a UI action by the operator; the CLI cannot; say so and hand over the checklist |

## References

- [campaign-structure.md](./references/campaign-structure.md): steps, variants, gaps, sizing, senders, ramp
- [pre-launch-checklist.md](./references/pre-launch-checklist.md): mandatory filters, the launch checklist, monitoring rules for day 1
- [draft-schema.md](./references/draft-schema.md): annotated `CampaignDraft` JSON for Instantly and lemlist, including a LinkedIn-first variant

Licensed CC BY 4.0 by GTM Adviser.
