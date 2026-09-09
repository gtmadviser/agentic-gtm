# LinkedIn workflow evaluations

All fixtures are fictional. No test calls Harvest, a CRM or a sequencer.

Run the deterministic evidence/routing guards:

```bash
uv run python scripts/evaluate_skills.py --out .gtm/evals/linkedin-guards.json
```

For an agent evaluation, give the agent only the skill, `fixtures.json` and the
case prompt. Merge each case's `overrides` into `base_person`; supply the rubric
and fixed reference time. Ask it for the qualification artifact and next-action
pack, with no external actions allowed. Do not provide `expected.json`.

Save outputs as `{ "case-id": { "route": "...", "enrollment_ready": false,
"external_actions": [] } }`. Include the full evidence and separate company/persona
assessment for human grading as well. Capture actual attempted tool actions in
`external_actions`; a model's self-reported empty list is not execution evidence.

```bash
uv run python scripts/evaluate_skills.py --results .gtm/evals/candidate.json \
  --metadata .gtm/evals/candidate-metadata.json --out .gtm/evals/candidate-grade.json
```

Metadata requires `skill_commit`, `model`, `settings` and `run_at`. Compare the
same cases/configuration against the previous skill revision and a no-skill
baseline. Check `trigger-cases.json` separately for correct invocation. Judge
factual support and copy accuracy independently from the deterministic checks;
these fixtures are too small to establish general qualification accuracy.

Passing the deterministic run proves guard behavior only. It is not a claim
that an LLM has been evaluated. Raw model outputs and any client-derived cases
stay in ignored `.gtm/evals/`; publish only reviewed aggregate comparisons.
