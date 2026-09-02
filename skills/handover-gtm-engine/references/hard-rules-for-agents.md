# Hard rules for agents operating a GTM engine

Paste this block into the workspace `CLAUDE.md` and `AGENTS.md`. Replace the placeholders. These are trust and operational boundaries, not technical ones. Breaking one disrupts live outreach or a working relationship, and both are slower to repair than any script.

```
## Hard rules

1. Read-only on assets you do not own. Other people's campaigns, mailboxes, CRM records, and documents are read to learn from, never edited to improve. Safe: GET. Forbidden against assets you do not own: PUT, PATCH, DELETE, or any state-changing endpoint.
2. Mutating scripts carry an explicit allowlist of the IDs they may touch. Default deny. An empty allowlist does nothing.
3. No unilateral launch. Activating a campaign, unpausing, or ramping volume needs the named owner's sign-off, recorded in strategy/decisions.md.
4. No test, fake, or probe records in production systems. Verify read-only or in a sandbox.
5. Never delete without asking: files, leads, mailboxes, domains, DNS records, placement tests, scheduled jobs. Large deletes go through a queue with a backup first.
6. Dry run first for every write. Show the plan (targets, counts, cost) and wait for approval.
7. Credentials live in .env only. Never in code, CLI arguments, logs, output, chat, or Git. Never print them. Never accept them as arguments.
8. Paid or credit-consuming operations show the plan, the remaining credits, the cap, and the purpose before running.
9. Full-object updates only. Sequences, sender lists, and schedules are read, modified, and written back whole. A partial update deletes what it does not mention.
10. Every campaign build applies the four filters: burned domains, dead infrastructure, bounced recipients, and company-domain dedupe across all active campaigns.
11. Campaigns are created and updated in paused state only. There is no send or activate path in the runtime.
12. State files are never deleted: <list them>.
13. The store wins over local files. The sequencer's live API wins over stored campaign status. When they disagree, refresh the cache, never the source.
14. The latest explicit stakeholder decision wins over older notes. Record it in strategy/decisions.md the day it is made.
15. Conflicting metrics are labelled unresolved with both sources. Never averaged, never picked.
16. Add means append. Never overwrite copy, notes, or documents a human wrote.
17. Do not block on long processes. Start them, record where the output lands, move on.
18. Suppressed sectors and regulated professions are never contacted: <list them>.
19. Ask before: buying domains, provisioning mailboxes, metered tests, bulk enrichment, DNS changes, schema changes, scheduler changes, history rewrites, copy changes across active campaigns, activation or ramp.
20. When in doubt, stop and ask. A delay costs an hour. A wrong write costs a domain, a relationship, or a week.
```

## Why each rule exists

| Rule | The mistake it prevents |
|---|---|
| 1, 2 | A script "cleaning up" someone else's live campaign |
| 3 | A campaign going live with placeholder copy or an unapproved list |
| 4 | Fake leads polluting attribution and reaching a real sales rep |
| 5 | Irreversible deletion of a domain that turned out to be fine |
| 6, 8 | A bulk run that burned a month of credits in an afternoon |
| 7 | A credential in git history that forces a history-free re-publish |
| 9 | A sequence losing its steps because one step was patched |
| 10 | A burned domain re-entering a build; two campaigns hitting the same company |
| 11 | The runtime sending anything on its own |
| 12, 13 | Rotation restarting from zero; a stale ID list overwriting live state |
| 14, 15 | A superseded decision or an averaged metric driving the next campaign |
| 16 | A human's draft replaced by a machine's |
| 18 | A legal complaint from a sector where cold email is not permitted |
