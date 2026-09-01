---
name: source-market
description: Search accounts or contacts through the explicitly configured AI Ark or Blitz adapter, normalize and deduplicate results, and retain provenance in Supabase. Use after ICP and sourcing filters are approved; do not use for speculative scraping or direct campaign enrollment.
---

# Source Market

Read the approved ICP, exclusions, active experiment, and `gtm.yaml`. Run `gtm doctor`.

1. Translate criteria into a provider query JSON under `.gtm/`; never add a provider because it has an affiliate relationship.
2. Start with a small probe. Run `gtm --json source accounts --query <file>` or `gtm --json source contacts --query <file>`.
3. Inspect false positives before expanding. Loosen one filter at a time when results are empty; do not remove anti-ICP or suppression rules silently.
4. Keep normalized contacts, provider IDs, raw attributes, and provenance in Supabase. Store only approved aggregate notes in Git.
5. Report query, provider, observed date, result count, duplicate count, and unresolved data-quality risks.

Sourcing never authorizes outreach.

Licensed CC BY 4.0 — GTM Adviser.
