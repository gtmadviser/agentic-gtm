---
name: audit-deliverability
description: Read-only audit of sending domains, DNS, mailbox fleet health, warm-up, list verification, inbox placement, bounce and reply signals, and domain burn risk, with every finding classified as blocking, material, or informational. Use before any campaign launch, at the weekly deliverability checkpoint, or whenever bounce, placement, or reply metrics move; do not use to provision, delete, modify DNS, activate warm-up, change campaign state, or send.
---

# Audit Deliverability

> Deliverability is the part of the engine that decides whether anything else matters. This skill sits between Reach and Measure in the pipeline (Research → ICP → Source → Personalize → Reach → Measure → Iterate). It reads the fleet, compares it with numeric thresholds, and produces a findings report with an owner and a verification step per finding. It never changes infrastructure. The irreversible step is always a human decision taken after the audit.

## When to use / when not to

Use it:
- Before a campaign plan is applied (`gtm campaign plan` should not run until the last audit is green).
- At the weekly checkpoint, before `weekly-gtm-review`.
- When bounce rate, placement, or reply rate move by more than the thresholds in `references/thresholds.md`.
- Before launching a new market, persona, or mailbox fleet (see `references/launch-gates.md`).
- When someone proposes retiring or replacing domains or mailboxes. Run the burn method first.

Do not use it:
- To buy domains, create or delete mailboxes, change DNS, enable or disable warm-up, pause or activate campaigns, or send test emails. Those are separate, approved, dry-run-first operations outside this skill.
- To explain reply rate from open rate. Open tracking is unreliable and often disabled. Opens are never evidence.
- On a fleet that has sent fewer than 80 emails per domain. Report "insufficient data", not a verdict.

## Inputs

| Source | What to read |
|---|---|
| `gtm.yaml` | `providers.sequencer`, scopes, policies |
| `gtm --json doctor` | Which credentials and which store are available |
| `gtm --json sync campaigns` | Campaign state and, where supported, campaign metrics into the store |
| Store table `campaign_metrics` | sent, delivered, bounced, replied, positive replies per campaign and window |
| Sequencer API (read-only) | mailbox list with status, warm-up score, daily limit, sending gap; campaign sender lists; placement test results |
| Mailbox provider API (read-only) | mailbox inventory per domain, warm-up state, DNS records |
| DNS resolvers | SPF, DKIM, DMARC, tracking-domain CNAME, root A record, redirect target |
| `.gtm/deliverability/` | Prior audit CSVs and the watchlist state file |
| `reports/deliverability-*.md` | Prior findings, so this audit reports changes, not just state |
| `experiments/*.json` | The active experiment's safeguards (daily cap, bounce stop rule) |

The v0.2 runtime has no mailbox-fleet command. Pull inventories with the provider APIs into `.gtm/deliverability/` (gitignored). Git receives aggregates by provider group, never addresses.

## Procedure

