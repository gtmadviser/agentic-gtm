# Mailbox fleet

How to size, structure, warm, and rotate a sending fleet. This is the engineering under "high volume without torching your domain".

## Sizing formula

```
mailboxes_needed = daily_send_target / 20
domains_needed   = mailboxes_needed / mailboxes_per_domain   (2 for new provisioning)
```

| Daily target | Mailboxes | Domains at 2 per domain |
|---|---|---|
| 200 | 10 | 5 |
| 1,000 | 50 | 25 |
| 5,000 | 250 | 125 |
| 10,000 | 500 | 250 |

Some providers place many low-volume mailboxes on one tenant domain with a per-mailbox cap of 2 to 4 sends a day. Treat those pools as a diversity layer and size real volume on the standard 20-a-day mailboxes. Count per-domain capacity, not mailbox count, when such a provider is in the mix.

Start small. A first campaign needs 3 to 5 domains and 6 to 10 mailboxes. Scale the fleet only after two clean weeks of bounce, placement, and reply data.

## Domain strategy

- Register lookalike secondary domains: brand plus a short word (`get`, `try`, `hq`, `team`, `app`). Brand-adjacent names read as legitimate.
- `.com` only. Check availability in batches and register through a registrar with an API so DNS can be scripted.
- Point every domain at a 301 redirect to the real website. Never leave a sending domain unresolvable.
- Keep a domain registry in the store: name, registrar, nameserver type, provider, market, mailbox count, status (`active`, `warming`, `retired`, `burned`), first and last send. The registry is the source of truth; text files and provider dashboards are caches.
- Never set registrar-level forwarding on a domain whose nameservers belong to the mailbox provider. It silently replaces the nameservers and breaks every email record.
- Fresh domains for new mailboxes. Reused or retired domains can leave newly provisioned mailboxes stuck in a provisioning state with no API recovery path.

## Provider mix

Split the fleet across at least two mailbox providers and both consumer ESP families (Google-hosted and Microsoft-hosted mailboxes). One provider's outage or reputation event must not take the whole fleet down. Keep the provider group on every mailbox row; every metric in the audit is split by provider group.

Microsoft-hosted mailboxes may not be connectable to a sequencer via SMTP and IMAP passwords once basic authentication is disabled. Budget the manual OAuth step per mailbox and do not trust a connect call's success code until the mailbox has read mail for a few hours.

## DNS per domain

| Record | Requirement |
|---|---|
| SPF | One TXT with the provider's include and `-all` or `~all`; never two SPF records |
| DKIM | Selector CNAME or TXT from the provider, resolving |
| DMARC | `_dmarc` TXT with at least `p=none` and a reporting address; move to `p=quarantine` once aligned |
| Tracking domain | CNAME to the sequencer's custom tracking host, one per sending domain; the shared default host hurts placement |
| Root and www | A records so the domain resolves; some sequencers flag domains without them |
| Redirect | 301 to the real website |

Apply DNS only after every mailbox on the domain reports active. Records posted before the provider creates the zone are accepted and then silently dropped. Verify with `dig` at the authoritative nameserver, never by reading the API response.

## Warm-up

- Start warm-up the day the mailbox exists. 14 days minimum, 21 preferred.
- Ramp about 5 a day, adding 2 to 5 a day, up to about 40 warm-up sends a day, reply rate setting about 30%.
- Keep warm-up on while the mailbox sends cold email at low volume. Turn it off only when retiring the mailbox.
- Verify warm-up is running by re-reading the mailbox from the provider. Seat caps and export toggles can make an enable call succeed and do nothing.
- A mailbox exported from a provider into a sequencer can arrive with warm-up off. Re-enable in batches of 100 and re-read.
- Add a mailbox to a campaign only when its warm-up score is 90 or higher and it has warmed for at least 14 days.

## Persona and signature

- One persona per market: one surname, one to three first-name variants spread across domains. Usernames without leading or trailing dots, hyphens, or underscores.
- Every mailbox carries a signature matching its persona, set and re-read to confirm it is non-empty. A blank signature makes the signature variable render nothing and the prospect receives unsigned mail.
- Select campaign senders by persona from the registry, never by domain or country tag; providers can mix personas across the domains of one order.

## Rotation

Three pools, tracked by tag in the sequencer and by status in the registry:

| Pool | Meaning |
|---|---|
| active | On a campaign now |
| backup | Warmed, score 90 or higher, not on a campaign |
| warming | Under 14 days or score under 90 |

Daily health check: any active mailbox under the score threshold or with the wrong persona is replaced from the backup pool of the correct persona. Weekly performance check: the bottom 10% by bounce rotate out. Weekly reply-rate rotation: stage 1 at 50 sends with 0 human replies (watch), stage 2 at 100 sends with 0 human replies (rotate out). The watchlist is a stateful file; never delete it.

Sequencers usually replace the whole sender list on update. Read, modify, write back; never post a partial list.

## Retire, do not replace by default

When domains are burned, the default action is to retire them and stop paying. Replace capacity only when lead supply exceeds the remaining daily cap. Idle warmed mailboxes are pure cost.
