---
name: handover-gtm-engine
description: Package a running outbound engine for handover to a new operator or back to the company, with a source-of-truth matrix, decision register, ownership and open-items matrix, automation inventory, credentials transfer plan, operator routine, acceptance exercises, wrap-up retrospective, and a history-free repository snapshot. Use at the end of an engagement, when an operator changes, or when the engine has run for 90 days without a written handover; do not use to transfer credentials through the repository or to sign off an operator who has not completed the acceptance exercises.
---

# Handover GTM Engine

> An outbound engine is scripts, schedules, state files, credentials, provider quirks, and decisions. Most of it lives in people's heads until the person leaves. This skill turns the engine into a package a new operator can run in their first week without the previous operator, and gives the company a clean, secret-free repository they own. It sits across the whole pipeline (Research → ICP → Source → Personalize → Reach → Measure → Iterate) because every stage has something to hand over.

## When to use / when not to

Use it:
- At the end of an advisory or agency engagement, two weeks before the last day.
- When the operator changes, in either direction.
- Every 90 days of operation even without a change; a handover doc that is never written is never accurate.
- After a credential incident, to produce the history-free snapshot.

Do not use it:
- To move credentials. Credentials go through a password manager, never through Git, a chat, or a document.
- To sign off an operator who has not run the acceptance exercises in front of the outgoing operator.
- As a substitute for `weekly-gtm-review`. The wrap-up retrospective uses the reviews; it does not replace them.

## Inputs

| Source | What to read |
|---|---|
| `gtm --json doctor` | Providers configured, store backend, credentials present by name |
| `gtm --json next` | Which stages are done and what the engine is waiting on |
| `context/company.md`, `market/icp.md`, `strategy/decisions.md` | Durable context and every recorded decision |
| `experiments/*.json`, `campaigns/*.json`, `reports/*.md` | What ran, what was measured, what was concluded |
| Store tables | `action_plans`, `apply_results`, `campaign_metrics`, accounts and contacts counts |
| Scheduler | Every scheduled job: command, schedule, host, log path, last successful run |
| `.gtm/` | Stateful files that must survive (watchlists, rotation splits, cursors) |
| `.env.example` | Credential names (never values) |
| Provider dashboards | Anything that is UI-only and not in the API |
| The outgoing operator | The undocumented rules, asked one topic at a time |

## Procedure

1. **Run the doctor and the gate machine.** Paste `gtm doctor` and `gtm next` output at the top of `handover/START-HERE.md`. This is the "state of the engine on the handover date".
2. **Inventory automations.** One row per scheduled job: name, command, schedule, host it runs on, log path, last successful run, what breaks if it stops, owner after handover. A job on a personal machine is a blocking item: it dies with that machine.
3. **Inventory stateful files and tables.** List every file under `.gtm/` and every store table that holds state which cannot be regenerated (watchlists, rotation splits, sync cursors, plan records, suppression lists). Mark each "never delete".
4. **Write the source-of-truth matrix.** For each topic (domains, mailboxes, campaigns, live campaign status, outreach history, deals, suppression, rotation state, placement results), name the one source that wins and the caches that must not be trusted.
5. **Build the decision register** with four sections: confirmed (who, when), working assumptions (to be confirmed by whom), conflicts (two sources disagree, what evidence, what clarification is needed), unresolved. The latest explicit stakeholder decision beats older notes. Never silently resolve a conflict.
6. **Build the ownership and open-items matrix.** Every open item gets an ID, an owner, and the next action in one sentence. Items that require sign-off are marked and cannot be launched unilaterally. Items that need a named person's own action (an OAuth login, a password change) are marked "(self)".
7. **Write the credentials transfer plan.** Names of every credential from `.env.example`, who holds it today, who will own it, transfer channel (password manager), rotation date after handover, and whether the rotation needs a reconnect that would reset warm-up. Prefer invites and per-person accounts over shared passwords.
8. **Write the operator routine** (daily 15 minutes, weekly rhythm, monthly review) from `references/operator-routine.md`, adapted to the actual schedules found in step 2.
9. **Write the acceptance exercises** per module from `references/acceptance-checklist.md`. Each module passes only through four steps: explained, shown live, done by the new operator, and the new operator explains the result and the risks back.
10. **Write the hard rules block** from `references/hard-rules-for-agents.md` into the workspace `CLAUDE.md` and `AGENTS.md`, adapted to the systems in use. This is the part that prevents the expensive mistakes.
11. **Write the wrap-up retrospective** from `references/wrapup-template.md`: numbers with denominators, phases, learnings, anti-learnings, open items, recommendations. Numbers come from the store and the reports, never from memory.
12. **Produce the history-free snapshot.** Export the tracked files at the handover ref, run the secret gate (no `.env` value, no credential-looking literal, no credential-type file in the export), build a single-commit repository, and push only to an empty repository the company owns after a typed confirmation. Never use a platform "transfer ownership" on a repository whose history ever contained a secret; transfer moves history.
13. **Sign off.** The acceptance sheet is complete, the credentials are in the password manager with the old values rotated where possible, the snapshot repository is verified, the old repository is archived. Record the sign-off date and both names in `strategy/decisions.md`.

