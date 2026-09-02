# Operator routine

The minimum routine that keeps an outbound engine healthy. Adapt the weekday labels to the actual schedule of the automations, but keep the order: health first, replies second, decisions last.

## Daily (15 minutes)

Morning:
1. `git status --short --branch`. Pull with rebase only if the tree is clean.
2. Read the last log line of every scheduled job. A missing line is an incident, not a quiet day.
3. Scan the sequencer for anomalies: bounce spikes, campaigns that stopped, senders in error.
4. Scan the CRM and the reply inbox for urgent replies, booked meetings, and customer-protection events (a prospect became a customer, a customer complained).
5. If a campaign launched in the last 3 days, check sends against the ramp plan, bounce, and reply handling.

Before changing any campaign:
1. Resolve the live campaign ID from the sequencer or the store, never from a hardcoded list.
2. Confirm the sender pool by persona and provider group from the registry.
3. Apply the four list filters: burned domains, dead infrastructure, bounced recipients, company-domain dedupe across active campaigns.
4. Confirm signatures are non-empty and market-specific values are set.
5. Run the change as a dry run first. Keep the script or payload in Git.

End of day:
1. Commit intentional doc and script changes. Never raw exports, never secrets.
2. Record any manual operation in the relevant doc or state file.

## Weekly

| Day | Do |
|---|---|
| Start of week | Read the performance-check output and the placement tests. Investigate any provider group under the pass bar. Run `audit-deliverability` if a threshold is crossed. |
| Mid-week | Sweep positive replies: reply to interested within the hour, contact referrals within 24 hours, remove hostile respondents. Review the reply-rate rotation output and the fleet snapshot. |
| End of week | Refresh metrics (`gtm --json sync campaigns` or `gtm metrics import`), run `gtm --json review outreach`, then `weekly-gtm-review`. If the report looks wrong, check each input's last run before touching the number. |
| Weekend or Monday | Review the cleanup queue. Large deletes need a store backup and approval first. |

## Monthly

1. Month-over-month trend on the KPI hierarchy: opportunities per 1,000 sent, then opportunities per reply, then positive reply rate, then reply rate. Opens are not a metric.
2. Hypothesis register sweep: every running experiment gets a verdict against its preregistered decision rule, or a written reason it is still running.
3. Promote learnings: anything validated twice moves from the experiment log to the copy rules, ICP, or thresholds. Anti-learnings get the same treatment.
4. Credentials review: rotation dates due, shared passwords to replace with invites, unused keys to revoke.
5. Fleet cost review: idle warmed mailboxes, burned domains still paid for, unused subscriptions.
6. State-file backup: copy `.gtm/` state files and export the store tables that hold state.

## Ask before

- Buying domains or provisioning many mailboxes
- Creating metered placement tests
- Large paid enrichment runs
- Deleting large lead sets
- Changing scheduler definitions or the store schema
- Force-pushing or rewriting history
- Changing copy across active campaigns
- Activating or ramping a campaign or a market

## Usually safe without asking

- Read-only API pulls and store selects
- Dry runs
- Reading logs
- Generating reports without posting them
- Small documentation fixes
- Editing scripts in a branch when nothing executes
