# Incident response

Triage steps for the incidents that recur. Every incident ends with a written note in the deliverability report: what was observed, what was changed, who approved it, how it was verified. The audit skill diagnoses; the change is a separate approved action.

## Bounce spike

Trigger: campaign bounce above 2%, or a single sender above 5%, or T+1 bounce above 3% after a launch.

1. Split bounces by campaign, by sender, by provider group, by recipient domain. The split tells you which of the four causes it is.
2. One campaign, many senders: list problem. Pause the campaign. Re-verify the list. Remove hard bounces and every row that failed verification. Resume with the ramp plan.
3. One sender, many campaigns: mailbox problem. Remove the sender from campaigns. Check connection status, auth records, and blacklist status of its domain. Swap in a backup mailbox.
4. One provider group: provider or ESP event. Pull a placement test for that group. Check the provider's status page. Reduce that group's daily limits until the test passes.
5. One recipient domain: their gateway is rejecting. Suppress that domain for 30 days; do not fight it.
6. Verify: bounce under 2% on the next 200 sends before restoring full cap.

## Blacklist listing

Trigger: a sending domain or its IP appears on a public blocklist, or a placement test shows one ESP rejecting the whole group.

1. Confirm the listing at the list operator, not from a third-party aggregator.
2. Quarantine every mailbox on the listed domain (remove from campaigns, keep warm-up running).
3. Find the cause: unverified list, hostile content pattern, compromised mailbox, spam-trap hit. Fix it before requesting delisting; a second listing after delisting is much harder to clear.
4. Request delisting where the operator offers it. Record the date.
5. Keep the domain quarantined for 7 days after delisting, then run a placement test before it returns to a campaign.

## Spam-folder drop

Trigger: a provider group falls below 80% inbox on the primary consumer ESP, or slides more than 10 points week over week.

1. Check auth pass rates in the test. Any SPF, DKIM, or DMARC failure is the fix; do nothing else until it is repaired and verified at the authoritative nameserver.
2. Check the tracking domain. A shared default tracking host is a common cause; every sending domain needs its own CNAME.
3. Check volume. A mailbox that jumped from 10 to 40 sends a day or skipped warm-up will land in spam. Return it to ramp.
4. Check content. New copy with links, images, attachments, or spam-scored phrases in step 1 can drop placement for the whole group. Compare with the last passing test's copy.
5. Reduce daily limits on the group by half until two consecutive weekly tests pass.

## Reply cliff

Trigger: human replies on a campaign or group fall by more than half week over week with sends unchanged.

1. Separate the group from the copy. Same copy on another group replying normally means infrastructure; same group with other copy replying normally means copy or list.
2. Run the reply-rate rotation; check how many mailboxes hit stage 2.
3. Run the burn test on the group's domains.
4. Compare with placement. High seed inbox with no replies is list or copy; low seed inbox is reputation.
5. Do not touch copy and infrastructure in the same week. Change one, measure, then the other.

## Provider outage or mass disconnect

Trigger: many mailboxes flip to an error status at once.

1. Read the provider's status page and the sequencer's status page before touching anything.
2. Do not reconnect in a loop. Every reconnect attempt on a provider-locked mailbox can reset its warm-up. Open a ticket with the provider and wait for their confirmation.
3. Rebalance: move the affected campaigns' daily volume onto healthy groups within their caps, or reduce the campaign cap. Never exceed 30 sends per mailbox to compensate.
4. When the provider confirms recovery, reconnect in small batches, re-read status after a few hours, then re-enable in campaigns.

## Scheduler silently dead

Trigger: no health-check, rotation, or placement output for two or more days.

1. Check the last log timestamp of each scheduled job.
2. Common causes: machine asleep, missed runs not caught up, log path inside a protected user folder blocked by the OS, environment not loaded, network not up at trigger time.
3. Run the job by hand once, read the output, then fix the scheduler. Prefer a scheduler that catches up missed runs and a wrapper that waits for network.
4. Reconcile: anything the health check would have swapped in the dead window is now overdue. Run it.

## Report looks wrong

Trigger: the weekly numbers contradict the sequencer dashboard or last week's report.

1. List the inputs in order: sequencer analytics, CRM attribution, LinkedIn sync, call log, dashboard ETL. Check each one's last successful run.
2. Check the denominator. A changed window, a merged campaign, or a re-labelled provider group moves every rate.
3. Do not "fix" the number. Label it unresolved in the report with the two conflicting sources and an owner.

## Credential exposure

Trigger: a key, password, or credential file appears in a commit, a log, or a chat.

1. Rotate the credential first, before anything else. Confirm the old value fails.
2. Remove the file from the working tree and add its pattern to `.gitignore`. Note that it remains in history until a history-free snapshot replaces the repo.
3. Check whether any mailbox app passwords were included. Regenerate them at the provider; where the mailbox stays connected via OAuth, no warm-up reset is needed.
4. Turn on secret scanning and push protection on the repository. Install the pre-commit secret guard that `gtm init` ships.
5. Record the incident: what, when, scope, remediation, verification, and what is still pending, in the handover file.
