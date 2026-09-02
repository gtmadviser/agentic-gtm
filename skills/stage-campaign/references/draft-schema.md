# CampaignDraft schema

The JSON that `gtm campaign plan --draft <file>` reads. The CLI validates it; a shape error stops at plan time, never at the provider. Run `gtm --json campaign plan` early to catch mistakes.

## Fields

| Field | Type | Rule |
|---|---|---|
| `id` | UUID, optional | generated if absent; keep it once generated so re-plans reference the same draft |
| `name` | string | `YYMMDD_<market>_<segment>_<angle>` |
| `provider` | `lemlist` or `instantly` | must match `providers.sequencer` in `gtm.yaml` |
| `audience_query` | object | the query that built the pool; recipients are never in the draft |
| `steps` | array | see below; copied from the copy file byte for byte |
| `schedule` | object | `timezone`, `from`, `to`, `days` |
| `suppression_lists` | array of strings | names of the lists applied, for the record |
| `status` | `"paused"` | anything else fails validation |

### Step

| Field | Type | Rule |
|---|---|---|
| `day` | integer | offset from the previous step; 0 for the first |
| `channel` | `email`, `linkedin_invite`, `linkedin_message` | Instantly supports `email` only |
| `subject` | string | email only; empty string for a same-thread follow-up |
| `body` | string | the control variant |
| `variants` | array of `{subject, body}` | optional; 3-4 total including the control |

The adapter maps steps to the provider's format. Do not write provider-specific fields into the draft.

## Example: Instantly, email, two steps, three variants

Fictional company Harbor Metrics writing to online bike shops in Germany.

```json
{
  "name": "260915_DE_ecom_late-delivery",
  "provider": "instantly",
  "audience_query": {
    "country_code": "DE",
    "industry": "ecommerce_sports",
    "employee_count_max": 50,
    "has_review_text": true,
    "experiment": "exp-2026-09-late-delivery"
  },
  "steps": [
    {
      "day": 0,
      "channel": "email",
      "subject": "{{firstName}}, Bewertung von März",
      "body": "{{firstName}}, in einer Ihrer Bewertungen von März steht: \"zehn Tage zu spät, und niemand hat Bescheid gesagt\".\n\nWir haben ein Programm gebaut, das eine hängende Sendung am selben Tag erkennt und den Kunden informiert, bevor er Ihnen schreibt.\n\nSoll ich Ihnen die Liste der verspäteten Sendungen vom letzten Monat schicken? Antworten Sie mit \"Liste\". Oder mit \"nein\", dann höre ich auf.\n\n{{accountSignature}}",
      "variants": [
        {
          "subject": "{{firstName}}, Samstagsbestellungen",
          "body": "{{firstName}}, Samstag bestellt, Montag verschickt, Donnerstag schreibt der Kunde \"wo bleibt mein Rad\".\n\nWir haben ein Programm gebaut, das eine hängende Sendung am selben Tag erkennt und den Kunden informiert, bevor er fragt.\n\nSoll ich Ihnen die Liste vom letzten Monat schicken? Antworten Sie mit \"Liste\". Oder mit \"nein\", dann höre ich auf.\n\n{{accountSignature}}"
        },
        {
          "subject": "{{firstName}}, zehn Tage",
          "body": "{{firstName}}, \"zehn Tage zu spät\" steht in einer Ihrer Bewertungen. Wir erkennen hängende Sendungen am Tag, an dem sie hängen. Liste vom letzten Monat? Antworten Sie mit \"Liste\".\n\n{{accountSignature}}"
        }
      ]
    },
    {
      "day": 3,
      "channel": "email",
      "subject": "",
      "body": "Falsche Person, oder falsches Problem? Wenn sich bei {{companyName}} jemand anderes um den Versand kümmert, reicht mir ein Name.\n\n{{accountSignature}}"
    }
  ],
  "schedule": {
    "timezone": "Europe/Berlin",
    "from": "08:00",
    "to": "17:00",
    "days": ["mon", "tue", "wed", "thu", "fri"]
  },
  "suppression_lists": ["unsubscribes", "customers", "open-deals", "competitors", "legal-exclusions"],
  "status": "paused"
}
```

Notes:
- Variant bodies are the copy file's variants A, B, C. The `body` at step level is the control.
- Step 2 has an empty subject: same-thread reply.
- The demo phone number, if the CTA is a call, goes in the CTA line with its country code and is a different number from the one in the signature.

## Example: lemlist, LinkedIn-first with an email leg

Fictional company Harbor Metrics writing to heads of operations at UK online retailers.

```json
{
  "name": "260915_UK_ecom_linkedin-first",
  "provider": "lemlist",
  "audience_query": {
    "country_code": "GB",
    "industry": "ecommerce",
    "title_regex": "(head|director|vp) of (operations|fulfilment|logistics)",
    "experiment": "exp-2026-09-li-first"
  },
  "steps": [
    { "day": 0, "channel": "linkedin_invite", "subject": "", "body": "" },
    {
      "day": 0,
      "channel": "linkedin_message",
      "subject": "",
      "body": "Thanks for connecting, {{firstName}}. One of your March reviews mentions a parcel that arrived ten days late with no update. We flag stuck parcels the day they stall. Worth a look?"
    },
    {
      "day": 2,
      "channel": "linkedin_message",
      "subject": "",
      "body": "Short version: a list of last month's late parcels for {{companyName}}, no login needed. Want it?"
    },
    {
      "day": 3,
      "channel": "linkedin_message",
      "subject": "",
      "body": "Maybe I have the wrong person. Who owns delivery at {{companyName}}?"
    },
    {
      "day": 7,
      "channel": "email",
      "subject": "{{firstName}}, march review",
      "body": "{{firstName}}, one of your March reviews says the parcel arrived \"ten days late and nobody told me\".\n\nWe built a tool that spots a parcel the day it stalls and messages the customer before they write to you.\n\nWant the list of last month's late ones? Reply \"list\". Reply \"no\" and I stop.\n\n{{accountSignature}}"
    }
  ],
  "schedule": {
    "timezone": "Europe/London",
    "from": "08:00",
    "to": "17:00",
    "days": ["mon", "tue", "wed", "thu", "fri"]
  },
  "suppression_lists": ["unsubscribes", "customers", "open-deals", "competitors"],
  "status": "paused"
}
```

Notes:
- The invite carries no note. The messaged invite is a challenger variant, staged as a separate campaign arm with senders split evenly.
- The email leg runs only for contacts who did not accept, and only with verified addresses. The adapter does not add contacts; the launching human loads the filtered pool in the UI.
- lemlist stores sequence steps separately from the campaign; the adapter creates the paused campaign, then adds steps, then re-verifies paused. Senders are assigned in the UI.

## What the plan looks like

```json
{
  "id": "…",
  "operation": "campaign.create_paused",
  "provider": "instantly",
  "targets": ["<draft id>"],
  "payload_summary": "Create one paused campaign named '260915_DE_ecom_late-delivery'",
  "idempotency_key": "<sha256>",
  "hash": "<sha256>",
  "expires_at": "<24 hours after creation>",
  "status": "pending"
}
```

Present `payload_summary`, `hash`, and `expires_at` to the operator. Apply with `gtm --json campaign apply --plan <id>` after `--dry-run` passed.
