# Handover package template

Copy the blocks below into `handover/` and fill them in. Delete nothing; write "none" where a section is empty. No credential values anywhere.

---

## START-HERE.md

```
# Start here

Engine: <company> outbound engine · Handover date: YYYY-MM-DD
Outgoing operator: <name> · Incoming operator: <name>

## State of the engine on the handover date
<paste `gtm --json doctor` and `gtm --json next` output>

## The five things that matter
1. <the item that breaks first if ignored, usually a scheduled job on the wrong host>
2. <the metric that is produced but not owned, e.g. interested leads with no meeting owner>
3. <the built-but-not-launched assets and who signs them off>
4. <the fleet state: warming, idle, in error, and what each costs>
5. <the credential plan status>

## Read in this order
1. HANDOFF.md
2. DECISIONS.md
3. AUTOMATIONS.md and STATE-FILES.md
4. OPERATOR-ROUTINE.md and ACCEPTANCE.md
5. WRAPUP.md
```

## HANDOFF.md

```
# Handover index

## 1. Ownership matrix
| Area | Owner | Backup |
|---|---|---|
| Mailbox and email infrastructure | | |
| Lists, signals, campaign launching | | |
| Data pipeline and scripts | | |
| Program owner and sign-off | | |

## 2. Open items
| ID | Item | Owner | Sign-off needed | Next action | Status |
|---|---|---|---|---|---|
| H1 | | | yes/no | | open |

## 3. Built but not launched
| Asset | State | Blocker | Owner |
|---|---|---|---|

## 4. Infrastructure state (aggregates only)
| Provider group | Mailboxes | Warming | Active | Error | Idle cost per month |
|---|---|---|---|---|---|

## 5. Hard rules
<paste from hard-rules-for-agents.md, adapted>

## 6. Operational gotchas
- <one line per trap, with the date observed and "verify before relying on it">

## 7. Access and credentials
See CREDENTIALS-PLAN.md. Values are in the password manager only.

## 8. Document index
| Topic | File |
|---|---|
```

## SOURCE-REGISTER.md

```
| Date | Source | Type (transcript, minutes, proposal, decision) | Status (current, superseded, historical) | Notes |
|---|---|---|---|---|
```

## DECISIONS.md

```
# Decision register
Last updated: YYYY-MM-DD. A working assumption is not a decision until a stakeholder confirms it.

## Confirmed
| Topic | Decided by | Date | Decision |
|---|---|---|---|

## Working assumptions
| Topic | Assumption | To be confirmed by |
|---|---|---|

## Conflicts to resolve explicitly
| Conflict | Evidence A | Evidence B | Clarification needed | Owner |
|---|---|---|---|---|

## Unresolved
- <question> · owner · needed by
```

## AUTOMATIONS.md

```
| Job | Command | Schedule | Host | Log path | Last success | Breaks if stopped | Owner |
|---|---|---|---|---|---|---|---|
```

## STATE-FILES.md

```
| File or table | Holds | Regenerable | Rule |
|---|---|---|---|
| .gtm/deliverability/watchlist.json | reply-rate rotation stages | no | never delete |
```

## CREDENTIALS-PLAN.md

```
| Credential name (from .env.example) | Holder today | Owner after | Channel | Rotate by | Rotation disconnects anything? |
|---|---|---|---|---|---|

Host settings: secret scanning on · push protection on · pre-commit secret guard installed
```

## ACCEPTANCE.md

Use `acceptance-checklist.md`.

## WRAPUP.md

Use `wrapup-template.md`.
