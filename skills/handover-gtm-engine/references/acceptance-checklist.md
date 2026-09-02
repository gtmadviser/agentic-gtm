# Acceptance checklist

An operator is signed off per module, not in one go. Every module passes through four steps in this order:

1. **Explained**: the outgoing operator explains it.
2. **Shown**: the outgoing operator performs it live.
3. **Done**: the incoming operator performs it, unassisted.
4. **Accepted**: the incoming operator explains the result and the risks back, and names the next safe check.

A module with any step open is not accepted. Keep the sheet in `handover/ACCEPTANCE.md` with a date per step.

## Golden rules (module 0, before anything else)

The incoming operator can state each rule and give one example of the mistake it prevents.

- [ ] Never commit secrets: `.env`, credential files, key material, encrypted archives stay out of Git.
- [ ] The store wins over local files for domains, mailboxes, and campaign metadata. Local files are caches or seeds.
- [ ] The sequencer's live API wins over any stored campaign status or hardcoded ID.
- [ ] Never partially update a sequence or a sender list; read, modify, write the full object.
- [ ] Every campaign build applies the four filters: burned domains, dead infrastructure, bounced recipients, company-domain dedupe.
- [ ] Never delete state files (watchlists, rotation splits, cursors).
- [ ] Large deletes go through a queue with a backup and an approval.
- [ ] Paid APIs cost credits; check remaining credits and show the plan before a bulk run.
- [ ] Never modify assets you do not own (other people's campaigns, mailboxes, CRM records) even to improve them.
- [ ] Dry run first. Ask before anything irreversible.

## Module 1: Repository and Git

Exercise: make a one-line documentation change, read the diff, commit it, push it, find it on the host.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted
- Can read `git status`, tell tracked from untracked, explain why a dirty tree is not rebased blindly, stage only their own files, and name the files that are never committed.

## Module 2: Source of truth

Exercise: for five topics (domains, mailboxes, campaign status, outreach history, deals) name where to look first and what not to trust.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted
- Can explain the difference between source of truth, state file, cache, and export.

## Module 3: The store

Exercise: find one campaign, derive its sequencer ID, trace one contact through outreach and activities, count mailboxes by provider group.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted
- Knows which tables are never edited by hand.

## Module 4: The sequencer

Exercise: open an active campaign, explain its sender pool and sequence, check lead and reply counts, confirm the signature variable is used, list the API gotchas that apply.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 5: Build or refill a campaign

Exercise: take an existing campaign and walk the standard flow up to the dry run: select sendable contacts, apply the four filters, select senders by persona, build the draft, run `gtm campaign plan`, present the plan. Do not apply.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted
- Can say which steps are read-only, which are dry runs, and which write to a provider.

## Module 6: Sourcing and enrichment

Exercise: explain the waterfall order (website, decision maker, LinkedIn, email waterfall, verification, store, export) and the selection rule at export; check remaining credits before naming a bulk run.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 7: Mailboxes and domains

Exercise: find one mailbox in the registry, explain its persona, market, provider group, and status; find its domain and say whether it is campaign-eligible; name the provider-specific traps.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 8: Deliverability, placement, rotation

Exercise: pull the latest placement results and judge each provider group; open the reply-rate watchlist and explain why one mailbox was rotated; check one campaign for sender problems.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 9: Reporting and attribution

Exercise: open the last weekly report, pick one number, name every data source it comes from and the last run of each; reconcile one campaign's opportunities against the CRM.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 10: Replies, suppression, cleanup

Exercise: find one reply and say what happens next; check whether a domain is suppressed; explain the cleanup queue without executing it.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 11: Scheduled automations

Exercise: list every job, its host, its log path, and its last successful run; run one job by hand and read its output; explain what breaks if each job stops.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 12: Incident response

Exercise: for a bounce spike, a reply cliff, a wrong-looking report, and a campaign that does not send, name the first three checks in order.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 13: Market launch

Exercise: name the stages and the hard gates; say which gate stops a launch today.
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Module 14: When to ask

Exercise: sort twelve actions into "ask first" and "safe without asking".
- [ ] Explained · [ ] Shown · [ ] Done · [ ] Accepted

## Sign-off

| Field | Value |
|---|---|
| Incoming operator | |
| Outgoing operator | |
| Date | |
| Modules accepted | 0 to 14 |
| Open modules and plan | |
