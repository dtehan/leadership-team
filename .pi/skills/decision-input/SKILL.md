---
name: decision-input
description: Format for structured decision input topics. Parses and validates decision requests.
---

# Decision Input Format

When receiving a decision request, parse it into this structure:

## Required Fields
- **Topic**: A short title for the decision (under 80 characters)
- **Description**: What specifically needs to be decided (1-3 sentences)
- **Background**: Relevant context, constraints, and prior work (1-3 paragraphs)

## Optional Fields
- **Urgency**: low / medium / high (default: medium)
- **Stakeholders**: Who is affected by this decision

## Parsing

If the user provides a free-form prompt, extract these fields as best you can.
If the user provides structured input (YAML, JSON, or markdown with headers),
parse it directly.

Example structured input:

```yaml
topic: European Market Expansion
description: Should we open a sales office in Berlin and localize our product for the EU market?
background: |
  We have 15% of revenue from EU customers via self-serve.
  Three competitors have established EU presence in the last year.
  Our product needs GDPR compliance work estimated at 3 months.
  Available budget: $2M for first year.
urgency: high
```
