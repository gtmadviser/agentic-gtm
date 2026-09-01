---
name: audit-deliverability
description: Review sending domains, DNS, mailbox health, capacity, suppression, and sequencer state without provisioning, deleting, activating, or sending. Use before outbound campaigns or when delivery metrics change; do not use for infrastructure mutation.
---

# Audit Deliverability

Read the approved experiment safeguards and configured sequencer scope.

1. Inventory sending domains and mailboxes without exposing addresses in Git.
2. Check SPF, DKIM, DMARC, tracking-domain alignment, recent provider health, daily capacity, warm-up state, bounce/suppression behavior, and campaign status.
3. Separate direct observations from likely causes. Never diagnose from open rate alone.
4. Classify findings as blocking, material, or informational and attach an owner and verification step.
5. Save an aggregate audit under `reports/`; keep mailbox identifiers and raw provider responses in Supabase or `.gtm/`.

This skill is read-only. Do not buy domains, create or delete mailboxes, modify DNS, change campaign state, activate warm-up, or send tests.

Licensed CC BY 4.0 — GTM Adviser.
