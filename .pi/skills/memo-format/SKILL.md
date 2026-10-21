---
name: memo-format
description: Required format for CEO decision memos. Use when producing the final output.
---

# Decision Memo Format

The final output memo must follow this exact structure. Save the memo to
`{account}/decisions/YYYY-MM-DD-{topic-slug}.md` where topic-slug is a kebab-case
version of the topic (e.g., `2026-04-01-european-market-expansion.md`).

```markdown
# Decision Memo: {Topic}

**Account**: {Account name}
**Date**: {YYYY-MM-DD}
**Decision**: {One-sentence summary of the decision}
**Confidence**: {High / Medium / Low}

## Executive Summary

{2-3 paragraphs summarizing the decision and key reasoning}

## Specialist Perspectives

### CFO - Financial Reality
{Summary of the CFO's position and key arguments}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL}

### CTO - Technical Feasibility
{Summary of the CTO's position and key arguments}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL}

### COO - Operational Reality
{Summary of the COO's position and key arguments}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL}

### {Guest title} (guest advisor — no vote)
{One block per guest in the room; omit if none. Summarise their argument and final advice.}
**How the decision responds**: {accepted / adopted with changes / not adopted, and why}

### Moonshot - Bold Vision
{Summary of Moonshot's position and key arguments}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL}

### Contrarian - Critical Challenge
{Summary of Contrarian's position and key arguments}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL}


## Areas of Agreement

{What did multiple specialists agree on?}

## Areas of Disagreement

{Where did specialists diverge? How was the disagreement resolved?}

## Decision Rationale

{Detailed reasoning for the final decision, addressing dissenting views}

## Recommended Next Steps

1. {Specific action item with owner and timeline}
2. {Specific action item with owner and timeline}
3. ...

## Risk Mitigation

{Key risks and how they will be addressed}

## Comparison With Prior Run

{Only for reruns (`rerun_of` set): how this decision differs from the original, what the guests changed or confirmed, and whether any core member's vote moved. Omit otherwise.}

## Open Context Gaps

{Facts the team needed but did not have, from `{account}/company/gaps.md` entries raised in this session. "None" if none.}

## Appendix: Process Metadata

- **Time spent**: {wall-clock duration}
- **Specialists consulted**: CFO, CTO, COO, Moonshot, Contrarian{, guests}
- **Full discussion**: `{account}/decisions/YYYY-MM-DD-{topic-slug}-discussion.md`
- **Dissenting opinions**: {which specialists opposed, if any}

## Appendix: Input

```yaml
{full contents of the input YAML file, verbatim}
```
```
