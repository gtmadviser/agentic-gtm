# Metrics CSV import

`gtm metrics import --file <csv>` loads counts into the `campaign_metrics` table. Use it for any provider without an analytics adapter, for LinkedIn or call steps, and for manual channels such as events. The file stays in `.gtm/` or the store; it is never committed.

## Columns

| Column | Type | Required | Notes |
|---|---|---|---|
| `provider` | text | yes | Lowercase provider slug, or `manual` |
| `campaign` | text | yes | Campaign name or provider ID; stable across imports |
| `variant` | text | no | Variant label; leave empty for campaign totals |
| `window_start` | date | yes | ISO `YYYY-MM-DD`, inclusive |
| `window_end` | date | yes | ISO `YYYY-MM-DD`, inclusive |
| `sent` | integer | yes | Messages sent, including follow-up steps |
| `delivered` | integer | no | Defaults to `sent` minus `bounced` |
| `bounced` | integer | yes | Hard plus soft bounces |
| `replied` | integer | yes | Human replies; exclude out-of-office and automatic replies |
| `positive_replies` | integer | yes | Sum of interested, soft, and referral labels |
| `meetings` | integer | yes | Meetings booked and attributed to the campaign |
| `opportunities` | integer | yes | CRM opportunities attributed inside the window |

Integers only, no thousands separators, no percentages. Empty cells are treated as missing, not as zero, except `variant`.

## Example

```csv
provider,campaign,variant,window_start,window_end,sent,delivered,bounced,replied,positive_replies,meetings,opportunities
lemlist,2026-07 Northstar Relay engineering leads,A cost framing,2026-07-07,2026-07-27,1240,1216,24,39,14,5,2
lemlist,2026-07 Northstar Relay engineering leads,B scenario opener,2026-07-07,2026-07-27,1198,1177,21,41,9,2,1
manual,2026-07 Northstar Relay LinkedIn follow-up,,2026-07-07,2026-07-27,310,310,0,58,31,9,3
```

## Building the file from a provider export

1. Export the campaign or step report from the provider UI for the exact window of the experiment.
2. Map the provider's column names to the columns above. Typical mappings: "emails sent" to `sent`, "bounced" to `bounced`, "replies" minus "auto replies" to `replied`, "interested" plus "referral" to `positive_replies`.
3. If the provider reports replies as one blended number, classify the replies first and count positives yourself.
4. If the provider reports per lead rather than per send, keep the per-send numbers for `sent` and derive nothing from unique leads.
5. Run `gtm --json metrics import --file <path>`. The command rejects unknown columns, non-ISO dates, and non-integer counts.
6. Re-importing the same provider, campaign, variant, and window replaces the earlier row. Use that to correct counts; do not add a second row for the same window.

## LinkedIn and calls

- `sent` for LinkedIn means messages or invitations sent, not profile views.
- Keep bare invitations and messaged invitations as separate variants so their acceptance and reply rates can be compared.
- For calls, `sent` is dials, `replied` is conversations, `positive_replies` is conversations with stated interest.

## Common mistakes

- Reporting the window as "last 30 days" instead of the experiment's window.
- Copying the provider's reply rate instead of the reply count.
- Counting out-of-office replies as replies.
- Mixing unique-lead denominators with per-send denominators in one file.
- Committing the CSV. It belongs in `.gtm/` or the store.