1. **Fix the scope and coverage.** State which providers, domains, markets, and date window the audit covers. Anything that has not sent in the window is "unjudged", listed separately, and never given a verdict.
2. **Inventory the fleet** into `.gtm/deliverability/mailboxes.csv` and `domains.csv`: one row per mailbox with provider group, domain, status, warm-up score, daily limit, campaigns assigned, sends and replies in window. Count mailboxes per domain. Flag any domain above 2.
3. **Check DNS on every sending domain**: SPF present with one `-all` or `~all`, DKIM selector resolving, DMARC policy present, custom tracking domain CNAME pointing at the sequencer's host (not the shared default), root and `www` A records present, and a redirect to the real website. Verify at the authoritative nameserver, not a cached resolver. Never trust a provisioning script's "record exists" summary.
4. **Check warm-up and capacity**: warm-up active on every mailbox that is not yet sending; warm-up age in days; score; daily limit within 20 to 30; sending gap 8 to 12 minutes. List every mailbox on a campaign with score under 90, warm-up under 14 days, or a wrong persona for its campaign.
5. **Check verification and bounces**: was 100% of every active list verified before send? Compute bounce rate per campaign, per sender, and per provider group from `campaign_metrics` or the sequencer's analytics. Compare with 2% overall and 5% per sender.
6. **Read placement tests**: pull the latest completed test per provider group via the API. Report aggregate inbox rate, then the per-recipient-ESP split, then per-sender only where one ESP is not uniformly broken, then SPF, DKIM, and DMARC pass rates. Method in `references/placement-tests.md`.
7. **Run the reply-rate rotation logic**: per mailbox, sends versus human replies in window. Stage 1 watch at 50 sends with 0 human replies, stage 2 flag at 100 sends with 0 human replies. Bottom 10% by bounce rate are rotation candidates. Persist the watchlist in `.gtm/deliverability/watchlist.json`, never delete it.
8. **Run the burn test at the domain level** with `references/burn-detection.md`. Output four buckets: burned candidate, healthy, insufficient data, recovered since last audit. Cross-check every burned candidate against the live sequencer inbox before it appears in the report.
9. **Classify every finding** as blocking, material, or informational. Attach the evidence row, an owner, and the exact command or query that verifies the fix.
10. **Write the report** to `reports/deliverability-YYYY-MM-DD.md` using the output contract below. Recommend reversible actions first: remove a mailbox from a campaign before deleting it, pause before retiring, re-test before replacing.
11. **Update the register**: append the audit date, the counts per bucket, and any retracted verdicts to `strategy/decisions.md` if a decision was taken, otherwise to the report only.

## Hard rules

1. This skill is read-only. It never creates, deletes, pauses, resumes, activates, provisions, or configures anything. It does not send test emails.
2. Never send cold email from the company's primary domain. Sending domains are lookalike secondary domains on `.com`, redirecting to the real site.
3. Maximum 2 mailboxes per sending domain for new provisioning. Existing 3 or 4 are grandfathered and flagged material.
4. 20 to 30 sends per mailbox per day. Size the fleet at 20. Sending gap 8 to 12 minutes.
5. Warm up 2 to 3 weeks before the first cold send. Never under 10 to 14 days. A mailbox joins a campaign only after warm-up is verified active and aged.
6. Drop any mailbox with a warm-up score under 90 from a build. Verify warm-up is actually running by re-reading the provider, because start calls can return success and do nothing.
7. Verify 100% of a list before it is sent. Unverified lists have produced 7% to 29% bounce and killed domains.
8. Bounce above 2% on a campaign, or above 5% on one sender, is a blocking finding: pause that campaign or sender, re-verify, swap the sender.
9. Placement pass bar: at least 80% inbox on the primary consumer ESP per provider group and no provider group in spam majority. A launch needs a passing test under 7 days old.
10. Judge burn at the domain level, never per mailbox, and never on fewer than 80 sends. A burn verdict is a candidate until the live inbox cross-check confirms 0 replies.
11. The irreversible step is never automated. Deleting mailboxes, cancelling subscriptions, or retiring domains happens only after a human reads the report and the verdict survived a second window.
12. Diagnose from bounces, replies, placement, and auth results. Never from open rate alone.
13. Metered tests cost credits. Pulling existing results is always fine. Creating a new metered test needs explicit approval.
14. Mailbox addresses, domain lists, and per-mailbox rows stay in `.gtm/` or the store. Git receives aggregates by provider group.

## Checklist

