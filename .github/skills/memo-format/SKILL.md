---
name: memo-format
description: Required format for a named team's decision memo. Use when producing an evaluate result for any team and profile-backed leader.
---

# Team Decision Memo Format

Save to `{team}/decisions/YYYY-MM-DD-{topic-slug}.md` with unused output names.
Use the transcript's snapshotted room, never the current edited team definition.
Historical memos are not reformatted or overwritten.

The memo has these sections in order:

```markdown
# Decision Memo: {Topic}

**Account**: {Account name}
**Team**: {Team name} ({team-slug})
**Simulation**: Based on public and supplied context, not statements by real people
**Date**: {YYYY-MM-DD}
**Leader**: {Resolved name and title}
**Decision**: {One-sentence summary}
**Decision authority**: {Team decision | Recommendation to escalate to {authority}}
**Confidence**: {High / Medium / Low}

## Executive Summary
{2-3 paragraphs: trade-off, conclusion, key evidence and limits}

## Participant Perspectives
### {Name} - {Title} 
{One block per person, in snapshotted order: argument and final position}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL / ADVICE}

## Synthetic Perspectives
{Only if present: each archetype's argument and final position; separate from votes}

## Areas of Agreement
## Areas of Disagreement
{Flag dissent and any deference to rank; explain what could tip a close decision}
## Decision Rationale
{Leader's reasoning, response to dissent and advisors, not a majority count}
## What This Asks of the Teams
{Per function: owner, capacity/budget, what changes and what stops}
## Escalation
{Only when needed: to whom, approval requested, evidence and dissent to bring}
## Recommended Next Steps
1. {Action, owner, capacity and timeline}
## Risk Mitigation
{Address the Contrarian pre-mortem if present}
## Comparison With Prior Run
{Reruns only: previous reference, room changes, arguments, vote shifts and decision}
## Open Context Gaps
{Missing facts raised in the run, or None}
## Appendix: Process Metadata
- **Time spent**: {measured wall-clock duration}
- **Cost**: {measured runtime value, or unavailable}
- **Room**: {leader, voters, advisors, archetypes}
- **Full discussion**: {discussion path}
- **Dissenting opinions**: {who opposed, or None}
## Appendix: Input
{Full contents of the saved question verbatim, in a fenced YAML block}
```

Omit optional sections and unused perspective types, not mandatory evidence or
dissent. The leader's own position belongs in the rationale, not the voter tally.
