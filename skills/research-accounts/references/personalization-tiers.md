# Personalization tiers

Personalization variables are ranked by effort to obtain and impact on reply quality, then mapped to columns that actually exist in the store. A variable with no column is a wish, not a variable.

## Tiers

| Tier | Source | Effort | Impact | Examples |
|---|---|---|---|---|
| 0 list-level | the query itself | none | low | industry, size band, country, role family |
| 1 company facts | company website, public page | low | medium | what they do in one line, who they sell to, locations, product names |
| 2 company signals | press, jobs, ads, detectors | medium | high | funding, hiring, job-post phrase, tool on site, expansion |
| 3 person facts | public profile, posts | medium | high | role start date, headline, a recent post theme, tenure |
| 4 deliberately not pursued | internal or private | high | low or negative | org charts, private funding details, guessed technologies, personal life, protected traits |

Tier 4 exists so nobody spends credits on it. Write it down.

## Variable schema

Store on `contacts.attributes` and `accounts.attributes`:

```
core:          first_name_clean, company_name_clean, title_clean, country, language
tier1:         one_liner, sells_to, locations, product_names
tier2:         signal_type, signal_summary, signal_url, signal_date, tool_on_site, hiring_function, hiring_count
tier3:         role_start_date, headline, recent_post_theme, recent_post_date, tenure_months
derived:       segment, angle, pain_line, proof_point, cta_angle
composite:     context_blob (max 3,000 chars)
```

Every tier 2 and tier 3 value carries its url and date in a sibling field. Copy steps read only fields that are non-empty.

## Effort budget

At list scale, fill tier 0 and tier 1 for every account, tier 2 for accounts above the fit threshold, and tier 3 only for accounts scheduled for a personal channel. Do not fill tier 3 for 2,000 accounts to send 2,000 emails; the reply data will not show the difference and the spend will.

## Mapping to copy

| Variable present | Opener type |
|---|---|
| tier 3 recent post or role change | personal observation opener |
| tier 2 signal | company trigger opener |
| tier 1 only | scenario opener for the segment |
| tier 0 only | do not send a "personalized" opener; send the segment's best generic opener |

Follow-ups use tier 0 and tier 1 only. Repeating a personal fact in a follow-up reads as automation.

## Quality gate

Before variables go to `write-outreach`:

- every variable that will be rendered is non-empty for 100% of the rows in the pool, or the copy carries a fallback,
- no tier 2 or 3 value is older than its decay window,
- cleaned names pass a sanity check (no company names in `first_name_clean`, no legal suffixes in `company_name_clean`),
- a random sample of 20 rows is read by a human.
