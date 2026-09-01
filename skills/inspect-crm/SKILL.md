---
name: inspect-crm
description: Inspect HubSpot fields and pipelines, obtain human field-map confirmation, then analyze won, lost, and open opportunities separately. Use for CRM audits, pipeline diagnosis, or evidence extraction; do not use before credentials and a startup-owned Supabase are configured.
---

# Inspect Crm

Read `OPERATING-CONTRACT.md` and `gtm.yaml`. Run `gtm doctor` first.

1. Run `gtm --json sync crm`. On first use it writes `.gtm/hubspot-inspection.json` and exits before pulling.
2. Review properties and pipelines with the operator. Add only the confirmed semantic mapping under `field_maps.hubspot` in `gtm.yaml`.
3. Rerun the sync. Do not invent meanings for custom properties or collapse won, lost, and open stages.
4. Run `gtm --json review pipeline` and interpret only approved aggregates. Record limitations and missingness.
5. Update evidence and ICP artifacts only when the CRM supports a claim; keep provider records in Supabase.

Never bypass the field-map pause or copy raw CRM rows into Git.

Licensed CC BY 4.0 — GTM Adviser.
