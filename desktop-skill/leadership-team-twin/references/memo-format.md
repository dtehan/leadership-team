# Decision memo format

Use exactly this structure. Write it in the chat; offer it as a downloadable document too.

```markdown
# Decision Memo: {Topic}

**Customer**: {Customer name}
**Date**: {YYYY-MM-DD}
**Decision**: {One-sentence summary}
**Confidence**: {High / Medium / Low}

> Simulation built from public and supplied information. Not what the real executives said
> or will do.

## Executive Summary
{2-3 paragraphs: the decision and the key reasoning}

## Specialist Perspectives
### CFO - Financial Reality
{position and key arguments}
**Position**: SUPPORT / OPPOSE / CONDITIONAL
### CTO - Technical Feasibility
### COO - Operational Reality
### {Guest title} (guest advisor, no vote)   <- one block per guest; omit if none
**How the decision responds**: {accepted / adopted with changes / not adopted, and why}
### Moonshot - Bold Vision
### Contrarian - Critical Challenge

## Areas of Agreement
## Areas of Disagreement
{where they diverged and how it was resolved}

## Decision Rationale
{detailed reasoning, addressing dissent}

## Recommended Next Steps
1. {specific action, owner, timeline}

## Risk Mitigation

## Open Context Gaps
{facts the team needed and did not have, or "None"}

## Appendix: Full discussion
See the discussion file `{customer}-discussion-{YYYY-MM-DD}-{topic}.md` (the verbatim conversation).

## Appendix: Input
{the question, background, constraints and stakeholders as given}
```

After the memo, always add **Account-executive takeaways**: three objections to prepare for,
likely champion and likely blocker, how to reframe the pitch, first next step.
