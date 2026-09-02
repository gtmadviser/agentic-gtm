# Burn detection

A "burned" domain is one whose reputation is damaged enough that mail from it does not reach inboxes regardless of copy or list. The signal is zero human replies at a volume where zero is statistically implausible. This method turns that intuition into a test, then adds the two rules that prevent the expensive mistake: judge at the domain level and never automate the irreversible step.

## Definitions

- **Send**: one outbound message from a mailbox on the domain in the window.
- **Reply**: any inbound message to that mailbox in the window. Count auto-replies and out-of-office separately, but any reply proves the domain can deliver.
- **Provider baseline** `p`: reply rate of the whole provider family (all domains on the same mailbox provider and ESP family) in the same window. The family must itself be healthy, at least 1%, or no domain in it can be judged.
- **Judged sends** `N`: sends on the domain in the window.

## The test

A domain is a **burned candidate** when all three hold:

1. Domain reply rate is exactly 0%.
2. `N >= 80` (below that: "insufficient", never a verdict).
3. `P(0 replies | p) = (1 - p)^N < 0.02`.

Minimum `N` for the test to be able to fire, by baseline:

| Provider baseline `p` | `N` needed for `(1-p)^N < 0.02` |
|---|---|
| 1.0% | 390 |
| 1.5% | 259 |
| 2.0% | 194 |
| 2.5% | 155 |
| 3.0% | 129 |
| 5.0% | 77 |

Formula: `N_min = ln(0.02) / ln(1 - p)`. With typical baselines of 2% to 3%, a domain needs 130 to 200 sends before zero replies means anything. That is why the unit is the domain, not the mailbox: at 20 sends a day per mailbox, a single mailbox takes weeks to reach the threshold and mailboxes on low-volume tenant pools never do.

## Buckets

| Bucket | Rule |
|---|---|
| Burned candidate | Test fires and the live cross-check confirms 0 replies |
| Healthy | Reply rate at or above half the provider baseline |
| Weak | Above 0% but under half the baseline; watch, do not act |
| Insufficient | `N < 80` or the family baseline is under 1% |
| Recovered | Flagged in a prior audit, now healthy on a longer window; un-flag and record the retraction |
| Isolated bad mailbox | 0 replies at 80 or more sends on a domain whose sibling mailboxes reply normally; swap the mailbox, keep the domain |

## Worked example (fictional)

Provider family "north-google" in the window: 40,000 sends, 1,000 replies, baseline `p = 2.5%`. Six domains on the family:

| Domain | Mailboxes | Sends | Replies | `(1-p)^N` | Bucket |
|---|---|---|---|---|---|
| a.example | 2 | 410 | 9 | n/a | Healthy (2.2%) |
| b.example | 2 | 396 | 0 | 0.00004 | Burned candidate |
| c.example | 2 | 120 | 0 | 0.048 | Insufficient for a verdict; watch |
| d.example | 2 | 402 | 3 | n/a | Weak (0.7%); watch |
| e.example | 1 | 61 | 0 | n/a | Insufficient (`N < 80`) |
| f.example | 2 | 388 | 12 | n/a | Healthy (3.1%) |

Only `b.example` is a candidate. It goes to the live cross-check: read the inbox of each of its mailboxes through the sequencer API for the same window. If any human reply exists that the store missed, the domain drops to Weak. If the cross-check confirms zero, it is reported as burned with `N`, `p`, and the probability.

`c.example` is the important row. Zero replies at 120 sends with a 2.5% baseline happens by chance about 5% of the time. It is not burned. It is re-judged next window.

## The false-positive rule

Verdicts made on short windows reverse. A domain flagged at 0 for 250 sends can reply at a normal 3% once the window triples. If the irreversible step (deleting mailboxes, cancelling the provider order, dropping the domain) had been taken on the first verdict, the capacity would be gone for nothing and the retraction impossible.

Therefore:

1. The audit reports candidates. It never retires anything.
2. The first action on a candidate is reversible: remove its mailboxes from campaigns and tag them `quarantine`. Sending stops, nothing is destroyed.
3. Re-judge every quarantined domain at the next audit on the longer window. Un-flag any that recover and write the retraction into the report and into `strategy/decisions.md`.
4. Retire (stop paying, delete) only after a candidate survives two consecutive windows and a human approves the list explicitly, by domain.
5. Before retiring, confirm the domain is excluded from every campaign build filter so it cannot re-enter a campaign when a paused campaign resumes.

## Bimodal patterns are the strongest evidence

When 20 domains share the same provider, batch, volume, and window, and the outcome splits into "0 replies" and "3% to 6% replies" with nothing in between, the domain is the only variable. Report the split explicitly; it is far stronger than any single domain's probability.

## Record

`.gtm/deliverability/domains.csv`: domain, provider group, mailboxes, sends, replies, human replies, reply rate, baseline, probability, bucket, prior bucket, last send. In Git: counts per bucket, the bimodal split if present, and the retractions. Never the domain list.
