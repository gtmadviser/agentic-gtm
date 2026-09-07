# ICP scoring and routing

Build the rubric from the approved ICP and experiment, not from the list you
just collected. Give it a version and retain the evidence date. If the company
has a rubric, use it. Otherwise propose weights and a qualifying threshold for
approval; do not silently adopt a technology company's title or headcount gates.

| Criterion | Evidence | Decision |
|---|---|---|
| Company fit | domain, sector, size, geography, business model | pass, fail, unknown |
| Persona fit | resolved current title, function, responsibility | pass, fail, unknown |
| Required business trigger | a dated source explicitly required by the ICP | pass, fail, unknown |
| Anti-ICP | competitors, own employees, excluded industries/roles | exclude or clear |
| Engagement | exact post, reaction/comment/reply, first observation | separate signal; zero automatic fit points |

For an approved weighted rubric, `fit_score = sum(earned criterion points)`.
Include `score_max`, `known_weight` and per-criterion evidence. Unknown criteria
earn no points but are not a negative fact. A score cannot override a failed
mandatory criterion or missing critical evidence. Keep `fit_status` (`fit`,
`not_fit`, `review`) separate from score and confidence. Do not infer protected
or sensitive personal traits; score business relevance only.

`qualification.csv` should include `person_id`, `profile_url`, `current_title`,
`company_domain`, `rubric_version`, `fit_score`, `score_max`, `known_weight`,
`fit_status`, `criterion_results_json`, `evidence_ids`, `unknowns`,
`excluded_reason`, `reviewed_by`, `reviewed_at`. Evidence entries carry a source
URL, observed date and the supported value. A bare score is not qualification.

CRM fields are company-specific. Read configured field mappings and actual
pipeline/lifecycle stage definitions; do not hardcode customer or deal IDs.
Match a company independently of the contact, then inspect associated open
deals and account ownership. A net-new contact at a customer is not a net-new
prospect. An empty owner property and a failed owner lookup are different states.

Apply routing in this order:

1. Opt-out, complaint, competitor, own team, hard exclusion → `exclude`.
2. Customer, active opportunity or protected lifecycle → `notify_only`.
3. Unresolved identity, stale/missing CRM or suppression check, conflicting
   territory/owners, insufficient fit evidence → `hold`.
4. Known account owner or contact owner → `owner_review`. Preserve both owner
   IDs; conflicts need resolution. Do not enroll into somebody else's sequence.
5. Recent contact, existing campaign membership or re-approach cooldown → `hold`.
6. Reviewed ICP fit, clear suppression checks, unowned account/contact and
   agreed sender/territory → `outreach_draft`.

Carry `route`, `route_reason`, CRM match method, both owners, account/contact
lifecycle, open-deal count, campaign memberships, last outreach date,
`crm_checked_at` and `suppressions_checked_at` in `routing.csv`. Unknown is never
equivalent to zero open deals. Notify-only and owner-review outputs are local
handoffs until the user authorizes CRM tasks or messages.

Review the initial probe row by row. Record fit precision, ambiguous identity
rate and excluded/held counts. Agree the expansion threshold before scaling.
Keep the same rubric across comparison cohorts; version intentional changes.
