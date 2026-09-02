---
name: inspect-crm
description: Inspect HubSpot properties and pipelines read-only, obtain human field-map confirmation, then pull the minimum records and analyse won, lost, and open opportunities separately. Use for CRM audits, pipeline diagnosis, or evidence extraction for the ICP; do not use before credentials are configured or to write anything back to the CRM.
---

# Inspect CRM

> The CRM is the only evidence source a startup fully owns, and it is also the easiest one to misread. This skill runs at the Research stage of the engine (Research → ICP → Source → Personalize → Reach → Measure → Iterate) and feeds `refine-icp`. It has one non-negotiable gate: a human confirms what every field and stage means before a single record is analysed. It never writes to the CRM.

## When to use / when not to

Use when:

- A HubSpot portal exists and `gtm doctor` reports the `crm` capability as ready, or you are setting it up.
- `gtm next` reports stage `crm` as not done.
- The ICP needs observed evidence, a pipeline looks unhealthy, or someone asks "what does the data actually say".
- A field map exists but the portal changed (new pipeline, renamed stage, new custom property).

Do not use when:

- No CRM credentials are configured. Run `gtm doctor`, fix `.env`, come back.
- You need to change a deal, create a task, or update a property. There is no write path in this system.
- The question is about outreach results. That is `review-outreach`.

## Inputs

| Input | Where | What you take from it |
|---|---|---|
| Operating contract | `OPERATING-CONTRACT.md` | the field-map pause and the Git versus store boundary |
| Config | `gtm.yaml` | `providers.crm`, `scopes.hubspot.objects`, `field_maps.hubspot` |
| Doctor | `gtm --json doctor` | credential and store readiness |
| Inspection | `.gtm/hubspot-inspection.json` (written by the first `gtm sync crm`) | properties per object, pipelines and stages |
| Company brief | `context/company.md` | how the team describes stages, value, and sources |
| Store | `accounts`, `contacts`, `opportunities` tables | rows after the pull; aggregates only leave the store |

## Procedure

1. **Check readiness.** Run `gtm --json doctor`. Confirm `capabilities.crm.ready` is `true` and note which store is active (Supabase or `.gtm/store/`). If not ready, list the missing variables to the operator and stop.
2. **Confirm the token is read-only.** The HubSpot private app must carry only read scopes for companies, contacts, deals, and their schemas. If the operator cannot confirm, ask them to open the private app settings and read the scope list aloud. Do not proceed on a token with write scopes; ask for a new app.
3. **Run the inspection.** Run `gtm --json sync crm`. On first use it writes `.gtm/hubspot-inspection.json`, returns `status: field_map_confirmation_required`, and exits with code 2. That exit is the gate, not an error.
4. **Walk the inspection with the operator.** Follow `references/field-map.md`. Cover, in this order: pipelines in scope; which stages mean won, lost, and open; the primary deal-value field and its currency; create and close dates; deal source; owner; loss reason; company size, country, and industry fields; custom properties whose meaning is not obvious. For every property, record the fill rate the operator expects. Ask, do not guess.
5. **Write the confirmed map.** Put only confirmed semantics under `field_maps.hubspot` in `gtm.yaml`, with `confirmed_by`, `confirmed_at`, and `analysis_start_date`. Leave unknown fields out and list them in a `Limitations` note. Never invent a meaning to make the map complete.
6. **Pull the minimum.** Rerun `gtm --json sync crm`. It pulls companies, contacts, and deals within `scopes.hubspot.objects`, normalises them into `accounts`, `contacts`, and `opportunities`, and upserts them into the store with provider IDs. Read the returned counts and compare them with what the operator expects from the portal. A gap over 5 percent needs an explanation before analysis.
7. **Review the pipeline.** Run `gtm --json review pipeline`. It writes `reports/pipeline-<date>.md` with won, lost, and open reported separately, counts and amounts per cohort, and win rate by every dimension that has a confirmed field. Read `references/won-lost-open-analysis.md` before interpreting.
8. **Lead with coverage.** In your summary, state the data period, the number of deals per cohort, the fill rate of each dimension used, and the unique-account counts. Then the patterns. Then the caveats.
9. **Record limitations.** Add a `Limitations` section to the report: missing fields, ambiguous stages, pipelines excluded, enrichment not applied, time windows too short. Limitations are findings, not apologies.
10. **Hand off.** Add supported patterns as evidence rows in the `Observed evidence` section of `market/icp.md` with IDs, n, and confidence. Do not change the ICP definition itself; that is `refine-icp`. Run `gtm --json next`.

## Hard rules

