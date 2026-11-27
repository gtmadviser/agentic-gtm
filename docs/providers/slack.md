# Slack reference

Public docs: https://api.slack.com/methods

## Role in the engine

Slack is where the weekly GTM review lands once a human approves it. That is the only write the engine makes to Slack.

## Auth

| Mode | Env vars | Verification |
|---|---|---|
| Bot (recommended) | `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID` | `auth.test` before posting; `chat.postMessage` returns a message `ts` that is recorded as the provider ID |
| Webhook (fallback) | `SLACK_WEBHOOK_URL` | none; the post is accepted but delivery is unverified and the report says so |

Bot scopes needed: `chat:write` for the target channel, `users:read` and `users:read.email` to turn roster emails into mentions. Invite the bot to the channel first.

## Mentions and campaign links (required in every stakeholder message)

| Write in the draft | Rendered by `gtm report slack plan` | Source |
|---|---|---|
| `@Max` (any `short`, `name` or `aliases` of a roster member) | `<@U012ABC>` | `team` in `gtm.yaml`; `slack_user_id`, else `users.lookupByEmail` |
| `[[lemlist:cam_123|Vorstand Sie]]` | `<https://app.lemlist.com/teams/<team>/campaigns-v2/cam_123|Vorstand Sie>` | `links.lemlist_campaign` template; team ID from `GET /team` |

Bots without `users:read.email` (common for an agency bot in a Slack Connect channel shared with the client) cannot look up emails. Then set `slack_user_id` in the roster once: list `conversations.members` of the shared channel and identify each person from `users.info` or the channel history.

The plan output lists `unresolved_references`. Fix them before applying: an unresolved name posts as plain text and nobody gets notified.

Drafts that a human pastes into Slack do not turn `@Max` into a mention. For those, write the full display name and tell the operator to pick it from autocomplete, and write campaign links as plain URLs.

Base URL: `https://slack.com/api`. Header: `Authorization: Bearer <token>`.

## Behaviour

- `gtm report slack plan --report <file>` creates an immutable plan holding the channel, the text, and `unfurl_links: false`.
- `gtm report slack apply --plan <id>` posts exactly once. A second apply on the same plan returns `already_applied` without posting.
- Long reports: Slack truncates very long messages. Keep the posted summary short and link to the full report in the repository.

## Gotchas

| Symptom | Cause | Fix | Observed |
|---|---|---|---|
| `not_in_channel` | bot not invited | invite the bot, or use a public channel it can join | 2026-05 |
| `channel_not_found` | channel name used instead of ID | use the channel ID | 2026-05 |
| Duplicate posts | script retried after a network timeout | apply only through a plan; the idempotency record stops repeats | 2026-05 |
| Webhook post "succeeded" but nobody saw it | webhook bound to a different channel | prefer bot mode; label webhook posts unverified | 2026-05 |

## Verify before coding

Check the method page for the current required scopes. Slack changes scope names and deprecates methods with notice, but the notice is easy to miss.
