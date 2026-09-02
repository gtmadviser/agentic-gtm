# Positioning hypothesis template

Positioning is a bet on who you win with and why. This skill writes each bet so it can lose. A positioning line becomes a decision only when `strategy/decisions.md` records an owner and a date.

## Format

```markdown
## Option <n>: <short name>

Status: proposed | testing | adopted (D-nnn) | rejected (date)

**Statement.** For <WHO: segment, size band, role> facing <TRIGGER or situation>, <product> is the <category> that <one outcome>, because <structural reason>.

**Wins with.** The buyer and situation where this beats the alternatives in the map. Name the bucket it competes against most (direct, substitute, workaround, do nothing).

**Evidence for.**
- E-nnn or S-nnn, date, one line each.

**Disconfirming evidence to seek.**
- What we would have to see to drop this option (for example: the segment's loss reasons cite breadth; replies from this segment ask for integrations we lack).

**Cheapest test.** One experiment or a set of customer conversations, with the metric and the decision rule, handed to `design-gtm-experiment`.

**Copy guidance if adopted.** Angle, proof, forbidden framings.
```

## Rules

1. At most three options per review. More options means the question is not defined.
2. The statement names one outcome. Two outcomes is two options.
3. The structural reason must be something the alternatives cannot copy in a quarter.
4. Evidence lines cite IDs and dates. A line without an ID is a belief.
5. Disconfirming evidence is mandatory. An option nobody can disprove is a slogan.
6. Never position as "the cheaper X". If price is the only difference, the option is rejected.
7. The test goes through `design-gtm-experiment`; this file does not launch anything.

## Fictional example

```markdown
## Option 1: Same-day handoffs for owner-led teams

Status: proposed

**Statement.** For engineering leads at owner-led companies with 11 to 50 engineers who just added a second on-call rotation, Northstar Relay is the coordination tool that removes missed handoffs in a day, because the team sets it up itself without an admin project.

**Wins with.** Teams comparing us with a spreadsheet workaround or with doing nothing after a missed page. Rarely against Harbor Sync, whose buyer is a platform organisation.

**Evidence for.**
- E-003, 2026-08-22: won deals concentrate in the 11 to 50 band, supported.
- S-014, 2026-09-01: dated reviews of the main alternative cite weeks of rollout.

**Disconfirming evidence to seek.**
- Replies from this segment asking first about integrations.
- Loss reasons in the band citing "too small for us to matter".

**Cheapest test.** 200 delivered emails to the segment with the second-rotation trigger, decision rule: continue if positive replies per 100 delivered are at least 3; handed to design-gtm-experiment.

**Copy guidance if adopted.** Angle: the missed handoff after a new rotation. Proof: setup time, small-team references once approved. Forbidden: naming the alternative unprompted, price comparisons.
```

All names and figures invented.