## Hard rules

1. No credential value in any handover artefact. Names only. The transfer channel is a password manager.
2. Every automation has an owner and a host the company controls before sign-off. A job on a personal machine is blocking.
3. Every stateful file is listed and marked "never delete". Deleting a watchlist or a rotation split silently restarts rotation from zero.
4. Every open item has exactly one owner and one next action. "Team" is not an owner.
5. The latest explicit stakeholder decision wins over older notes, proposals, and transcripts.
6. Conflicting metrics are labelled unresolved with both sources. They are never averaged or picked.
7. Acceptance is per module and requires the new operator to perform the task, not watch it.
8. The history-free snapshot goes only to an empty repository, after the secret gate passes, after a typed confirmation.
9. An NDA is not a data-processing agreement. Do not assume a signed NDA authorizes any third-party processing of lead data.
10. Ask before every irreversible action in the handover window: deletes, DNS changes, history rewrites, subscription cancellations, credential rotations that disconnect mailboxes.

## Checklist

Package complete when:
- [ ] `handover/START-HERE.md` with doctor and gate-machine output, the five things that matter, and the read order
- [ ] `handover/HANDOFF.md` with ownership matrix, open items with IDs, hard rules, operational gotchas, document index
- [ ] `handover/SOURCE-REGISTER.md`: every source document with date and status
- [ ] `handover/DECISIONS.md`: confirmed, assumptions, conflicts, unresolved
- [ ] `handover/AUTOMATIONS.md`: every job with schedule, host, log, owner
- [ ] `handover/STATE-FILES.md`: every never-delete file and table
- [ ] `handover/CREDENTIALS-PLAN.md`: names, holders, channel, rotation dates; no values
- [ ] `handover/OPERATOR-ROUTINE.md` and `handover/ACCEPTANCE.md`
- [ ] `handover/WRAPUP.md` with numbers, phases, learnings, anti-learnings, open items
- [ ] Hard rules block in `CLAUDE.md` and `AGENTS.md`
- [ ] Pre-commit secret guard installed in the repository; secret scanning and push protection on at the host
- [ ] History-free snapshot built, secret gate passed, pushed to the company's empty repository, verified
- [ ] Credentials rotated where rotation does not disconnect mailboxes; the rest scheduled with an owner
- [ ] Acceptance exercises passed per module; sign-off recorded

## Output contract

- `handover/` (Git): the files in the checklist. Aggregates and names of things, never lead rows, mailbox addresses, or credential values.
- `strategy/decisions.md`: sign-off entry with date, outgoing and incoming operator, and the snapshot repository URL.
- Snapshot repository: one commit, tracked files at the handover ref, `.env` and gitignored files never present.
- Status fields on open items: `open`, `blocked`, `done`, with the blocking reason if blocked.

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| Reports go stale two days after handover | Nightly sync ran on the outgoing operator's machine | Migrate the job to a company-owned scheduler before sign-off; it is item one |
| New operator re-derives a rule the hard way | The rule lived in a chat or a head | Add it to the hard rules or gotchas section the day it is rediscovered |
| Two documents disagree on a number | Different denominators or windows | Label unresolved, list both, assign an owner; never average |
| A credential still works months later | Rotation was "later" | Rotation dates in the credentials plan with owners; check them at the 30-day review |
| A watchlist or rotation file is gone | Cleanup deleted "cache" | Restore from backup; the state-files list marks it never delete |
| Repository transferred with history | Platform transfer used | Too late for that copy; build the snapshot, ask the company to delete the transferred copy, rotate everything that was in history |
| Operator signs off but cannot run the Friday loop | Acceptance was "explained" not "done" | Re-run the acceptance exercise with the operator driving |

## References

- [operator-routine.md](./references/operator-routine.md), daily, weekly, monthly routine
- [acceptance-checklist.md](./references/acceptance-checklist.md), per-module prove-it exercises
- [handoff-template.md](./references/handoff-template.md), fill-in template for the handover package
- [hard-rules-for-agents.md](./references/hard-rules-for-agents.md), paste-ready block for a workspace `CLAUDE.md`
- [wrapup-template.md](./references/wrapup-template.md), the end-of-engagement retrospective

Licensed CC BY 4.0 by GTM Adviser.