1. Read-only. No write scope on the token, no write endpoint in the adapter, no exceptions for "just one property".
2. The field-map pause is never bypassed. If `field_maps.hubspot` is empty, the pull does not run.
3. No guessed semantics. A property without a confirmed meaning is excluded from analysis and listed under limitations.
4. Won, lost, and open are never collapsed into one number.
5. A cohort or cut with fewer than 10 closed deals is `insufficient`; 10 to 19 is `directional`; 20 or more is `supported`. Say the label every time you cite a number.
6. Report deal-level and unique-account-level results side by side for any pattern used as ICP evidence.
7. Raw rows stay in the store. Git receives aggregates, coverage figures, and decisions only. `.gtm/hubspot-inspection.json` stays in `.gtm/`.
8. The field map holds labels and property names, never data values.
9. Enrichment, if used, matches companies by exact normalised domain and contacts by exact profile URL. Fuzzy name matches are not accepted.
10. Pipelines not explicitly confirmed as in scope are excluded and named in limitations.
11. Analysis start date is confirmed by the operator and written in the map. Deals before it are excluded from cohorts.
12. Contact-level analysis (titles, personas) is reported in aggregate bands only.

## Checklist

- [ ] `gtm --json doctor` shows `crm.ready: true` and the active store.
- [ ] Token scopes confirmed read-only by the operator.
- [ ] First `gtm sync crm` exited with code 2 and wrote the inspection file.
- [ ] Pipelines in scope confirmed; won and lost stage IDs confirmed.
- [ ] Value field, currency, create date, close date confirmed.
- [ ] Source, owner, loss reason confirmed or listed as unavailable.
- [ ] Company size, country, industry fields confirmed with expected fill rates.
- [ ] `field_maps.hubspot` contains `confirmed_by`, `confirmed_at`, `analysis_start_date`.
- [ ] Second `gtm sync crm` counts compared with the portal.
- [ ] `gtm review pipeline` report read; coverage stated before patterns.
- [ ] Every cited number carries `insufficient`, `directional`, or `supported`.
- [ ] Limitations section written.
- [ ] Evidence rows added to `market/icp.md` with IDs; ICP definition untouched.
- [ ] No raw rows, contact data, or the inspection file in Git.

## Output contract

| Artifact | Location | Rules |
|---|---|---|
| Inspection | `.gtm/hubspot-inspection.json` | Local only, ignored by Git. Regenerated on demand by deleting it and rerunning the sync. |
| Field map | `gtm.yaml` under `field_maps.hubspot` | Flat keys, string values. Contains property names and labels, never values. Committed. |
| Normalised records | store tables `accounts`, `contacts`, `opportunities` | Upserted on `provider, provider_id`. Never exported into Git. |
| Pipeline report | `reports/pipeline-<YYYY-MM-DD>.md` | Generated by `gtm review pipeline`. Sections: coverage, cohorts, cuts, loss reasons, open pipeline, limitations, interpretation, owners. Aggregates only. |
| Evidence rows | `market/icp.md`, section `Observed evidence` | IDs `E-nnn`, type `CRM evidence`, cohort and n, both views, coverage, confidence, source `reports/pipeline-<date>.md#section`. |
| Limitations | inside the pipeline report | Named fields, pipelines, and windows that were excluded, with the reason. |

## Failure modes

| Symptom | Likely cause | Action |
|---|---|---|
| `sync crm` exits 2 on every run | `field_maps.hubspot` still empty or not saved | Confirm the map with the operator and write it; rerun |
| HTTP 403 on inspection | Token lacks schema read scopes, or the app is scoped to another portal | Ask the operator to fix the private app; do not retry blindly |
| HTTP 429 during pull | Rate limit on search endpoints | The client retries with backoff; if it persists, reduce `scopes.hubspot.objects` or run later |
| Deal counts differ from the portal | Excluded pipelines, archived deals, or the analysis start date | List which filter explains the gap; do not "fix" by widening scope silently |
| Win rate looks implausibly high | Lost deals never recorded, or lost stage not confirmed | Report the lost-stage coverage; label everything `directional` until confirmed |
| Value field is empty on most deals | Team uses a custom ARR or MRR property | Confirm the custom property as the value field; restate currency handling |
| Industry cut contradicts itself | Two overlapping industry fields | Pick one as primary in the map; report the other as secondary coverage |
| A pattern disappears in the unique-account view | One account with many deals | Report both views; do not promote the pattern |
| Operator asks to update a deal from here | Wrong tool | Decline; point to the CRM UI or a separate approved workflow |

## References

- [Field map](./references/field-map.md): how to walk the inspection, the confirmation questions, and a fictional confirmed map.
- [Won / lost / open analysis](./references/won-lost-open-analysis.md): the analysis outline and the table shapes the report uses.

Licensed CC BY 4.0 by GTM Adviser.
