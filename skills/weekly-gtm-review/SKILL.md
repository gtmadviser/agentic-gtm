---
name: weekly-gtm-review
description: Combine pipeline, campaigns, experiments, risks, owners, and next actions into a weekly GTM operating review, with an optional approval-gated Slack report. Use for recurring revenue-team reviews; do not use as a raw dashboard dump.
---

# Weekly Gtm Review

Read current decisions, experiments, recent reports, and the operating contract.

1. Refresh only needed sources, then run `gtm --json review weekly`.
2. Structure the review around changes, evidence, decisions needed, risks, and owner-bound next actions—not vanity metrics.
3. Keep won, lost, and open pipeline separate; tie campaign conclusions to preregistered experiments.
4. Resolve conflicting metrics or label them unresolved. Preserve the generated aggregate report under `reports/`.
5. If the operator approves publication, run `gtm --json report slack plan --report <file>`, present the immutable plan, and apply only with `gtm --json report slack apply --plan <id>`.

Webhook-only Slack mode is unverified and must be labelled as such. Never post without explicit apply approval.

Licensed CC BY 4.0 — GTM Adviser.
