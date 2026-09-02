# Campaign structure

Defaults that have held across markets and segments. Override only with a measured result recorded in `strategy/decisions.md`.

## Steps

| Sequence type | Steps | Why |
|---|---|---|
| Direct SMB, email | 2 | step 2 adds a few opportunities, step 3 adds none we have measured |
| Mid-market, email-led | 3, ceiling 4 | if three emails across 7-10 days did not land, the next five will not |
| Small TAM, partners, associations | longer is acceptable | the pool is the constraint, not the inbox |
| LinkedIn-first, multichannel | up to 7 touches | invite, message, bump, wrong-person check, withdraw, re-invite, email leg |

"Steps" in a request often means variants. Ask.

## Variants

- 3-4 variants per step, maximum.
- 500 sends per variant is the floor for reading a result. Pool ÷ variants below 500: either cut variants or declare the campaign directional and do not draw conclusions from it.
- Each variant has a hypothesis in the copy file. `stage-campaign` copies the variant bodies verbatim.
- Mix types: one ultra-short, one scenario, one proof-plus-CTA.

## Gaps

| Gap | Default |
|---|---|
| step 1 → step 2 | 3 days |
| step 2 → step 3 | 3-4 days |
| LinkedIn invite → withdraw if not accepted | 7 days |
| LinkedIn re-invite after expiry | about 27 days, and only within 6 weeks of an event anchor |
| re-approach after a full sequence | 60 days minimum since the last touch, non-repliers only, new angle |

## Sizing

- Per-mailbox daily cap: 20-30 after warm-up. Start at 20.
- Mailboxes needed = daily target ÷ per-mailbox cap. 1,000 sends per day at 20 per mailbox needs 50 healthy mailboxes.
- Mailboxes per domain: 2 maximum. Domains needed = mailboxes ÷ 2.
- Warm-up before the first real send: 14 days minimum, 21 days better. Warm-up must be verified as running through the API, not assumed from the dashboard.
- Ramp: start at about 25 percent of the cap and reach full cap over about 10 days.
- Never send cold email from the main company domain. Sending domains are lookalike domains that redirect to the main site.

## Senders

- Dedicated senders per campaign. One mailbox lives in exactly one campaign at a time.
- A/B campaigns: split senders evenly across the arms, within one mailbox of each other. Otherwise you measure sender health, not copy.
- Rotate senders out on the same day when: warm-up score drops under 90, bounce on that sender exceeds 5 percent, or reply rate is zero after 100 sends while peers reply at the pool baseline.
- Sender identity per market: local name, local number in the signature, local domain.

## Schedule

- Send in the recipient's timezone.
- Working days only. Weekends have produced near-zero conversion across our sets.
- Mid-week afternoons have shown the highest reply rate and the lowest conversion to opportunity in our sets; treat day-of-week and hour as a test variable, not settled knowledge.
- Follow-up in the same thread with an empty subject.

## Naming

`YYMMDD_<market>_<segment>_<angle>`, for example `260915_DE_ecom_late-delivery`. The date prefix lets the 60-day filter read launch dates from names when a log is missing. Suffix `_A` and `_B` for split arms; `_NoFollowup` for a step-count test.

## Tags

Tag senders with country and provider (`country:de`, `provider:<name>`) at import. Tag campaigns with the experiment ID. Rotation and reporting scripts key off tags, not names.

## What not to build

- A campaign with more than 4 variants "to learn faster". It learns slower.
- A reminder-style retarget ("did you see this"). Replies, no opportunities.
- A shared sender pool across campaigns. You lose attribution of damage.
- A campaign whose pool failed a filter "just this once".
