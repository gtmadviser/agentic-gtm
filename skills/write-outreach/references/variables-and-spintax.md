# Variables and spintax

Personalisation is only as good as the columns you actually have. Map variables to existing store columns, check fill rates on the exact pool, and never ship a variable that can be empty without a fallback.

## Tiers by effort and impact

### Tier 1: available now, no enrichment

| Variable | Typical source | Why it works | Example |
|---|---|---|---|
| city or region | company record | local proximity, credible peer proof | "three shops here in {{city}} run it this way" |
| trade or industry | company record | basis of every segment | "with roofers the pattern is almost always the same" |
| public rating | maps or review listing | the ego lever; real, public, flattering | "{{rating}} stars, you are clearly doing something right" |
| review count | maps or review listing | enables a number the reader can check | "at {{reviewCount}} reviews, a dozen people a day call you" |
| phone number | public listing | enables the number-nudge follow-up and a real test call | "is {{phone}} the right number?" |
| company name in running text | everywhere | minimum relevance | |
| website domain | company record | prerequisite for anything website-based | |

### Tier 2: one query or a simple scrape

| Variable | Source | Why it is strong | Example |
|---|---|---|---|
| opening hours | maps raw data | the best hook available for service businesses; turns "outside your hours" into an exact time | "after 17:00 and on weekends, what happens to calls?" |
| closed day | opening hours | very specific, reads researched | "you are closed Mondays. Who takes bookings?" |
| review quote | review text | verbatim, maximum credibility, cannot be argued with | "one review says 'hard to reach by phone'. Familiar?" |
| no contact form or callback option | homepage HTML | verifiable evidence instead of a claim | "your site has only the phone number, no form" |
| booking or reservation tool present | homepage HTML | shows digital maturity; "you solved X, not yet Y" | "bookings work online, the phone still runs through reception" |
| employee count | registry or enrichment | scales the pain plausibly | "with {{employees}} people nobody is only on the phone" |
| founding year | registry | continuity and ego angle | "since {{foundedYear}}, that does not happen with missed calls" |
| owner or managing director name | registry or enrichment | address and authority | |
| open roles, especially reception, admin, sales | careers page, job boards | highest intent signal there is: they are hiring to solve your problem | "you are hiring a receptionist. May I show an alternative?" |
| season trigger | industry plus date, pure logic | free, real urgency | tyres in October, heating in September, hospitality in December, tax deadlines |
| mobile numbers and roles from replies | reply signature parsing | for multichannel follow-up | |

### Tier 3: rich vertical data

E-commerce and software listings often carry 100 plus columns: product count, average basket, traffic estimate, tech stack, app spend, last platform change, social reach, returns page present. Use them for a segment hook, a loss calculation, or a timing trigger ("migrated last month").

### Tier 4: deliberately not pursued for SMB

Funding rounds, investors, university, "people also viewed", org charts, direct reports, LinkedIn post summaries, traffic estimates for local businesses, review sites with thin regional coverage, paid-search keywords for small shops. Effort and benefit do not match. Use them for enterprise or partner campaigns only, and only when verified.

## The fill-rate rule

Before every campaign build, count fill rates on the exact pool you will load, not on the whole table.

```sql
select count(*) as total,
       count(rating)       as has_rating,
       count(review_count) as has_reviews,
       count(phone)        as has_phone,
       count(city)         as has_city
from accounts
where country_code = 'DE' and industry = '<segment>';
```

Rule of thumb:
- below 80 percent fill: do not use the variable in step 1, or split the pool by fill and run two variants
- below 100 percent fill: define a fallback sentence per variable in the copy file
- a variable that renders empty is worse than no personalisation. "4.8 stars as a in ." ends the conversation.

Note the fill rate per variable under the copy file header so `stage-campaign` can check it again on the final list.

## Stacking

One variable reads like a mail merge. Two or three in one sentence read like research.

- Weak: "I saw you are a roofer in Bremen."
- Stacked (trade plus city plus rating plus time): "4.8 stars as a roofer in Bremen, and still between 7 and 9 nobody picks up, I would guess."

Rules: 2-3 variables in one sentence, never as a list. Every variable that can be empty has a fallback.

## Naming

Use the provider's native variable syntax and camelCase names that match store columns: `{{firstName}}`, `{{lastName}}`, `{{companyName}}`, `{{city}}`, `{{rating}}`, `{{reviewCount}}`, `{{phone}}`, `{{accountSignature}}`. Define the mapping once in the copy file. Never invent a variable the loader does not populate.

Formal address needs a salutation column (`{{salutation}}` plus `{{lastName}}`). If the pool lacks it, you cannot run a formal campaign on that pool. Fix the data, do not guess the gender from a first name.

## Spintax

Providers vary text per recipient with spintax. Use it at the sentence level, 2-3 options, all carrying the same meaning.

Instantly-style: `{{RANDOM | Quick one. | Short question. | Two lines, then I leave you alone. }}`
Fallback syntax (lemlist-style): `{{city|your area}}`. No spaces around the pipe in fallback syntax.

Rules:
- 2-3 options, not 27. Sentence-level permutations produce stitched copy and no learning.
- Spintax is not a variant. A variant has a hypothesis; spintax only reduces duplication for spam filters.
- Check the rendered preview for every option before staging.
