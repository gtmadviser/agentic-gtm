# Query JSON examples

The `gtm source` command passes the JSON file through to the configured provider unchanged, adding only pagination (`page` and `size` for AI Ark, `max_results` and `cursor` for Blitz). Field names therefore follow each provider's people-search documentation. Confirm names against the provider's current docs, then run a 5-row probe to check the response shape before the 25-row probe.

All examples are fictional. Replace values with your approved ICP.

## Structure to keep in every file

```json
{
  "_meta": {
    "slug": "de-workflow-tools-founders",
    "version": 1,
    "icp_ref": "market/icp.md#approved-working-definition",
    "experiment_ref": "experiments/2026-09-founder-signal.json",
    "changed": "initial",
    "author": "operator"
  }
}
```

Adapters ignore unknown keys in most providers. If a provider rejects `_meta`, keep the metadata in a sibling `.meta.json` file with the same slug.

## AI Ark, accounts via people search

```json
{
  "_meta": {"slug": "de-workflow-tools-founders", "version": 1},
  "countries": ["DE"],
  "industries": ["Software Development"],
  "companySizes": ["11-50", "51-200"],
  "titles": ["Founder", "CEO", "Managing Director"],
  "excludeTitles": ["Assistant", "Intern", "Student"],
  "keywords": ["workflow", "coordination"]
}
```

## Blitz, contacts

```json
{
  "_meta": {"slug": "de-workflow-tools-founders-people", "version": 1},
  "country_code": "DE",
  "industries": ["Software Development"],
  "employee_range": ["11-50", "51-200"],
  "job_title_include": ["Founder", "CEO", "Managing Director"],
  "job_title_exclude": ["Assistant", "Intern"],
  "job_level": ["C-Team", "Director"],
  "keywords": []
}
```

## Taxonomy rules

- Industry names must match the provider's taxonomy exactly, including case. When unsure, leave industries empty and use keywords plus country plus titles.
- Keywords are language specific. A German keyword returns nothing in France.
- Title lists should carry the local-language titles for the market.
- Employee ranges are strings in most providers, not numbers.

## Versioning

`de-workflow-tools-founders-v1.json` → `-v2.json` when one filter changes. Write the change in `_meta.changed`. Keep every version. The probe precision per version is the audit trail for the ICP.

## When it returns nothing

Loosen one filter at a time, in this order: confirm the industry name is exact, widen the employee range, drop keywords, broaden the title include list. Never drop an exclude.
