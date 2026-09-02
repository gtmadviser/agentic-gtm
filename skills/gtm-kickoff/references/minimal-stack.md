# The minimal stack

A first experiment needs four things. Everything else is optional.

| Need | Minimal option | Connected option |
|---|---|---|
| A list | a CSV you already have, or 25 hand-researched accounts | `gtm source` through AI Ark or Blitz |
| Verification | a verification provider's web interface on the CSV | the same provider through its API, cached by email |
| A channel | a personal inbox and a manual LinkedIn routine of 10 messages per day | lemlist or Instantly, created paused through `gtm campaign apply` |
| A store | the files store under `.gtm/store/` | Supabase with `gtm db migrate` |

## The no-database path

The files store is the default when `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are absent. Tables are CSV files under `.gtm/store/`, action plans and apply results are JSON files next to them. Git ignores the directory. Everything the skills describe works unchanged: sourcing writes rows, `campaign plan` writes a plan, `review` reads metrics.

To move to Supabase later: run `gtm db migrate`, then upsert each CSV through the store's REST endpoint or ask the operator to load them; provider and provider_id keys make the load idempotent.

## The no-sequencer path

Results still need to be measured. Keep a CSV with one row per campaign and window:

```
campaign,variant,provider,window_start,window_end,sent,delivered,bounced,replied,positive_replies,meetings,opportunities
founder-signal-v1,A,manual,2026-09-01,2026-09-14,120,118,2,9,4,1,0
```

Import it with `gtm metrics import --file metrics.csv`. `gtm review outreach` computes rates, the certainty tier, and compares them with the experiment's decision rule.

## The no-CRM path

Skip the `crm` stage with a written decision. Evidence comes from customer interviews, the best and worst customer exercise, and experiment results. Record won and lost reasons in `market/icp.md` under observed evidence as they accumulate.

## What never changes

- Campaigns are created paused. Launching is a human action in the provider.
- Suppressions apply on the CSV path exactly as on the connected path.
- Verification before sending is mandatory on both paths.
- Person-level data stays out of Git on both paths.
