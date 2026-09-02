# Building and confirming the field map

The field map is the human-confirmed translation between HubSpot property names and the semantics the analysis needs. It is the only thing standing between "the CRM says" and "someone assumed". This document is the interview script and the file format.

## What the inspection contains

`gtm sync crm` writes `.gtm/hubspot-inspection.json` on first run. It holds:

- `properties.companies`, `properties.contacts`, `properties.deals`: every property definition (name, label, type, options).
- `pipelines`: every deal pipeline with its stages, stage IDs, labels, and display order.
- `requires_field_map_confirmation: true`.

Open it next to the operator. Do not paraphrase it into Git.

## Interview, in order

Ask each question, write the answer, move on. "Unknown" is a valid answer and goes into limitations.

**Pipelines**

1. Which pipelines are in scope for this analysis? (Self-serve and sales-assisted usually need separate treatment.)
2. For each in-scope pipeline: which stage IDs mean won? Which mean lost? Everything else is open.
3. Are there stages that used to mean something else? Since when?

**Deal value and dates**

4. Which property is the primary deal value? Amount, or a custom ARR, MRR, or contract-value field?
5. Is value stored in one currency? If not, which property holds the currency code, and what is the reporting currency?
6. Which properties are the create date and the close date? Is close date set on lost deals too?
7. From which date onward is the data trustworthy? This becomes `analysis_start_date`.

**Attribution and outcome**

8. Which property records the deal source (channel)? How consistently was it filled?
9. Which property holds the owner? Are there historical owners no longer in the team?
10. Which property holds the loss reason? Is it free text or a picklist?

**Segmentation**

11. Which company properties hold employee count, country, and industry? Which is the cleaner industry field if there are two?
12. Which custom properties matter for segmentation (for example plan, segment, product line, previous tool)? What do their values mean?
13. Which contact property holds the job title? Is there a persona or seniority field?

**Coverage expectations**

14. For every property above: roughly what share of records has it filled? The report will measure the actual figure; the expectation catches surprises early.

## File format

`field_maps.hubspot` in `gtm.yaml` is a flat mapping of string keys to string values. Property names on the right, semantics on the left. Lists are comma-separated strings.

```yaml
field_maps:
  hubspot:
    confirmed_by: "Head of Revenue"
    confirmed_at: "2026-09-02"
    analysis_start_date: "2024-01-01"
    pipelines_in_scope: "default"
    won_stages: "closedwon"
    lost_stages: "closedlost"
    deal_value: "amount"
    deal_currency: "deal_currency_code"
    reporting_currency: "EUR"
    deal_create_date: "createdate"
    deal_close_date: "closedate"
    deal_source: "hs_analytics_source"
    deal_owner: "hubspot_owner_id"
    deal_loss_reason: "closed_lost_reason"
    company_employees: "numberofemployees"
    company_country: "country"
    company_industry: "industry"
    company_previous_tool: "current_solution"
    contact_title: "jobtitle"
```

Fictional portal, fictional custom properties. Keys the operator could not confirm are omitted, not guessed.

## Rules

- The map contains names and labels. It never contains a value from a record.
- `confirmed_by` is a role or a name the team accepts in Git. `confirmed_at` is the interview date.
- Change the map only through a new interview. Note the change in `strategy/decisions.md` with the date.
- If the portal has a stage with no clear meaning, it stays open and is listed under limitations.
- Enrichment sources join on exact normalised domain (companies) or exact profile URL (contacts). Set the precedence (enrichment first or CRM first) explicitly if both hold the same semantic.

## Read scopes

The private app needs read access to companies, contacts, deals, and their schemas. Owner read access is optional and only needed for owner-level cuts. No write scope, ever. If the operator cannot list the scopes, treat the token as unverified and stop.

## Checklist before the pull

- [ ] Every in-scope pipeline has confirmed won and lost stage IDs.
- [ ] Primary value field and currency handling confirmed.
- [ ] `analysis_start_date` confirmed.
- [ ] Create and close date properties confirmed.
- [ ] At least one segmentation field confirmed with an expected fill rate.
- [ ] Unconfirmed fields listed for the limitations section.
- [ ] Map saved in `gtm.yaml`; second `gtm sync crm` run.
