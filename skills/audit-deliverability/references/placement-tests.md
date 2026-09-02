# Inbox placement tests

A placement test sends one message from each tested mailbox to a seed list of real inboxes at the major consumer and business ESPs and reports where each landed. It is the only direct measurement of reputation. Everything else is inference.

## Design

- **One test per provider group.** A group is one mailbox provider plus one ESP family (for example "provider A, Google-hosted"). Mixing groups in one test hides which infrastructure is failing.
- **Seed list** spanning the recipient ESPs your market uses: Gmail, Outlook and Microsoft 365, and the regional business mail hosts. 20 seeds per test is enough for a group signal.
- **Weekly cadence**, same weekday, same seed list, so the series is comparable.
- **Sample the senders**: 20 to 30 mailboxes per group per test. Rotate the sample so every mailbox is tested at least monthly.
- **Named tests** with a stable prefix and a date, so the API can list and sort them without a local index.

## Pull, never ask

Pull results through the sequencer's placement analytics API. Never ask the operator to paste numbers or read a dashboard. Do not rely on a local "latest test IDs" file: list all tests via the API, sort by creation time, filter to completed tests with the standard prefix.

Some providers charge credits per test. Pulling existing results is always free and read-only. Creating a metered test requires explicit approval; check remaining credits first.

## Read in this order

1. **Aggregate inbox rate per test group.** The headline. Pass bar 80% or higher inbox on the primary consumer ESP; fail if any group is spam majority.
2. **Per-recipient-ESP split.** The actionable view. A group at 50% inbox overall can be 100% inbox at one ESP and 0% at another; the aggregate hides the real problem. Keep "other or unknown ESP" as its own bucket; never merge it into Gmail.
3. **Per-sender ranking**, only when one ESP is not uniformly broken. If every sender in a group lands in spam at one ESP, ranking senders is noise. Skip the table and report the group verdict.
4. **Authentication pass rates**: SPF, DKIM, DMARC per sender. Any failure is a fixable misconfiguration and goes in the findings table as material, blocking if the group is launching.

Count "Important" or "Primary" tab placements as inbox. Count promotions or updates tabs separately; they are not spam but not primary either. Some providers report the important tab under "other tabs" and make a 25% inbox rate look like a failure when it is not. Compute effective inbox rate as inbox plus important over total.

## Record

`.gtm/deliverability/placement-YYYY-MM-DD.csv` with one row per seed delivery: test id, provider group, sender (local only), recipient ESP, placement, spam flag, SPF, DKIM, DMARC, spam score if the provider reports one. In Git, the report carries the group-level and ESP-level tables only.

Keep the weekly series. Trend beats snapshot: a group sliding from 92% to 84% to 78% over three weeks is a material finding before it is a blocking one.

## Interpreting against real replies

Placement tests measure seed inboxes, not prospects. Compare them with the reply-rate rotation output. A group with 90% seed inbox and 0 replies at 100 sends per mailbox has a list or copy problem, not a reputation problem. A group at 40% seed inbox with normal replies is at risk but not yet failing. Both signals go in the report.

## Common pitfalls

- Reading only the aggregate. The split by recipient ESP is where the fix lives.
- Trusting a local cache of test IDs. Manual tests created since the last cron run are missing from it.
- Treating a single test as a verdict. Two consecutive failing tests on the same group confirm; one can be a seed-list artefact.
- Creating metered tests in a loop. Each one costs credits and the operator did not approve it.
- Ignoring auth failures because the inbox rate looks fine today. They will not look fine next week.
