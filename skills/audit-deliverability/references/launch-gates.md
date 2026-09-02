# Launch gates for a new market or fleet

A stage model with hard gates. Infrastructure and lead sourcing run in parallel with everything; the launch stages run one market at a time. The longest external pole (any localized asset a third party must provide, such as a local phone line, a local legal review, or a native copy reviewer) is requested on day 0.

## Rule

At most one market in stages D to H at a time. A market may not launch until every gate in stages F and G is checked. A gate is a box a second person can verify, not a feeling.

## Stages

### A. Market decisions (day 0)
- Wave-1 segments: proven winners in the home market that exist in the new market's lead pool.
- Persona: one surname, one to three first-name variants, localized signature.
- Reply-handling owner who reads and answers in the local language.
- Compliance notes for the market. Examples of the questions to answer: does B2B cold email need presumed consent (parts of the EU treat unsolicited B2B email as unfair competition), does the market allow B2B email under legitimate interest with opt-out, does it require a postal address and a working unsubscribe in every message, are there sector exclusions (regulated professions) that must be suppressed. Write the answer into `strategy/decisions.md` before any list is built.
- Sending window and timezone. Confirm the sequencer accepts the timezone string before the build; some accept only a whitelist.
- Request any localized third-party asset today.

### B. Email infrastructure (passive, 3 to 6 weeks)
- Domains, mailboxes, DNS, signatures, redirects, warm-up per `mailbox-fleet.md`.
- Registry rows in the store for every domain and mailbox with market and persona.
- Rotation pools and tags created now, not "later". A fleet without pools sits idle after launch.
- Finalization steps that are easy to forget: signature set and re-read on every mailbox; redirect verified on every domain; warm-up verified active after any export.

### C. Lead pipeline (parallel)
- Source, resolve the company website, find the decision maker, run the email waterfall, verify 100%.
- Selection rule at export: valid executive email first; valid generic company mailbox with a named owner second; otherwise drop.
- Suppress customers, open deals, competitors, and legally excluded sectors.

### D. Copy localization (2 to 5 days)
- Localize the two proven angles from the home market, not the losing ones.
- Native reviewer sign-off recorded in the copy file. Translation is not localization.
- Placeholders for any market-specific asset not yet delivered (`{{LOCAL_NUMBER}}`), never a wrong value.

### E. Campaign build (1 to 2 days)
- Build as a paused draft through `gtm campaign plan` and `gtm campaign apply`.
- Naming `YYMMDD_<market>_<segment>`.
- Sender pool selected by persona and provider group from the registry; each mailbox in exactly one campaign.
- Burned-domain filter, dead-infrastructure filter, bounced-recipient filter, and company-domain dedupe across all active campaigns applied to every list.

### F. Monitoring wiring (hard gate)
- [ ] Persona and campaign routing know the new market.
- [ ] Health check dry run shows the new campaigns under the right persona.
- [ ] Placement test groups include the market's provider groups.
- [ ] Reply-rate rotation includes the new campaigns.
- [ ] Attribution and reporting include the new campaigns.
- [ ] Store rows exist for every campaign with the sequencer's campaign ID.

### G. Pre-launch verification (2 to 3 days before launch)
- [ ] Placement test per provider group: 80% or higher inbox on the primary consumer ESP, no spam-majority group, under 7 days old.
- [ ] Seed sends (5 to 10 per persona) with final copy: rendering, spintax expansion, greeting merge for every lead shape, signature block present.
- [ ] Warm-up re-check: any mailbox under 90 dropped from the build.
- [ ] Signature non-empty and persona-correct on every campaign mailbox, re-read via API.
- [ ] Redirect on every sending domain, re-checked.
- [ ] Bounced and suppressed rows removed after the final list load.

### H. Launch day
1. Test every market-specific asset against the acceptance criteria written in stage A.
2. Replace placeholders in all sequences and signatures; re-read to confirm zero placeholders remain.
3. Re-run the four list filters on the loaded leads.
4. Confirm the placement test under 7 days old passed.
5. Activate with ramp: about 25% of daily cap on day 0, full cap over about 10 days. Activation is a human action outside this skill and outside the runtime.
6. Confirm rotation pools are enrolled the same hour.

### I. Post-launch
- T+1: sends match the ramp plan; bounce under 3%.
- T+3: reply rate against the home-market baseline; complaint signals; localized asset log sanity check.
- T+7: placement re-test; first rotation pass sane; attribution report includes the campaigns; decide wave 1.5.

## Gate summary

| Gate | Passes when |
|---|---|
| Compliance | Market rules written into `strategy/decisions.md` with owner and date |
| Infrastructure | Every mailbox warmed 14+ days, score 90+, signature set, redirect live, pools created |
| List | 100% verified, four filters applied, selection rule followed |
| Copy | Native sign-off recorded; no placeholders at launch |
| Monitoring | Every stage-F box checked by a second person |
| Placement | Passing test per provider group under 7 days old |
| Ramp | Written ramp plan and T+1, T+3, T+7 owners |
