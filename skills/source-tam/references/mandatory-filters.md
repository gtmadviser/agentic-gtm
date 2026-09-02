# The three mandatory filters

Every campaign build passes its candidate senders and recipients through three filters before the list is called usable. Each filter exists because a real pipeline skipped it and paid for it. The pattern generalizes.

## 1. Sender side: burned domains and dead infrastructure

Two checks, because they catch different things.

**Burned-domain registry.** A file or table with `domain, status, reason, since`. Status in `burned` or `retired` means the domain never sends again. Any mailbox on that domain is dropped from every build, forever. Keep the evidence next to the decision so a later audit can overturn it.

**Live-infrastructure allowlist.** Sequencers report mailboxes as active long after the underlying provider cancelled them. Build the allowlist from the provider inventory (which mailboxes exist and are healthy today) joined to the sequencer inventory, and pass only the intersection. Never trust the sequencer's own status flag alone.

Typical incident shape: half the senders in a large campaign were cancelled infrastructure that the sequencer still called warm. The fix was not a bigger burn list; it was a second filter with a different source of truth.

## 2. Recipient side: bounced and previously contacted

A recipient that ever bounced never enters a build again. Source the exclusion set from ground truth, the send events themselves, not from a nullable status column on the contact record. A status column that is empty for a whole pool passes everything.

Typical incident shape: a re-approach pool re-imported contacts that had bounced months earlier, because the build filtered on a contact flag that was never populated. The fix was a bounced ledger rebuilt from send events and cached locally.

Extend the same ledger with `last_contacted_at` per domain so the re-approach window (60 days minimum, 90 default) is one lookup.

## 3. Cross-campaign domain dedupe

Sequencers dedupe by email, not by domain. Two people at the same company in two campaigns is a duplicate to the recipient. Maintain a domain ledger `(domain, country, campaign, loaded_at)`. One decision maker per domain per campaign, and no domain in two live campaigns at once.

## File layout under `.gtm/suppressions/`

```
burned-domains.csv        domain,status,reason,since
usable-senders.csv        mailbox,provider,health,checked_at
bounced-recipients.csv    email,bounced_at,campaign
domain-ledger.csv         domain,country,campaign,loaded_at
```

All gitignored. Refresh from the source of truth before every build. Keep the refresh timestamp in the build log.

## Rules

1. A filter whose source is empty or unreachable fails the build. It does not pass it.
2. Log the count before and after each filter, and the list of what was dropped, in the build log.
3. Run sender-side filters on every build. Run recipient-side filters on every build. Run the domain ledger on every build.
4. Anyone who bypasses a filter writes the reason and their name into the build log.
