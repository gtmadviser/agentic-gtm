---
name: linkedin-engager-outreach
description: Discover LinkedIn posts from a company, its founders and reviewed employees, collect their engagers with HarvestAPI, qualify against the company's ICP and prepare routed LinkedIn outreach. Use for the full company-voices-to-outreach playbook or specific post reactions/comments. Includes roster review, selective enrichment, CRM checks and paused handoff. Excludes writing social posts and broad follower scraping.
---

# LinkedIn Engager Outreach

Turn a company's LinkedIn content into an evidence-backed, routed outreach pack.
Start from explicit posts or discover posts from the company, founders and
reviewed current employees. Engagement is a sourcing signal, not ICP fit.

## Establish the working scope

Read `gtm.yaml`, company context, approved ICP/personas, experiment and sender
voice. Reuse existing decisions and approvals within their accepted scope.

- Company page, founder/key-voice URLs, employee roster or explicit posts.
- Publication window and whether this is a seed batch or employee expansion.
- ICP revision, mandatory criteria, exclusions, territory and current CRM maps.
- Harvest account scope, dated price basis, endpoint cost bounds and total budget.
- Sender, LinkedIn capacity and the approved invitation/message approach.

If only post URLs are supplied, enter at engagement collection. If the user asks
for the full playbook, include roster and post discovery. Never silently turn
one explicit post into a scrape of every employee's history.

## Discover the sources

1. **Create a local run.** Raw data belongs in `.gtm/linkedin-engagement/` and
   the client store. Read [collection commands](references/harvest.md) and, for
   company/founder/employee discovery, [source roster](references/source-roster.md).
2. **Start with seed voices.** Collect posts from the company page and explicitly
   selected founders/key voices. Preserve voice identity, source type, post URL,
   post publication date and repost context. Count actual posts before expanding
   engagement spend. Zero posts is a valid result.
3. **Prepare the employee expansion.** Use company-scoped employee search, then
   bounded profile enrichment where needed to inspect current roles. Advisors,
   investors, former staff and ambiguous multiple roles require review. A search
   hit or company name in a headline is not proof of current core employment.
   Review the roster before fetching employee posts; dedupe seed/employee aliases.
4. **Use an explicit date window.** Scan all accepted pages; an old pinned post
   does not prove that later pages contain no recent posts. Quarantine missing
   dates. Founder/company/employee ordering is a configurable collection priority,
   not an ICP score or a universal intent ranking.

## Collect and qualify

5. **Plan each bounded stage offline.** Use `harvest_pipeline.py plan`. The plan
   snapshots inputs, limits, price basis and optional reviewed sample checkpoint.
   `fetch --approve <hash>` applies that exact scope. Existing authorization is
   sufficient when it covers the concrete plan; otherwise obtain it before spending.
6. **Collect engagements.** Fetch paginated reactions/comments and returned
   replies. Reuse fresh client/account-scoped cache entries. A pending or uncertain
   paid call blocks replay, including in a new run. Page/record/budget caps remain
   visible; separately paginated replies are not claimed complete.
7. **Normalize and reconcile.** Merge by provider ID and verified URL aliases,
   never names. Keep all source voices and interactions; exclude own-team actors
   from outreach. Use the persistent seen ledger for newly observed events.
   A reaction's first observation is not its actual engagement time. A new comment
   from an existing person adds evidence, not another enrollment.
8. **Screen cheaply, enrich selectively.** Use captured headlines for obvious
   exclusions and an inclusive shortlist. Retain unknowns for review; don't
   purchase profiles for the whole audience by default. Resolve selected opaque
   profiles and verify current roles/company, then dedupe again. Use CRM company
   facts first; enrich missing company facts or business signals only as needed.
9. **Keep fit dimensions separate.** Apply the approved rubric through
   [scoring and routing](references/scoring-and-routing.md). Record company fit,
   persona fit, criterion evidence, unknowns and the rubric revision. Engagement
   stays separate. Missing mandatory evidence holds the person regardless of score.
10. **Refresh relationships.** Check contact AND account lifecycle, associations,
    open deals, both owners, DNC/opt-outs, activities and existing campaign membership.
    Use the client's canonical relationship/suppression process when available.
    A new contact at a customer is not a new prospect. Failed lookup is not no match.
11. **Route before drafting.** Hard exclusions → exclude; customer/open deal →
    notify-only; owned relationships → owner handoff; conflicts or missing/stale
    checks → hold; reviewed unowned fit → outreach draft. The offline `qualify`
    command enforces these guards against supplied evidence. It does not fetch
    CRM facts or make LLM judgments for you.

## Prepare and review outreach

12. **Create distinct motions.** Owner handoffs carry the exact source post and
    supported business context. Net-new/unassigned outreach gets its own reviewed
    sender/territory cohort. Never load somebody else's owned-account list into
    the new campaign. See [outreach handoff](references/outreach-handoff.md).
13. **Use the client's tested sequence.** Bare invitations are a supported variant;
    when selected, place the warm post reference after acceptance. Do not replace
    an established bare-invite motion with a generic note. Existing connections
    skip the invite. Exact copy, delays and withdrawal behavior follow the
    experiment and platform capability; replies/opt-outs stop follow-up.
14. **Review a small sample, then expand.** Inspect identities, fit, route and
    exact copy. Record sample, rubric and recipe hashes with `gtm checkpoint`.
    An expansion plan can bind that record; changed artifacts invalidate it.
    Reuse a still-valid review instead of adding repetitive approval rituals.
15. **Stage and measure.** Use `stage-campaign` to prepare a paused destination or
    a documented manual import when the adapter cannot express the LinkedIn
    sequence. Verify rows, sender, schedule and conditions. Count invitations,
    acceptances, messages, human/positive replies, meetings and opportunities
    separately; keep denominators and missing outcomes explicit.

## Outputs and boundaries

- Local discovery: reviewed roster, `posts.json`, quarantined records and coverage.
- Local collection: immutable plan, saved pages, events, people and seen ledger.
- Client store: shared enrichment cache and per-run reserved-cost ledger.
- Local decisions: qualification, routing, sample checkpoint and exact outreach pack.
- Git: reusable recipes and reviewed aggregate reports; no raw lists or client IDs.

The helpers automate discovery, collection, selective enrichment, normalization,
seen-event reconciliation and deterministic qualification/routing guards.
Evidence interpretation, client CRM mapping, copy review and paused provider
handoff remain explicit agent/operator work. No helper sends messages, writes
CRM records, enrolls leads or installs a recurring job.

Licensed CC BY 4.0 by GTM Adviser. Helper scripts and runtime are MIT licensed.
