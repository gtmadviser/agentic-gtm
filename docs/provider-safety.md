# Provider safety notes

Provider APIs differ, so the public contract is stricter than any single API.

## Campaign creation

The official [lemlist create-campaign API](https://developer.lemlist.com/api-reference/endpoints/campaigns/create-campaign) and [Instantly create-campaign API](https://developer.instantly.ai/api-reference/campaign/create-campaign) may return a newly created empty campaign as running or active. Agentic GTM therefore uses this order:

1. Create an empty campaign shell containing only its name and optional timezone.
2. Immediately call the provider's documented pause endpoint.
3. Verify paused/draft state.
4. Only then add sequence content or schedules.
5. Verify paused/draft state again.

Adapters never add contacts, sending accounts, activate a campaign, or call a send endpoint. If the pause cannot be verified, the adapter aborts before adding sequence content and reports the empty shell ID so the operator can inspect it.

## Sourcing

AI Ark uses its documented zero-based people-search pagination. Blitz uses its documented cursor pagination. Both normalize results to the same public contracts and keep provider-specific attributes and provenance outside Git.
