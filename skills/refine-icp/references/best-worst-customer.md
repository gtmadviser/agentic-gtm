# The best/worst-customer trick

Use this when the CRM is thin (fewer than 20 closed deals) or when a team needs a shared picture in under an hour. It produces a WHO plus a TRIGGER, which is the minimum an outbound experiment needs.

## Steps

1. **Pick three best-fit customers.** Fast decision, low support load, expanding usage, would recommend you. Do not pick by deal size alone.
2. **Pick three worst-fit customers.** Slow decision, heavy support, churned or stalled, argued about price, asked for features nobody else wants. Lost deals count if the reason is known.
3. **Describe each on the same eight lines**: company size, geography, industry, what they were using before, who signed, who used it day to day, what happened right before they bought, what they said the product was for.
4. **Write the gap.** In plain language, what separates the two groups? Usually two or three lines. Resist adding more.
5. **Sharpen to WHO + TRIGGER.**
   - WHO: company shape (size band, market, technical precondition) plus the role that decides.
   - TRIGGER: the "why now" event that appeared in the best-fit stories. Typical triggers: a new hire in the deciding role, a funding round, a product launch, a migration, a tool they adopted or dropped, a contract renewal, a compliance deadline, a new office or market.
6. **Label the result.** With three customers per side this is a `hypothesis`, not `supported` evidence. Record it as such in `market/icp.md` with the six customers listed only in the store or in a local note, never in Git.
7. **Test it.** The first experiment audience should be the WHO, sourced on the TRIGGER. `design-gtm-experiment` takes it from here.

## Fictional example

Product: a scheduling tool for outpatient clinics.

| | Best fit | Worst fit |
|---|---|---|
| Size | 3 to 8 practitioners | single practitioner, or hospital department |
| Before | paper calendar or a generic booking widget | hospital-wide system |
| Signed | practice owner | procurement office |
| Used by | front desk, two people | fifteen rotating staff |
| Trigger | second location opened, or a front-desk hire left | annual budget review |
| Said it was for | "stop double bookings" | "integrate with everything" |

Gap: owner-led practices with a front desk of one or two people, buying to fix a concrete failure after a change in staff or locations. Worst fits buy through a committee to satisfy an integration wish.

WHO: owner-led outpatient practices with 3 to 8 practitioners and a front desk, in the home market.
TRIGGER: a new location, or a front-desk hire posted in the last 60 days.

## No customers yet

Borrow. Take a direct competitor and list its most visible public customers (case studies, review sites, logo walls). Apply the same eight lines to the ones that look most and least happy in public sources. Label everything `hypothesis` and cite the sources with dates in `market/`.

## Common mistakes

- Choosing best fit by revenue. The biggest logo is often the worst fit.
- Writing a wish list instead of the gap. If the gap has more than five lines, it is a wish list.
- Skipping the trigger. A WHO without a TRIGGER produces a list, not a campaign.
- Promoting the result to `supported`. It is a well-formed hypothesis. Nothing more until tested.
