---
name: record-outcome
description: Compare a named team's simulated decision with the real outcome, record per-person calibration and team dynamics, and preserve the original team history.
---

# Record Outcome

Close the learning loop against real evidence, not inferred agreement. Success
means an outcome note, supported per-profile calibration, profile-owned leader
lessons and rebuilt indexes, without changing original memos or transcripts.

## Select and scope

Run **account-scope** first. Work only in `{account}`. Ask for the team and decision
reference if unclear, then look only in that team's decisions. Never read another
customer's history.

Use the saved transcript's `team_snapshot`, `effective_room`, `leader` and `roster`,
not today's team membership: removed participants still belong to that past run.
Validate all supplied paths remain in the selected account before reading or writing.
If the transcript lacks a named team, leader or room snapshot, stop and explain
that a complete named-team record is required. Never infer missing membership or
guess a replacement person from the current team definition.

If `session.workflow` is `brainstorm` or `scope`, stop before outcome/calibration writes.
Explain that exploratory rankings and proposed plans are not approve/deny predictions; use a
subsequent evaluate decision record for this workflow. Do not convert rankings
into real-person positions.

Ask the user:
1. What actually happened, and the decision date.
2. Who took which position and why, if known. Unknown is valid.
3. Source and confidence: first-hand, second-hand or public inference.
4. What surprised them, including who really decided or overruled the team.

## Compare and record

1. Read the original memo/transcript. Extract the leader's call, each attending
   person's opening or briefing, final position/advice and reasons, plus decision
   authority. Include advisors; do not treat them as voters.
2. Compare each person as `matched`, `partial`, `missed` or `unknown`, with a short
   reason. Assess team dynamics: scope, escalation, deference and actual decision
   maker. Synthetic archetypes may be assessed for useful reasoning but are not
   real people and never receive a fabricated real-world position or biography.
3. Write an unused `YYYY-MM-DD-{topic-slug}-outcome.md` beside the original decision;
   never overwrite an earlier outcome or original artifact. Include:
   - recorded date, team/run reference, evidence and actual decision date;
   - What actually happened;
   - Twin vs. reality table: Person, Twin predicted, Reality, Verdict, Why the gap;
   - Team dynamics (scope, deference, who really decided);
   - Lessons; Context that would have changed the answer.
4. For each person with sufficient evidence (not `unknown`), append to the resolved
   canonical profile's `calibration.md`. Create with front-matter
   `summary: Where past simulations diverged from the real person`,
   `tags: [calibration]`, `load: always`, `roles: [{profile-id}]`.
   Entry heading: `### {date} - {team/run reference} - {topic} - {verdict}`.
   Follow with 2-3 lines: real behavior, simulated prediction, adjustment.
   Calibration is account-wide and reusable across teams; label the team so a
   context-specific result does not become an unsupported global personality.
   Keep about 15 entries, merging older supported patterns into Standing adjustments.
   Skip archetypes and unknown positions. Correct other dossier facts through
   company-research, not here.
5. Append peer-reliability and scope/deference lessons only to the historical
   leader's `{account}/company/profiles/{historical-leader-id}/memory.md`, using
   the original profile ID even if someone else now leads. Follow **memory-management**
   and label the original team and run so lessons retain their context across teams.
   Never edit participants' own memories or use today's leader as a replacement.
   If the historical profile is missing, stop and request its restoration rather
   than creating a replacement identity.
6. Append missing evidence to `{account}/company/gaps.md`, offer company-research,
   and run `python3 scripts/build_index.py {slug}`.
7. Verify the note and calibration updates exist; report supported hit rate,
   unknown count, biggest miss and correction, and what to watch next time.

## Reruns and limits

If linked reruns exist, offer to record the same outcome against each independently
using its own room snapshot; do not assume all team members or advice were the same.
Never rewrite history. A single miss is a note, not a new personality; a pattern
across 2-3 supported outcomes can become a standing adjustment. Politics, timing
or an executive override may explain a different outcome without a personality
error. State which evidence supports the explanation.
