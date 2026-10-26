# Group Decision Memo Format

Save to `{group}/decisions/YYYY-MM-DD-{topic-slug}.md`. Same shape as the leadership memo; the
member sections replace the fixed executive sections.

```markdown
# Decision Memo: {Topic}

**Account**: {Account name}
**Group**: {Group name} (simulation of a working group, not statements by real people)
**Date**: {YYYY-MM-DD}
**Chair**: {member name, or "neutral facilitator"}
**Decision**: {One-sentence summary}
**Decision authority**: {Decided by the group | Recommendation to escalate to {escalates_to}}
**Confidence**: {High / Medium / Low}

## Executive Summary

{2-3 paragraphs}

## Member Perspectives

### {Name} - {Title} ({function lens})
{Summary of their position and key arguments}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL}

{One block per voting member, in roster order. Then, if present:}

### {Name} - {Title} (advisor, no vote)
{Argument and final advice}
**How the decision responds**: {accepted / adopted with changes / not adopted, and why}

### Contrarian - Critical Challenge  /  Moonshot - Bold Vision
{Archetype seats, if in the room}
**Position**: {SUPPORT / OPPOSE / CONDITIONAL}

## Areas of Agreement
## Areas of Disagreement
{Where members diverged; how it was resolved. Note any deference to rank or to the chair.}

## Decision Rationale
{Reasoning, addressing dissent}

## What This Asks of the Teams
{Per function: what changes, who owns it, the capacity or budget needed, what stops. A decision
with no owner and no capacity is not a decision.}

## Escalation
{Only if the decision is a recommendation to escalate: to whom, what to ask for, what to
bring them (numbers, risks, the dissent).}

## Recommended Next Steps
1. {Action, owner (a member), timeline}

## Risk Mitigation
{Key risks and mitigations; the Contrarian's pre-mortem is addressed here if present.}

## Comparison With Prior Run
{Reruns only; omit otherwise.}

## Open Context Gaps
{From `{account}/company/gaps.md` entries raised in this session, or "None".}

## Appendix: Process Metadata
- **Time spent**: {duration}
- **Room**: {members, advisors, archetypes}
- **Full discussion**: `{group}/decisions/YYYY-MM-DD-{topic-slug}-discussion.md`
- **Dissenting opinions**: {who opposed, if any}

## Appendix: Input
```yaml
{full contents of the input file, verbatim}
```
```
