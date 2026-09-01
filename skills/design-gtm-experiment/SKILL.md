---
name: design-gtm-experiment
description: Preregister a measurable GTM experiment with audience, trigger, channel, hypothesis, denominator, safeguards, owner, and decision rule. Use before launching a new message, channel, offer, or segment test; do not use for unmeasured activity lists.
---

# Design Gtm Experiment

Read company context, the approved ICP, evidence, and prior experiments.

1. State one falsifiable hypothesis and the belief it tests.
2. Define audience and exclusions, trigger, channel, unit of analysis, numerator, denominator, minimum sample, time window, safeguards, and owner.
3. Write an explicit continue/change/stop decision rule before execution. Avoid open and click rates as primary success metrics when revenue intent is the question.
4. Identify confounders and what must remain constant.
5. Save the preregistration as JSON or Markdown under `experiments/` with status `draft`; obtain human approval before any campaign plan.

Never retrofit the denominator or decision rule after seeing results without recording a new version.

Licensed CC BY 4.0 — GTM Adviser.
