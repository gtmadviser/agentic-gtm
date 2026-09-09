# LinkedIn company voices to outreach

Use `linkedin-engager-outreach` for the complete company/founder/employee
playbook or enter with an explicit list of posts:

> Discover recent posts from our company, founders and reviewed current
> employees using Harvest. Collect the engagers within the agreed budget,
> qualify them against our ICP, and prepare owner handoffs or net-new outreach.

The skill implements the stages learned from earlier client pipelines without
bundling their recipients, IDs, proprietary criteria, copy or credentials.

| Stage | What runs | What needs review |
|---|---|---|
| Employee discovery | Company-scoped Harvest search | Actual current membership, concurrent roles and selected voices |
| Post discovery | Paginated company/profile posts within a fixed window | Topic relevance, roster scope and repost attribution |
| Engagement | Reactions/comments/returned replies, cached with cost reservations | Caps, incomplete reply coverage and any uncertain request |
| Identity | Offline dedupe and optional profile enrichment | Current employment, aliases and own-team suppression |
| Qualification | Separate company/persona rubric and relationship guards | Evidence interpretation and client-specific CRM checks |
| Handoff | Local owner tasks or a reviewed net-new outreach pack | Sender, exact copy, paused provider staging and verification |

Read the [skill](../skills/linkedin-engager-outreach/SKILL.md),
[source roster](../skills/linkedin-engager-outreach/references/source-roster.md),
[commands and spec](../skills/linkedin-engager-outreach/references/harvest.md), and
[qualification contract](../skills/linkedin-engager-outreach/references/scoring-and-routing.md).

The new `harvest_pipeline.py` helper uses the installed runtime and the selected
workspace's files/Supabase backend. `plan`, `roster`, `normalize`, `reconcile`
and `qualify` are offline. `fetch --approve <hash>` spends only against its exact
accepted stage, request cap and endpoint cost bounds. Account-scoped cached data
can be reused across runs; pending/uncertain paid calls cannot be blindly replayed.

Raw JSON/CSV, comments, profiles, CRM checks and copy remain in ignored `.gtm/`
or the client store. Only reusable assets and reviewed aggregates belong in Git.
The original explicit-post helper remains available for version-1 runs; its
request cap alone is not a monetary cap. New runs should use version 2.

## Sample checkpoints

Record an already-performed review of the sample, rubric and recipe artifacts:

```bash
gtm --json checkpoint record --artifact .gtm/linkedin-engagement/sample.json \
  --artifact market/icp.md --recipe-version linkedin-v2 --reviewer '<reviewer>' \
  --out .gtm/linkedin-engagement/sample-review.json
```

Bind it to an expansion plan with the helper's `plan --checkpoint <file>
--accepted-hash <hash> --recipe-version linkedin-v2 --workspace .` options.
Fetch rechecks the artifact contents before calls. A changed sample/ICP or
recipe revision invalidates that review. The checkpoint records human review;
it is not proof of live deployment state or authorization to send.

## Validation and remaining provider work

`uv run pytest` covers deterministic collection, aliases, budget/concurrency
behavior, qualification guards and installation. `uv run python
scripts/evaluate_skills.py --out .gtm/evals/linkedin-guards.json` runs the synthetic
routing suite. The [evaluation guide](../evals/linkedin-engager-outreach/README.md)
also defines saved-model comparisons and trigger cases; passing deterministic
tests is not a claim about an LLM's factual qualification accuracy.

No helper writes CRM records, enrolls leads, sends messages, withdraws invites
or installs a schedule. Paused staging/manual handoff follows the existing
provider and authorization boundaries. In particular, the lemlist adapter does
not yet verify every LinkedIn sequence setting automatically.

See [enrichment and starter upgrade notes](enrichment-and-starter-upgrade.md).

- [Get this implemented](https://gtmadviser.com/playbooks/linkedin-engagers)
- [Have GTM Engine operate it](https://gtmengine.io)
