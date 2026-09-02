---
name: gtm-kickoff
description: Guided entry point for the Agentic GTM workspace. Runs doctor and next, explains the stage model, routes to the right skill, and walks a new company through the first session, including the path with no CRM and no database. Use to start any session or when unsure which skill applies; do not use to skip an approval gate or to run a stage out of order.
---

# GTM Kickoff

> Every session starts here. The engine runs Research → ICP → Source → Personalize → Reach → Measure → Iterate, and this skill tells you where the workspace currently is on that path and what the next reviewable artifact is. It does not do the work of other skills. It reads state, routes, and hands off at every approval gate.

## When to use / when not to

Use when:
- A session begins in an Agentic GTM workspace.
- The operator asks "what now", "where are we", or names a goal without a skill.
- A new company is being set up for the first time.

Do not use when:
- A specific skill was named and its inputs exist. Go straight there.
- Someone wants to jump to `stage-campaign apply` without an approved experiment and audience. Routing refuses; the gate is the point.

## Inputs

| Input | Where | What you take from it |
|---|---|---|
| Readiness | `gtm --json doctor` | store backend, provider readiness, missing credentials |
| Stage state | `gtm --json next` | `stages[]` with `done` and `evidence`, plus `next.stage`, `next.skill`, `next.why` |
| Operating contract | `OPERATING-CONTRACT.md` | the rules every skill obeys |
| Workspace files | `context/`, `market/`, `strategy/`, `experiments/`, `campaigns/`, `reports/` | what exists, what is stale |
| Config | `gtm.yaml` | providers, policies, field maps |

## Procedure

1. **Run readiness.** `gtm --json doctor`. Read the store backend (`supabase` or `files`), which providers are ready, and what is missing. Say it in two lines. Do not fix credentials; point to `.env.example`.
2. **Run the gate machine.** `gtm --json next`. Read `stages[]` in order and `next`. The first stage with `done: false` is the current stage. Everything after it is locked.
3. **Explain the position.** One paragraph: which stages are done with their evidence, which stage is current, what artifact ends it, which skill produces that artifact.
4. **Route.** Use `references/routing-table.md`. Name the skill, its inputs, what done looks like, and the typical trap at this stage. If the operator's goal belongs to a supporting skill (`map-market`, `audit-deliverability`, `advance-deals`, `handover-gtm-engine`), route there without changing the chain.
5. **First session for a new company.** If `context` is not done, follow `references/first-session.md`: onboard, best and worst customers, ICP draft, decide whether a CRM exists, design the first experiment, audit deliverability before any list is built.
6. **Minimal stack path.** If doctor shows no CRM, no Supabase, or no sequencer, follow `references/minimal-stack.md`. The files store, `gtm metrics import`, and a manual channel routine are supported paths, not workarounds.
7. **Hand off at every gate.** Before any skill that writes externally or spends credits, state the gate and stop: field-map confirmation, credit plan approval, experiment approval, campaign plan review, apply approval, report publication approval. The operator says go.
8. **Close the session.** Update `strategy/decisions.md` with decisions made, run `gtm --json next` again, and state the next artifact.

## Hard rules

1. `gtm --json next` decides the current stage. The operator can override with a written decision in `strategy/decisions.md`; the kickoff never overrides silently.
2. Stages are entered in order. Supporting skills run any time; chain skills do not skip.
3. The system never activates a campaign, never sends, never deletes. Say so when asked.
4. Every external write goes through plan then apply with an explicit plan id. Kickoff never runs an apply.
5. Every credit-consuming operation waits for an approved credit plan.
6. `audit-deliverability` runs before the first list is built and again before every launch.
7. A session without a decision written to `strategy/decisions.md` is not closed.
8. No client or customer names, contacts, or raw exports are written to Git by any step routed from here.

## Checklist

- [ ] `gtm --json doctor` run; store backend and provider readiness stated
- [ ] `gtm --json next` run; current stage named with evidence
- [ ] Skill routed with inputs, done-criteria, and trap
- [ ] First-session flow used when context is not done
- [ ] Minimal-stack path used when doctor shows gaps
- [ ] Every approval gate named before the routed skill runs
- [ ] Decisions written to `strategy/decisions.md`
- [ ] `gtm --json next` run again at close; next artifact stated

## Output contract

| Artifact | Location | Tracked in Git | Content |
|---|---|---|---|
| Session opening summary | inline | no | readiness, position, route |
| Decision log entries | `strategy/decisions.md` | yes | decision, owner, date, superseded version |
| Session note (optional) | `reports/session-<date>.md` | yes | what was done, what is next, open questions |

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| `next` says `context` although `context/company.md` was filled | template headings only, or the file was not saved | open the file, check for content beyond headings, save |
| `next` says `crm` but there is no CRM | `providers.crm` set in `gtm.yaml` | remove the provider or mark the stage skipped with a decision |
| Operator wants to source before ICP is approved | the ICP is a declared belief | route to `refine-icp`; a probe is allowed only against a written working definition |
| Doctor shows `files` store but the team expected Supabase | credentials missing | point to `.env.example`; the files store is valid until then |
| Session ends with work done but nothing recorded | no decision entry | write the decision, then close |

## References

- `references/routing-table.md` - stage to skill to done-criteria to trap
- `references/first-session.md` - the first session for a new company
- `references/minimal-stack.md` - the smallest setup for a first experiment

Licensed CC BY 4.0 by GTM Adviser.
