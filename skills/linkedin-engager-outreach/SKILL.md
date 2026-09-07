---
name: linkedin-engager-outreach
description: Turn LinkedIn post reactions, comments, and replies into an ICP-scored audience and a reviewed LinkedIn outreach pack using HarvestAPI. Use for post engagers, people who liked or commented on specific posts, and the Harvest to ICP to LinkedIn outreach process. Includes deduplication, profile resolution, CRM ownership checks, suppressions, and paused campaign handoff. Do not use for broad follower scraping or immediate sending.
---

# LinkedIn Engager Outreach

Produce a small, evidence-backed audience from explicit LinkedIn posts, score it
against this company's approved ICP, and prepare the appropriate LinkedIn next
action. Raw engagement is a sourcing signal, not proof of fit or buying intent.

## Inputs and scope

Read `gtm.yaml`, `context/company.md`, `market/icp.md`, the active experiment, and
the sender's approved voice examples. Resolve paths from the company workspace.
Use existing session decisions before requesting missing inputs.

- An explicit list of post URLs or post URNs, with topic, author and publication date when known.
- An approved ICP version, exclusions, geography, persona and company criteria.
- A bounded Harvest budget: post list, page cap, request cap, current pricing, and approved spend ceiling.
- Current CRM account/contact ownership, customer/open-deal state, opt-outs, recent outreach and campaign memberships.
- Intended sender, territory, language, LinkedIn relationship state and channel capacity.

If ICP approval is missing, collect existing local evidence and prepare the ICP
decision through `refine-icp`. If CRM or suppression data is unavailable, scoring
can continue; mark routing unresolved and withhold an enrollment-ready export.

## Procedure

1. **Create a local run.** Use `.gtm/linkedin-engagement/<run>/`. The supplied
   script creates its own ignore file. Never put raw data in `company-knowledge/`,
   `reports/` or public examples. Read [Harvest collection](references/harvest.md).
2. **Plan collection without spending.** Run the helper's `plan` command with
   explicit posts and finite limits. Show the request ceiling and current price
   basis. Existing approval covering the same scope and budget is sufficient;
   otherwise obtain approval for this concrete paid plan before `fetch`.
3. **Collect or reuse cached pages.** Fetch reactions and comments, flatten
   returned replies, and preserve pagination and completeness. The helper does
   not separately crawl comment-reply endpoints. Never call a capped or partial
   result “all engagers.” Paid requests are not automatically retried.
4. **Normalize people and evidence.** Run `normalize`. Merge reactors,
   commenters and repliers by provider person ID and normalized profile URL;
   never merge on name alone. Exclude author-marked actors and organization
   profiles. Record source posts and every distinct interaction. Quarantine
   missing identities; do not lose them silently.
5. **Find newly observed evidence.** Compare event IDs with the local seen ledger
   across runs. Preserve earliest `first_seen_at` and each observation date.
   Reactions have no reliable engagement time. Post dates bound collection;
   first-seen dates describe discovery, not when somebody reacted. A new comment
   from an existing person is new evidence, not another lead.
6. **Prequalify cheaply, then resolve.** Use headlines only to flag obvious
   exclusions or candidates for review. Resolve opaque `/in/ACo…` identities
   through Harvest profile lookup only when needed, approved and uncached.
   Use the resolved current role/company for final fit. Save opaque-to-public
   aliases and deduplicate again before CRM matching. See the collection reference.
7. **Score ICP fit with cited evidence.** Apply the company's approved criteria
   using [scoring and routing](references/scoring-and-routing.md). Record each
   criterion, value, evidence, confidence and unknown. Keep `fit_score` separate
   from observed engagement. Unknown company size or ambiguous employment is
   a review state, never an assumed pass. Do not import another client's thresholds.
8. **Match CRM and suppress.** Match people by configured LinkedIn property or
   verified email, accounts by domain/company LinkedIn identity. Check both
   contact and account ownership and lifecycle plus associated open deals.
   Exact matches outrank fuzzy names. Refresh these checks before staging.
9. **Route each person.** Opt-out/competitor/own-team/excluded → exclude;
   customer or active deal → notify-only; owned account/contact → owner review;
   unresolved facts/conflicts → hold; eligible unowned prospect → outreach draft.
   A notify-only row describes a task to prepare, not permission to message anyone.
10. **Draft a LinkedIn pack.** Follow [outreach handoff](references/outreach-handoff.md)
    and `write-outreach`. Use the actual post and relationship context, one reason
    to connect and a low-friction question. Invite only if not connected; message
    after acceptance or an existing connection. An invite rejection, opt-out or
    reply stops automated follow-up. Review every row in the initial probe.
11. **Stage the reviewed selection.** Hand off to `stage-campaign` with audience,
    sender, exact copy, schedule, ownership checks and evidence. Keep campaigns
    paused and verify uploaded rows/settings. A documented manual import is the
    fallback where the adapter cannot express LinkedIn steps or conditions.
12. **Measure and learn.** Record collected people, unique identities, eligible,
    held/excluded, invites, accepted connections, human/positive replies,
    meetings and opportunities. Distinguish invitations from messages. Use
    `review-outreach` to choose the next experiment against its decision rule.

## Outputs

| Artifact | Location | Contents |
|---|---|---|
| Collection plan and state | local run `plan.json`, `state.json` | approved scope hash, request count, cached pages, failures |
| Evidence and people | local run `events.json`, `people.csv` | source post, person identity, role, observed dates, interactions |
| Qualification | local run `qualification.csv` | rubric version, score, cited evidence, unknowns, exclusions, reviewer |
| Routing | local run `routing.csv` | CRM matches, owners, lifecycle, deals, suppression/recency checks, route and reason |
| Outreach pack | local run `outreach.csv`, `handoff.md` | reviewed target selection, sender, exact copy, evidence, paused staging instructions |
| Seen ledger | `.gtm/linkedin-engagement/seen.json` | stable event IDs and earliest observations; never enroll twice |
| Aggregate review | `reports/linkedin-engagers-<date>.md` | funnel counts, cost, completeness, precision, decisions; no person data |

The script implements collection and normalization. Scoring, profile enrichment,
CRM decisions, ledger reconciliation and outreach are explicit agent workflows
with reviewable artifacts; they are not automated provider writes.

## Completion checks

- Paid calls stayed inside approved scope; partial pages and uncertain requests are disclosed.
- Every selected person has an identity, source post and supported current ICP fit.
- Multiple interactions and identity aliases cannot create duplicate enrollment.
- Ownership, open deals, suppression and contact history were checked at both account and person level.
- Unknowns remain on hold; engagement alone never increases the fit score.
- The pack records a reviewed sender, exact copy and a paused destination or manual handoff.
- Raw lists, comments, CRM IDs and credentials remain local; Git receives only reusable files and aggregates.

Licensed CC BY 4.0 by GTM Adviser. The helper script is MIT licensed.
