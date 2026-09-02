# Wrap-up retrospective template

The retrospective of record for an engagement or a quarter of operation. Every number carries its denominator, window, and source. Learnings and anti-learnings are both quantified. Write it before the handover sign-off; it is the document the next operator reads to avoid repeating the expensive parts.

```
# <Company> outbound engine wrap-up

Period: YYYY-MM-DD to YYYY-MM-DD · Prepared by: <name> · Source: <store tables, report files>

## 1. The numbers (with denominators)
| Metric | Value | Denominator | Window | Source |
|---|---|---|---|---|
| Messages sent | | | | |
| Delivered | | sent | | |
| Bounced | | sent | | |
| Replies | | delivered | | |
| Positive replies | | delivered | | |
| Positive replies per 1,000 sent | | sent | | |
| Meetings | | positive replies | | |
| Opportunities | | sent, per 1,000 | | |
| Cost per opportunity | | | | |

Split the same table by channel (email, LinkedIn, phone, other) and by campaign family. The channel split is usually the biggest finding.

## 2. Phases
| Phase | Dates | What was built or run | Outcome |
|---|---|---|---|

## 3. Learnings (validated, with evidence)
- YYYY-MM-DD · <statement> · Evidence: <campaigns, n, rates> · Applies to: <copy rules, ICP, thresholds>

## 4. Anti-learnings (what not to repeat, with evidence)
- YYYY-MM-DD · <statement> · Evidence: <n sends, 0 results, cost> · Rule adopted: <the rule>

## 5. What is built but not launched
| Asset | State | Owner | Decision needed |
|---|---|---|---|

## 6. What is measured but not owned
<the gap between what the engine produces and what the company acts on, e.g. positive replies without a meeting owner; name the owner needed>

## 7. Infrastructure and cost
| Item | Count | Monthly cost | Recommendation (keep, retire, reassign) |
|---|---|---|---|

## 8. Incidents
| Date | What | Scope | Remediation | Verified | Pending |
|---|---|---|---|---|---|

## 9. Open items carried into the handover
See HANDOFF.md section 2. Every item has an ID, an owner, and a next action.

## 10. Recommendations
Ranked. One sentence each. The first one is the thing that produces revenue from what already exists.
```

## Writing rules

- Numbers come from the store or the reports. If a number cannot be sourced, it is not in the retrospective.
- Every rate names its denominator. "Reply rate" without "of delivered" or "of sent" is not a number.
- Zero results are reported as loudly as wins. A family of campaigns that consumed a large share of volume for no opportunities is the most valuable line in the document.
- Anti-learnings become rules, not regrets. Each one ends with the rule adopted.
- The channel split comes before the copy split. Channel usually dominates.
- Keep people out of it. Aggregate by role or team. Individual conversion tables belong in an internal file, not in a document that travels.
