# Security

## Report a vulnerability

Do not open a public issue for a suspected vulnerability. Email `security@gtmadviser.com` with reproduction details and the affected version.

## Data boundary

Agentic GTM has no telemetry and no GTM Adviser backend. Connected data goes directly between your machine, your selected providers, and your Supabase project. Do not commit `.env`, `.gtm/`, raw exports, contacts, provider identifiers, or action plans.

## Release checks

Public releases run tests plus secret, high-entropy, private-key, PII-pattern, prohibited-term, and Git-history scans. Maintainers also perform a human clean-room review of synthetic fixtures and documentation.