Pre-launch (all must pass; any open box is blocking):
- [ ] Every sending domain has SPF, DKIM, DMARC, custom tracking domain, root and www A records, and a redirect to the real site, verified authoritatively.
- [ ] No sending domain is the primary company domain.
- [ ] No domain carries more than 2 mailboxes.
- [ ] Every campaign mailbox has warm-up score 90 or higher and at least 14 days of warm-up, ideally 21.
- [ ] Every campaign mailbox has a non-empty signature matching its persona.
- [ ] Daily limit 20 to 30 and sending gap 8 to 12 minutes on every mailbox.
- [ ] 100% of the list verified; suppression and bounced lists applied.
- [ ] Placement test per provider group under 7 days old, 80% or higher inbox, no spam-majority group.
- [ ] Ramp plan written: about 25% of daily cap on day 0, full cap over about 10 days.
- [ ] Monitoring cadence wired for the new campaign (health check, performance check, placement, reply-rate rotation).
- [ ] T+1, T+3, T+7 checks scheduled with owners.

Weekly:
- [ ] Bounce per campaign, per sender, per provider group compared with thresholds.
- [ ] Reply-rate watchlist advanced; stage-2 flags reported.
- [ ] Placement results pulled and split by recipient ESP.
- [ ] Burn buckets recomputed; recovered domains un-flagged.
- [ ] Unjudged fleet listed with the reason.

## Output contract

- `reports/deliverability-YYYY-MM-DD.md` (Git, aggregates only) with sections in this order: Scope and coverage caveat · Findings table (severity, finding, evidence, owner, verification step) · Fleet aggregates by provider group (mailboxes, warm-up median, sends, bounce, reply) · Thresholds compared (table from `references/thresholds.md` with actual values) · Placement by provider group and recipient ESP · Burn buckets with counts · Recommended actions, reversible first · Unjudged and why · Changes since last audit.
- `.gtm/deliverability/mailboxes.csv`, `domains.csv`, `placement-YYYY-MM-DD.csv`, `watchlist.json` (local, gitignored). The watchlist is stateful and is never deleted.
- Store table `campaign_metrics` refreshed by `gtm --json sync campaigns` or `gtm metrics import --file <csv>` before the audit reads it.
- Severity definitions: **blocking** stops a launch or an active campaign today; **material** must be fixed within the week and has an owner; **informational** is recorded for trend.
- Every finding names one owner and one verification step that a second person can run.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Bounce spike on one campaign, other campaigns fine | Unverified or stale list segment | Pause the campaign, re-verify, remove bounced rows, resume with ramp |
| Bounce spike on one sender across campaigns | Mailbox connection error, provider block, or domain listed | Remove the sender from campaigns, check auth and blacklist status, swap in a spare |
| Placement 100% spam at one recipient ESP for a whole provider group | Provider-level reputation or auth failure at that ESP | Treat the group as blocked for that ESP; fix auth; do not rank individual senders |
| Zero replies on a young domain at 100 sends | Often chance, sometimes burn | Bucket "insufficient" or "candidate"; re-judge at the next window; do not retire |
| Replies fine, "opens" near zero | Open tracking disabled or blocked | Ignore opens; nothing to fix |
| Warm-up shows active in the dashboard, score 0 after export | Export carried config but not the enable toggle | Re-enable warm-up in batches; re-read to verify |
| DNS records "exist" per script, missing at the resolver | Records posted before the zone existed, orphaned | Fix in the provider UI; verify with `dig` at the authoritative nameserver |
| Whole fleet went quiet on a schedule | Scheduler died silently (missed runs, blocked log path, machine asleep) | Check the last log timestamp; use a scheduler that catches up missed runs; log outside protected user folders |
| Domain flagged burned last month replies normally now | False positive on a short window | Un-flag, record the retraction, keep the domain |

## References

- [thresholds.md](./references/thresholds.md), every number in one table
- [mailbox-fleet.md](./references/mailbox-fleet.md), sizing formula, domain strategy, warm-up, rotation
- [placement-tests.md](./references/placement-tests.md), how to run and read inbox placement tests
- [burn-detection.md](./references/burn-detection.md), the domain-level burn method and the false-positive rule
- [incident-response.md](./references/incident-response.md), triage steps per incident type
- [launch-gates.md](./references/launch-gates.md), the stage model for a new market or fleet

Licensed CC BY 4.0 by GTM Adviser.
