# Company voices and post discovery

Use two scopes: a seed batch of company/founder/key voices, then expansion to
reviewed employees. Both use the same normalized post schema and engagement
collector. Priority changes collection order; it never supplies fit points.

## Roster

The `employees` stage uses `profile-search?currentCompany=<company URL>` with
finite pages. Results are candidate employees, initially `membership: review`
and `approved: false`. Hidden/missing identities go into quarantine.

Use a separate `profiles` stage for the candidate roster where current-role
validation is needed. The offline `roster` command joins those profiles:

```bash
python <skill-path>/scripts/harvest_pipeline.py roster \
  --employees .gtm/linkedin-engagement/roster/employees.json \
  --profiles .gtm/linkedin-engagement/roster-profiles/profiles.json \
  --company https://www.linkedin.com/company/synthetic-company \
  --out .gtm/linkedin-engagement/reviewed-roster.json
```

This example company is fictional. Match exact company identities or separately
verified aliases, not a substring of its name. A single resolved current role at
the target company is `core`; a resolved role elsewhere is `not_current`;
multiple/unknown roles remain `review`. Array order is not proof of a primary
job. Inspect founders with concurrent projects, board members, investors,
advisors and contractors rather than sweeping them into the employee expansion.

Review candidates and set `approved: true` only for selected voices. Each employee
needs `membership` (`core`, reviewed `core_multi`, or `reviewed_exception`) and
`membership_evidence` with the current roles, source and observation date.
Unknown/private profiles remain held. Founder sources may be selected explicitly
without treating the employee-search heuristic as authoritative.

Keep the full roster for own-team suppression; create a separate selected source
list for discovery. Deduplicate public/opaque aliases and founders already in
the seed batch. Preserve excluded/held rows in an audit artifact.

## Posts

A `posts` input row has `url`, `kind` (`company`, `founder`, `employee`), `approved`,
and optional `source_id`/`priority`. Employee rows carry the membership evidence
above. Default order is founder, company, employee; use explicit priorities if
the experiment calls for another order.

The stage scans a fixed inclusive `published_since` / exclusive `published_until`
window, with timezone-aware timestamps. It paginates both profile and company
posts and forwards returned pagination tokens without changing their case.
It does not stop at the first older post because posts can be pinned/reordered.
Missing publication dates are quarantined. Page caps mean partial discovery.

`posts.json` deduplicates exact post identities while retaining every discovering
voice in `sources`. Reposts keep their context: do not claim an employee authored
the original text. Review topic relevance and source identity before spending
on engagement. A founder with no posts simply contributes no engagement jobs.

For recurring operation, an overlapping recent-post window plus persistent
seen-event comparison catches later-discovered engagement on earlier posts.
Choose the cadence/window for the client; no schedule is installed by this skill.
Record first seen separately from post publication and comment time.
