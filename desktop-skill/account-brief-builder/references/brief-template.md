# Account brief template

Save the finished brief as a file (for example `{customer}-account-brief-{YYYY-MM-DD}.md`; keep only the newest in the Project) and add it to the
customer's Claude Project knowledge. Keep it a few pages. Facts carry a source and date;
interpretation is labelled *(inferred)*.

```markdown
# Account brief: {Customer}
**Legal entity / ticker**: ...   **As of**: {date}   **Confidence**: low / medium / high

## Change log
Newest first, last 10 entries. Each entry: date, what changed by section, personas that moved,
gaps filled or opened. First entry on a new brief: "{date}: initial brief".

## Snapshot
What they do, size, segments, geography, how they make money.

## Financial picture
Revenue and margin trends, cost pressure, capital allocation, stated investment commitments,
guidance and what analysts push on. Numbers in a table with the period and source.

## Technology in place
Cloud, data platforms, analytics and AI tools, ERP and core systems, security posture.
Status per item: in place / evaluating / rumoured / retired, with evidence quality.
Where Teradata is or is not present today, if the user knows.

## Technology under evaluation
Announced pilots, RFPs, partnerships, stated AI and data strategy.

## Strategy and market
Stated priorities and targets, competitors, regulatory pressure, recent events
(leadership changes, M&A, outages, litigation).

## The leaders (public-source personas)
For each of CEO, CFO, CTO, COO:
- **Name / title / tenure** (or "unknown")
- **Stated priorities** in their own words, with dates
- **How they communicate and handle pushback**
- **Decision tendencies**: data-first or instinct, risk appetite, build/buy/partner leaning, what they have backed or killed
- **Known positions**: AI, cloud, cost, vendors, M&A
If a seat is vacant or the person is unknown, say so and describe the role generically.

## Account intelligence (from the account executive)
Relationships, politics, budget cycle, incumbent vendors, what has been heard in meetings,
past Teradata history. Mark as first-hand or second-hand.

## Open context gaps
- [open] {fact the twins need and lack}
```
