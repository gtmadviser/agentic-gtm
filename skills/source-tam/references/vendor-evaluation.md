# Evaluating a data vendor

Buy data the way you would buy any input: measure it on a sample before signing, and price it per usable contact, not per record.

## Criteria

| Criterion | Weight | What to measure |
|---|---|---|
| Contact availability | 3 | share of records with a named decision maker and an email |
| Verification pass rate | 3 | share of vendor emails that an independent verifier marks `valid` |
| Segmentation fields | 2 | employee count, revenue band, industry code present and populated |
| Freshness | 2 | update cadence, last-updated field per record |
| Legal basis | 3 | does the licence permit marketing use, per record, in writing |
| Export and retention | 2 | bulk export allowed, retention period, re-pull charges |
| Coverage of your slice | 2 | records in your ICP after filters, not total database size |
| Cost per usable contact | 3 | price divided by (contact availability × verification pass rate) |
| Concentration risk | 1 | would this vendor carry more than half of your enrichment spend |

Score 1 to 5 per criterion, multiply by weight, compare totals. A vendor with no written marketing licence scores zero on legal basis regardless of the rest.

## The pilot

Before any subscription: a fixed small budget, a sample of 1,000 to 3,000 records from your slice, an independent verifier on every email returned, and a written result with match rate, pass rate, and cost per usable contact. Do not build the integration in full until the pilot passes the thresholds you set beforehand.

## Questions to ask

1. Is there a bulk export or is it API only? What are the rate limits?
2. Price per record, per search, or per hit? What is charged on a miss?
3. Are emails included, and are they verified? When?
4. Which financial and size fields are present, and for what share of records?
5. What is the update cadence and is there a per-record timestamp?
6. What does the licence say about marketing use and about retention after cancellation?
7. What share of your database falls into my filters? Show the count before I buy.

## Decision thresholds

Set them before the quotes arrive and write them in `market/tam.md`. Example pattern: below a price floor with comparable quality, consider; between floor and ceiling, the vendor with included enrichment wins; above the ceiling, decline unless the pilot shows a pass rate no other source reaches.
