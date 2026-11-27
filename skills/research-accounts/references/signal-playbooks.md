# Signal playbooks

Each playbook answers three questions: how to observe the signal, how to verify it, and the one sentence it earns in copy. A signal that cannot be verified with a url is not a signal.

## Own-product signals

The strongest signals come from the company's own systems, not from a vendor. Anyone who signed up, filed an issue or hit a limit has already stated the pain. Work this table before any public signal, and before sourcing a cold list at all: a warm pool that clears the experiment's minimum sample outranks a cold one.

| Signal | How to observe | Verify | Decay | The sentence it earns |
|---|---|---|---|---|
| Signup or trial started | product database, auth log | account id plus created date | 30 days | "You set up <product> on <date> and stopped at <step>. Most teams stall there because of X." |
| Free tier in active use | usage events, seat count | 2 or more active weeks, or seats above 2 | 30 days | "Three people at <company> use <product> every week. The next thing that usually breaks is Y." |
| Plan limit hit or action failed | limit events, error log | event id plus date | 14 days | "Your team hit the <limit> twice last week. That is the point where Z starts to cost time." |
| Issue, ticket or feature request naming the pain | issue tracker, support inbox, public repo issues | issue url or ticket id | 60 days | "Your issue about <pain> is the one we hear most from <segment>. Here is what changed." |
| Public repo interaction (star, fork, issue, discussion) | the public repository | url | 90 days | "You opened a discussion on <topic> in <repo>. Curious whether that is still open." |
| Event, webinar or waitlist registration | registration list | registration id plus date | 30 days | "You signed up for <event> on <topic>. Two of the questions there were about X." |
| Lapsed user | last activity date | 60 or more days idle after prior activity | 90 days | "You used <product> in <month> and then stopped. What did we get wrong?" |

Rules for own-product signals:

- The relationship is the consent basis. Record it in `consent_basis` and keep product accounts out of cold-list suppression logic; they are a separate pool with its own experiment.
- State only what the recipient can verify in their own account or on the public repo. Never cite one person's usage to a colleague.
- A paying customer or an account with an open opportunity is never enrolled in a campaign. Route it to the owner (see `signal-schema.md`, routing).
- Usage numbers are facts with a date; the reason behind them is `inferred:` until the recipient says it.

## Person signals

| Signal | How to observe | Verify | Decay | The sentence it earns |
|---|---|---|---|---|
| New in role | profile role start date, announcement post | start date within 90 days | 90 days | "Noticed you took over X in <month>. Usually the first quarter is when Y shows up." |
| Engaged with relevant content | reactions or comments on posts about the problem | post url plus date | 30 days | "Saw your comment on <topic>. Curious whether Z is on your list." |
| Posted about the problem | their own post mentions the pain | post url | 30 days | "You wrote about <pain> last week. Two teams in your situation did A." |
| Warm intro available | mutual connection, investor, partner | the connector confirms | 60 days | "<Connector> suggested I reach out about <topic>." |

## Company signals

| Signal | How to observe | Verify | Decay | The sentence it earns |
|---|---|---|---|---|
| Funding round | press, funding databases, announcement post | announcement url, date | 180 days | "With the new round, teams usually double X. That is when Y breaks." |
| Hiring surge in the relevant function | careers page, job boards | 3 or more open roles in the function | 90 days | "You are hiring three <role>s. That usually means <workload> is outgrowing <tool>." |
| Job-post language | phrases in job descriptions that name a tool, a pain, or an initiative | job url, quoted phrase | 90 days | "Your <role> posting mentions <phrase>. That is the exact situation we handle." |
| Ads running | ad libraries of the major platforms | ad id or screenshot date | 60 days | "You are running ads for <offer>. When that works, <downstream pain> follows." |
| Leadership change | press, profile updates | url, date | 120 days | "Your new <title> joined in <month>. New leaders tend to revisit <process>." |
| Expansion or launch | blog, press, new market page | url, date | 120 days | "Congrats on the <market> launch. The first thing that breaks abroad is usually <pain>." |

## Website signals

| Signal | How to observe | Verify | Decay | The sentence it earns |
|---|---|---|---|---|
| Pricing page | pricing page exists, tiers, self-serve versus contact-sales | page url, hash | 180 days | "You sell <tier> self-serve. Teams doing that usually hit <pain> at <scale>." |
| Case-study page | who they show as customers, what outcome they claim | page url | 180 days | "Your <customer> case study talks about <outcome>. We help with the part before it." |
| Technology on site | scripts, providers, integrations visible in the page source or a detector | detector output, date | 180 days | "You run <tool> on the site. Most teams pairing it with <other> struggle with <gap>." |
| Site search hits | a search for a phrase on their domain returns pages | search url | 180 days | "Your docs mention <phrase> four times. That is usually where <pain> lives." |

## List-shaping playbooks

These do not earn a sentence. They make the other playbooks possible.

- **Company name cleaning.** Strip legal suffixes, marketing taglines, and location suffixes before using a name in copy. Keep the cleaned name in a separate column.
- **First name cleaning.** Strip titles, initials, and honorifics. Reject names that are not names.
- **Social link finding.** Resolve the public profile slug for each contact once and cache it. Opaque profile ids are not stable keys.
- **Lookalikes.** From three to five best customers, extract shared observable traits (size band, category, tool on site, hiring pattern) and search for companies sharing at least three. Record which traits matched per account.
- **Name to colleagues.** When the sourced person is wrong, find the right role at the same domain rather than dropping the account.

## Copy-generation playbooks

- **Specificity.** One observable, dated fact per opener. If the fact is generic enough to fit 1,000 recipients, it is not personalization.
- **Constraint box.** Give the copy step a fixed set of allowed facts per account. Anything outside the box is not used.

## Rules

1. One signal per opener. Two signals read as surveillance.
2. Quote nothing from a person's post verbatim; paraphrase the theme.
3. Decay windows are hard limits. An expired signal is context for the segment, not a why-now.
4. Absence of a signal is recorded, not filled.
5. Own-product signals outrank public signals on relevance. When both exist, the opener uses the own-product one.
6. Own-product data stays in the store. Git gets aggregate rates per signal type, never per-account usage.
