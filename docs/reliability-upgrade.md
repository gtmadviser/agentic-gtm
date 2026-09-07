# Reliability changes and upgrade notes

This change adds the LinkedIn engager playbook and repairs the workspace,
storage, apply and metrics paths used around it. It does not release a new
version or activate any provider workflow.

## Apply safety

File writes use a process lock and atomic file replacement. Campaign and Slack
CLI applies claim a pending plan before calling the provider. Supabase claims
use a conditional update on the plan ID, hash and pending status. A second
worker cannot apply the same plan concurrently. HTTP mutations are attempted
once, including after timeouts and server errors.

An interrupted apply can leave `applying`; a caught provider failure leaves
`needs_review`. These states intentionally prevent replay. Inspect the provider
using any returned shell/message ID and reconcile the outcome before preparing
another action. Do not reset the plan to pending or create a duplicate plan to
work around an uncertain result. This implementation does not automatically
resume individual remote steps or provide exactly-once delivery across a
provider and the local store. Result persistence precedes final plan status so
a crash between the two still prevents the CLI from replaying a completed write.

The lemlist adapter rejects multiple variants before creating a shell. Its
apply result is `verified: false` because a paused-state readback does not
confirm schedule hours/days, sender, all content or LinkedIn acceptance
conditions. Configure and verify those manually while paused. Use the local
outreach pack when the provider behavior cannot be represented by the adapter.

## Metrics and migration

Back up operational data, review `gtm db migrate --dry-run`, then apply packaged
`0003_reliability.sql` to your intended Supabase project before using these
contracts there. No live database migration is performed by installing the code.
The file backend does not require SQL.

New metric imports accept `campaign_id`, `kind` (`interval` or `cumulative`), and
`unit` (`email`, `contact`, `account`). Defaults preserve interval CSV imports.
Use stable campaign IDs so renaming a campaign cannot double-count it. A
cumulative series contributes its latest snapshot; interval series require
non-overlapping half-open windows. Mixed units or mixed snapshot/interval data
for one campaign fail visibly. Reviews report their scope rather than calling
all stored history a weekly change.

Missing reply, positive-reply, meeting and opportunity counts remain null.
Unknown is not zero. Rankings require complete outcome counts; sample-size
tiers remain heuristics, not statistical confidence. Instantly unique human
replies use `reply_count_unique`; `total_opportunities` only populates
opportunities. Positive replies and meetings remain unknown when not supplied.

Older Instantly rows lack a reliable stable campaign ID and use different reply
semantics. SQL migration marks these `instantly.analytics.legacy`; file reviews
detect the old shape. Reviews stop with an actionable error. Export/archive
those legacy rows locally and resync the affected campaigns before reviewing.
Do not merge old campaign-name snapshots with new campaign-ID snapshots.

New CSV writes distinguish empty strings, nulls and literal `json:` values.
Legacy blank variants are normalized to the empty string when reading metrics.
Other malformed rows stop the review instead of disappearing. New provider
records have deterministic IDs; upserts preserve IDs already in either store.

## Installation and remaining boundaries

Wheels now contain all 16 canonical skills and their helpers. `gtm init` copies
them to `.agents/skills/` and `.claude/skills/`, preserving existing local files.
The starter generator copies every packaged migration and excludes incidental
sync copies. Publishing a starter still requires a real runtime release/tag;
this branch does not create or publish one.

The broader review also identified work outside this patch: full HubSpot field
mapping and association-aware CRM pulls, adapter-wide scope enforcement and
pagination, runtime budget plans for AI Ark/Blitz, experiment-specific readiness,
and fully automated verification/enrollment. Those remain explicit follow-up
work. The new skill handles the relevant CRM, budget and readiness decisions
through reviewable local artifacts and documents manual provider fallbacks.

Validation uses synthetic data and mocked providers. It covers concurrent plan
claims, uncertain writes, metric snapshot semantics, credential isolation,
local-store compatibility, Harvest collection and installation artifacts. It
does not certify live provider behavior or LLM qualification accuracy.
