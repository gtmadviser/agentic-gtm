# Credit approval

Every operation that consumes paid credits, calls a metered API, or triggers a per-search charge is preceded by a plan the operator approves. This includes probes.

## The plan

```
Provider:            <slug>
Operation:           <search accounts | search contacts | enrich | verify>
Billing model:       <per hit | per search | per record | per technology found | flat rate>
Remaining credits:   <number, read live from the provider>
Rows in scope:       <number>
Expected spend:      <credits or currency, with the formula>
Hard cap:            <credits or currency; the run stops here>
Purpose:             <experiment id and what the result unlocks>
Resumable from:      <cache path or checkpoint>
Approved by:         <name, timestamp>
```

## Rules

1. Read the remaining balance from the provider before estimating. Never estimate from memory.
2. State the billing model. Per-search and per-technology-found models make cost per usable contact equal price divided by hit rate. Put that number in the plan.
3. Set a hard cap. The run aborts at the cap and reports the checkpoint.
4. Run from cache. A re-run must not re-bill rows that already have a result.
5. Present the plan, then wait. Approval is a human message, not a default.
6. Record actual spend next to the plan afterwards. The gap between expected and actual spend is a data-quality finding.

## Cheap first, always

Probe with 5 rows on a new provider to confirm the response shape and the billing before the 25-row probe. A flat-rate provider you already pay for is tried on every eligible row before any per-credit provider sees one.
