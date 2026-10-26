---
name: record-group-outcome
description: Close the learning loop for a working group. After the real group decides (or the outcome is known), compare it with what the member twins predicted, record per-member calibration, and feed corrections back into their dossiers and memory. Use when the user reports what actually happened on a past group decision.
---

# Record Group Outcome

> **Account scope:** run the **account-scope** skill first. One customer per session; `{account}` = `accounts/{slug}`.

Same loop as **record-outcome**, for a group: `{group}` = `{account}/groups/{group-slug}`. The
leadership skill is left untouched; follow these paths instead.

## Inputs
Ask, for a decision in `{group}/decisions/*-transcript.json` (let the user pick if unclear):
1. What actually happened (the real decision or outcome so far).
2. Who said what, if known (which managers pushed for or against, and why). "Unknown" is fine.
3. Source and confidence: first-hand, second-hand, or public inference.
4. Anything that surprised them, especially **who actually decided**: the group, or someone above it.

## Procedure
1. Read the transcript and memo. Extract the chair's call, each member's opening stance, final
   position and reasoning, and the memo's decision authority (decided vs escalate).
2. For **each member** (and archetype seat), compare predicted vs actual: `matched`, `partial`,
   `missed`, `unknown`. One sentence on why. Also assess the **group-level** questions:
   was the scope right (did the real decision land at the level the twin said), and did the
   real group defer to a senior voice the twin did not expect?
3. Write `{group}/decisions/YYYY-MM-DD-{slug}-outcome.md`:
   ```markdown
   # Outcome: {topic}
   **Recorded**: {date} · **Evidence**: {first-hand | second-hand | public} · **Decision date**: {…}
   ## What actually happened
   ## Twin vs. reality
   | Member | Twin predicted | Reality | Verdict | Why the gap |
   ## Group dynamics (scope, deference, who really decided)
   ## Lessons
   ## Context that would have changed the answer
   ```
4. **Calibration**: for each member with a verdict other than `unknown`, append to
   `{account}/company/profiles/{member-slug}/calibration.md` (create with front-matter
   `summary: Where past simulations diverged from the real person`, `tags: [calibration]`,
   `load: always`, `roles: [{member-slug}]`):
   ```
   ### {YYYY-MM-DD} · {topic} · {matched|partial|missed}
   {2-3 lines: what the real person did/said, what the twin predicted, the adjustment}
   ```
   Keep it to about 15 entries; merge older ones into a "Standing adjustments" list.
   A member in several groups shares one dossier: note the group in the entry heading.
   Group-level lessons (deference patterns, scope) go in the chair's memory instead.
5. **Chair memory**: append to the chair's memory (`{group}/memories/chair.md`, or the member
   chair's file) under `## Peer Patterns` any change in how reliable each twin was.
   Do not edit members' own memory files.
6. Add any `[open]` gaps to `{account}/company/gaps.md` and offer **company-research**.
7. Run `python3 scripts/build_index.py {slug}`.
8. Summarise: hit rate, the biggest miss and the fix, what to look at next time.

## Rules
- Never rewrite history: leave transcripts and the original memo alone.
- One `missed` is a note; a pattern across 2-3 decisions becomes a standing adjustment.
- A real decision may differ for reasons unrelated to the person (politics, timing, an
  executive overruling the group). Say which.
