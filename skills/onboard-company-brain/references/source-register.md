# Source register

`context/sources.md` records where every fact in the workspace came from. It holds pointers and authority, never the content. It is what makes "the latest stakeholder decision wins" checkable.

## Format

```markdown
# Sources

| ID | Type | Title or description | Date | Authoritative for | Location | Notes |
|---|---|---|---|---|---|---|
| S-001 | interview | Founder interview, product and precondition | 2026-08-20 | product, technical precondition | meetings/2026-08-20-founder-interview.md | redacted notes |
| S-002 | document | Strategy memo v3 | 2026-07-30 | declared ICP, positioning | shared drive (not in Git) | superseded on targeting by D-001 |
| S-003 | report | Pipeline review | 2026-08-22 | closed-deal patterns | reports/pipeline-2026-08-22.md | coverage limits inside |
| S-004 | decision | Growth sync | 2026-08-22 | first experiment audience | strategy/decisions.md D-001 | |
```

Types: interview, document, report, dashboard, decision, public source, experiment.

## Rules

1. Every fact in `context/company.md` and every evidence row in `market/icp.md` cites a source ID.
2. The register stores the location of a source, not its content. Confidential documents stay outside Git; the row says where they are.
3. `Authoritative for` names the topics on which this source outranks older sources. When two sources claim the same topic, the newer date wins and the older row gets a note.
4. Public sources carry the URL and the observed date. Web pages change; the date is part of the citation.
5. Transcripts are never committed. A redacted note in `meetings/` is the citable artifact; the transcript location goes in `Notes` as "local only".
6. When a source is superseded, keep the row and add `superseded by S-nnn on date` in `Notes`.

## Reading order for a new session

1. `OPERATING-CONTRACT.md`
2. `context/sources.md` (to know what is authoritative)
3. `context/company.md`
4. `strategy/decisions.md`
5. `market/icp.md`

Read the register second, before the brief, so that every statement in the brief can be traced while reading.

## What is not a source

- A number remembered from a call without notes. Ask for the note or mark `[unknown]`.
- A competitor's website claim about the market. It is a claim; log it in `market/` with its date.
- A deck older than the latest decision on the same topic. Keep it as history, not authority.
