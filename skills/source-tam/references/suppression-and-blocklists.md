# Suppression sets and blocklists

Suppression protects relationships, legal standing, and reputation. It is applied before a list is usable and is maintained continuously while campaigns run.

## The sets

| Set | Source | Granularity | Refresh |
|---|---|---|---|
| Customers | CRM companies with a won deal or active subscription | domain | daily |
| Open opportunities | CRM deals in any open stage | email plus domain | every 15 minutes while campaigns run |
| Competitors | `market/competitors.md` plus a maintained domain list | domain | on change |
| Opt-outs and unsubscribes | sequencer unsubscribe events, reply classification | email plus domain when requested | continuous |
| Complaints and legal | a ticket or sheet maintained by the operator | domain | on change |
| Bounced | send events | email | every build |
| Own domains, partners, investors | `context/company.md` | domain | on change |

## The CRM-to-blocklist rule

When a contact enters any deal pipeline at any stage, stop cold-emailing them and their colleagues.

1. Poll the CRM for deals created in the last 15 minutes on a 5-minute schedule. The overlap is deliberate; it survives a missed run.
2. For every associated contact, add the exact email to the sequencer blocklist.
3. Also add the company domain, unless the domain is generic: free mail providers, ISPs, large shared corporate domains, franchise networks. Maintain the generic list explicitly and grow it when a shared domain appears in 3 or more deals.
4. Never blocklist your own domains.
5. Write an audit row: `blocked_value, kind (email|domain), reason, deal_ref, added_at`.
6. Do not auto-unblock when a deal is deleted. Removal is a human action with a note.

Sequencer blocklist endpoints are idempotent enough that duplicate additions are harmless; make the workflow continue on a duplicate error.

## Reply-driven suppression

Reply classification (see `review-outreach`) feeds this set. `unsubscribe`, `hostile`, and `not_fit` replies suppress the email immediately and the domain when the reply asks for it. `not_now` sets a re-approach date; it does not suppress.

## Deletion policy

Deleting records from a sequencer to free quota is fine only when:

- the store holds the contact, the send history, and the reply content for every record to be deleted,
- the record never replied and carries no interest label,
- the campaign has finished sending,
- a dry run listed exactly what will go, and
- the deletion log records every value removed.

Replied and interested records are never deleted from anywhere.
