---
name: stage-campaign
description: Build quality-gated campaign copy, create an immutable action plan, and apply it to lemlist or Instantly in paused state only. Use after an experiment and audience are approved; never use to activate, send, or bypass explicit apply approval.
---

# Stage Campaign

Read the approved ICP, experiment, account evidence, suppressions, and `OPERATING-CONTRACT.md`.

1. Draft a `CampaignDraft` JSON under `campaigns/` with the configured provider, exact audience query, steps, suppressions, and `status: paused`.
2. Quality-gate every claim, personalization token, channel constraint, opt-out path, and denominator. Reject fabricated relevance.
3. Run `gtm --json campaign plan --draft <file>`. Present targets, payload summary, expiry, and hash to the operator.
4. Apply only after explicit approval using the exact returned ID: `gtm --json campaign apply --plan <id>`.
5. Verify the provider reports draft or paused. Record the plan/result reference, not raw recipients, in Git.

There is no activation or send workflow. Do not attempt one through direct API calls or provider UI automation.

Licensed CC BY 4.0 — GTM Adviser.
