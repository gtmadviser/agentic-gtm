# Market signal sources

Public source types, what each one can prove, and how long the evidence stays fresh. Everything here is public and dated; private or scraped gated content is out of scope.

| Source type | What it proves | What it does not prove | Freshness window |
|---|---|---|---|
| Pricing page | commercial model, minimums, tiers, on the observed date | actual prices paid | 3 months |
| Product docs and changelog | shipped capabilities, integration list, setup path | usage or quality | 6 months |
| Public customers page, case studies | who they cite as customers; the jobs they emphasise | how many customers, retention | 12 months |
| Review sites (with dates) | recurring praise and complaints; who writes reviews (role, company size) | representativeness | 12 months, weight recent reviews |
| Job postings (theirs) | roadmap direction, markets they invest in, tech stack | timing | 3 months |
| Job postings (buyers) | tools mentioned as requirements; adoption in a segment | preference | 6 months |
| Public filings, funding announcements | stage, capital, stated strategy | execution | 12 months |
| Conference talks, webinars | positioning language, target buyer, proof they choose to show | | 12 months |
| Community threads (forums, public groups) | workarounds, internal alternatives, migration pain | prevalence | 12 months |
| Analyst or press coverage | category framing and vocabulary | market size unless the method is published | 12 months |
| Your own pipeline report | which alternatives win and lose against you, in aggregate | anything about the alternative's other customers | until the next report |

## Recording a signal

One row in `market/sources.md`:

| ID | URL or document | Observed date | Supports | Claim or observation | Confidence | Notes |
|---|---|---|---|---|---|---|
| S-011 | pricing page URL | 2026-09-01 | commercial model of Harbor Sync | observation | high | screenshot in local notes, not in Git |

- `Claim`: the vendor or a third party says it. `Observation`: you saw the state of a page, a filing, or a dated review yourself.
- `Confidence`: high (direct observation, primary source), medium (dated third party), low (undated or second-hand).
- Screenshots and downloads stay local. The register holds the pointer and the date.

## Freshness handling

- A signal past its window is marked `stale` in the profile. Stale signals may inform questions, never copy.
- Re-verify pricing pages before any copy that references a commercial difference.
- Review-site signals: weight the last 12 months; note the reviewer's role and company-size band, because a complaint from a 2,000-person company says little about an 11 to 50 buyer.

## Substitutes and do-nothing

The strongest alternatives are often not vendors. Look for:

- Spreadsheet or script workarounds described in community threads and job postings ("maintain the on-call spreadsheet").
- "Built in-house" and "no decision" in your own loss reasons.
- Adjacent tools stretched to do the job (a ticketing tool used as a scheduler).

Profile at least one substitute and record do-nothing as an explicit bucket with the loss-reason share that supports it.

## What not to collect

- Content behind logins, NDAs, or paywalls you do not have rights to cite.
- Scraped customer lists.
- Private statements from mutual customers or former employees.
- Market-size figures without a published method.
