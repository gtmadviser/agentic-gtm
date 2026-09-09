# LinkedIn outreach handoff

The minimum pack contains reviewed targets, their source posts and routing
evidence, exact sender identity, territory, language, approved copy, relationship
state, provider, destination campaign, schedule/timezone and capacity. Store
person-level content under the local run; only aggregate outcomes belong in Git.

Copy should reference the actual subject or comment naturally. Never say the
person praised the product just because they reacted. Avoid assumed pain,
invented familiarity, fabricated quotations, or implying that the sender wrote
someone else's post. A post reaction is neither consent nor confirmed intent.

Example structure, with fictional placeholders:

- Invitation: “Hi {{first_name}}, your comment on {{topic}} caught my eye.
  I work on {{relevant_area}} too. Open to connecting?” Use only for a commenter
  whose actual comment supports the opener; create a different reactor variant.
- After acceptance: one supported observation, one relevant reason to talk and
  a short question. Use the sender's real voice and this company's positioning.
- Existing connection: skip the invite. A reply stops scheduled follow-up;
  rejection, opt-out or complaint suppresses the person.

Do not apply cold-email word counts to LinkedIn invites. Check the provider's
current character limits, account restrictions and daily capacity. If connection
state is unknown, resolve it or leave the row on hold. A delay alone does not
implement “only after acceptance.” Verify that the chosen provider supports that
condition before treating a sequence as ready.

For API staging, use only supported operations in the configured sequencer.
`gtm campaign plan` does not upload audiences or guarantee connection-acceptance
conditions. The Harvest collector never sends messages. Where the adapter lacks
the needed behavior, export a local CSV plus exact manual setup instructions.
Do not substitute email for LinkedIn without a separate decision and verified
addresses. Do not use Harvest interaction endpoints as an unreviewed shortcut.

Verify a paused destination by reading it back: selected row count, no duplicate
profiles, sender, step types, exact copy, schedule and stop conditions. Record
provider IDs locally. Stage only the reviewed selection, not every row with a
high score. Launch requires the existing campaign approval process.

Count invitations, accepted connections, people messaged, human replies,
positive replies, meetings and opportunities separately. Report acceptance per
invite and replies per person messaged. Do not pool LinkedIn invitation counts
with email sends. Record unknown outcomes as unknown, not zero. Attribution
links outcomes to the person, campaign, cohort and original engagement evidence.

## Founder/company/employee motion

Keep the source kind and exact post per recipient. A person found through an
employee repost did not necessarily engage a founder-authored original. Multiple
voices or comments can help prioritize review, but never change mandatory fit.

Separate owned-account handoffs from the net-new/unassigned sequence. An owner
handoff contains the person, company, post, engagement and supported reason to
follow up. Create a new campaign within the accepted asset scope for the net-new
motion; never edit a rep's existing campaign as part of this playbook.

If the company's accepted experiment uses a bare invitation, send no note in
that step and put the accurate warm anchor in the message after acceptance.
Use a different branch for an existing connection. Invitation notes versus bare
invites, delays, bumps, soft closes and withdrawals are experiment choices, not
universal defaults. Do not automate withdrawals without explicit scope and
verified provider support. A rep-owned account never becomes unowned merely
because a new contact was discovered there.

A staged pack should record `source_kind`, `post_url`, `company_fit`, `persona_fit`,
`route`, `account_owner`, `contact_owner`, `sender`, `territory`, `relationship_state`,
`invite_variant`, exact message text, accepted delays, and the stop conditions.
Preserve the initial reviewed sample and recipe/ICP revision beside the pack.
