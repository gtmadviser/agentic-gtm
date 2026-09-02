# The first session for a new company

Ninety minutes, one operator, one person who knows the company. The outcome is a labelled company brief, a working ICP, a decision about the CRM, an approved first experiment, and a deliverability audit scheduled before any list exists.

## Sequence

1. **Readiness (5 min).** `gtm --json doctor`. Name the store backend. If it is `files`, say that everything works and that Supabase can be added later without losing data by importing the CSVs.
2. **Onboard (25 min).** Run `onboard-company-brain`. Ask only for facts not already in `context/company.md`. Label each statement: declared belief, observed evidence, hypothesis, decision. End with the missing-evidence register.
3. **Best and worst customers (15 min).** Ask for three customers the company would clone and three it regrets. For each: size, segment, who bought, what triggered the purchase, how long it took, what went wrong. The gap between the two lists is the ICP. Sharpen it to who plus trigger.
4. **ICP draft (15 min).** Run `refine-icp` with those six as evidence. Write the four sections. Attach confidence per criterion. Anti-ICP comes from the worst three.
5. **CRM decision (5 min).** Does a CRM exist with more than 30 closed deals? Yes: set `providers.crm`, schedule `inspect-crm` as the next session. No: record the decision to skip the stage and rely on interviews plus experiments.
6. **First experiment (15 min).** Run `design-gtm-experiment`. One hypothesis, one audience slice, one channel, a denominator, a minimum sample, safeguards, and a decision rule written now. Status `draft` until the owner approves.
7. **Deliverability first (5 min).** Schedule `audit-deliverability` before any list is built. If no sending infrastructure exists, the audit produces the setup checklist; nothing is sent from a main domain.
8. **Close (5 min).** Write decisions to `strategy/decisions.md`. Run `gtm --json next`. State the next artifact and who owns it.

## What the operator leaves with

- `context/company.md` with labels and a missing-evidence register
- `market/icp.md` with a working definition and confidence
- `strategy/decisions.md` with the CRM decision and the experiment approval status
- `experiments/<slug>.json` in `draft` or `approved`
- a scheduled deliverability audit

## Questions that save a week

- "Which customer did you close fastest, and what had just happened at their company?"
- "Which deal do you wish you had never taken?"
- "What does a buyer try before they call you?"
- "What can you not say in a cold message because it is not true yet?"
