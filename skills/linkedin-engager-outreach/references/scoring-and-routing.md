# Evidence, qualification and routing

Build the rubric from the approved company ICP and experiment. Preserve its
revision. Do not copy another client's title dictionary, headcount cutoff,
competitor list or signal-specific company segments.

Keep four things separate: company fit, persona fit, observed engagement and
outreach eligibility. Unknown mandatory evidence holds a row regardless of
engagement or its other scores. A fit score never authorizes a message.

## Evidence pipeline

1. Screen captured headlines cheaply. Exclude clear own-team/non-target cases,
   retain ambiguous founders or titles for review, and audit dropped rows.
2. Resolve shortlisted profiles when identity/current-role evidence is missing.
   Save opaque/public aliases and inspect all current roles; do not simply choose
   the first role returned. Hold conflicting employment.
3. Match companies to fresh CRM facts using domain or company LinkedIn identity.
   Enrich missing company facts selectively. If an experiment requires technology
   or business signals, record those sources in separate criteria; engagement
   is not a substitute for that evidence.
4. Recheck persona fit after resolution. A technical-looking headline can resolve
   to a different current job; do not preserve a stale prequalification pass.

## Executable rubric

`harvest_pipeline.py qualify` evaluates supplied criterion decisions and applies
relationship guards offline. It does not independently research or judge the
truth of the evidence; that remains the agent/reviewer's work.

```json
{
  "version": "approved-icp-v1",
  "criteria": [
    {"id": "company_size", "dimension": "company", "mandatory": true, "weight": 1},
    {"id": "current_role", "dimension": "persona", "mandatory": true, "weight": 1}
  ],
  "company_threshold": 0.75,
  "persona_threshold": 0.75,
  "check_max_age_hours": 24
}
```

Weights and thresholds above are illustrative; approve them for the client.
Each input person has `person_id`, resolved `profile_url`, `source_posts`,
`rubric_version`, `reviewed`, `sender`, and a `criteria` object keyed by criterion
ID. Each criterion has `status` (`pass`, `fail`, `unknown`) and `evidence` entries
with `source_url`, `observed_at` and the supported `value`. An unsupported pass
becomes unknown. The result preserves weighted score, maximum, known weight,
status and evidence separately for company and persona. Changed rubric versions
require rescoring, and the output has an input/rubric hash for cache identity.

The `checks` object contains explicit booleans for `opt_out`, `competitor`,
`internal`, `hard_exclusion`, `recent_outreach`, `campaign_member`, `owner_conflict`
and `ownership_resolved`; `lifecycle` (`prospect`, `customer`, `protected`);
`open_deals` (integer, never null when known); `account_owner` and `contact_owner`
(explicit null when confirmed unowned); `crm_checked_at`, `suppressions_checked_at`
and supporting `evidence_ids`. Unknown fields stay unknown, not false/zero.

```bash
python <skill-path>/scripts/harvest_pipeline.py qualify \
  --people .gtm/linkedin-engagement/qualification-input.json \
  --rubric .gtm/linkedin-engagement/approved-rubric.json \
  --out .gtm/linkedin-engagement/qualification.json
```

## Relationship decisions

Read the client's CRM property mapping and stage meanings. Match the account
independently from the person and inspect associated deals and activities.
An empty owner property and a failed owner lookup are different states.

- Opt-out, complaint, competitor, own team or hard exclusion → `exclude`.
- Customer, active opportunity or protected lifecycle → `notify_only`.
- Failed mandatory company/persona criterion → `exclude`.
- Missing identity/post, mandatory unknown, changed rubric, stale/incomplete CRM
  or DNC evidence, conflicting owners/territory → `hold`.
- Owned account/contact → `owner_review`; prepare a post-linked owner handoff.
- Existing campaign, recent outreach or re-approach cooldown → `hold`.
- Reviewed unowned fit with sender and complete checks → `outreach_draft`.

Owner and customer handoffs are local artifacts until the session authorizes
actual CRM tasks/messages. `enrollment_ready` remains false even for a draft:
paused staging, sender/copy checks and provider verification are separate steps.

Review the first small sample row by row. Measure fit precision, identity
ambiguity and held/excluded counts. Use the same rubric for comparison cohorts;
version intentional changes and refresh CRM/DNC immediately before staging.
