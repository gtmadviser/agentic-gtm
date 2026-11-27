# Agentic GTM operating contract

1. Treat Git as the home for company context, decisions, approved aggregates, experiment definitions, and reviewable artifacts—not raw personal or provider data.
2. Treat the startup's Supabase project as the operational system for contacts, opportunities, activities, provider IDs, sync cursors, action plans, and approval records.
3. Label statements as declared belief, observed evidence, hypothesis, or decision. Never present an inference as a fact.
4. Inspect schemas before pulling data. HubSpot analysis pauses until a human confirms the field map.
5. Define a hypothesis, denominator, safeguard, and decision rule before executing an experiment.
6. Never write to an external provider without an immutable plan and the operator's explicit apply command.
7. Campaigns may only be created or updated in a paused state. This system cannot activate or send them.
8. Credentials come only from environment variables. Never print, persist, or accept them as CLI arguments.
9. Keep human owners on decisions and next actions. The agent prepares evidence and options; the operator remains accountable.
10. Every Slack message, posted or drafted, tags the person who has to act with a real mention (`@Short` from the `team` roster in `gtm.yaml`) and links every campaign it names to the provider UI (`[[lemlist:<campaign_id>|<name>]]`). `gtm report slack plan` renders both and lists what it could not resolve.
