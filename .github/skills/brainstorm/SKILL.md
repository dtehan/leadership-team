---
name: brainstorm
description: Generate, develop and prioritize ideas with an explicitly selected named team. Use for brainstorming and exploratory team questions, not approve/deny decisions. Produces an idea backlog, ranked priorities and verbatim discussion.
---

# Brainstorm With a Named Team

Produce a broad idea backlog, substantive discussion and prioritized exploration
recommendations. All contributions are simulations based on public and supplied
context, never statements or predictions by real people. Priorities are not
implementation approvals.

## Scope and prepare

1. Run **account-scope**, then parse the question using **decision-input**.
   Persist `workflow: brainstorm`. A request/input workflow conflict blocks the run.
2. Read and follow the **Select and validate before running** and **Roles, context
   and memory** sections of [evaluate](../evaluate/SKILL.md), including explicit team
   selection, account/path checks, `teams.py resolve`, attendee validation, retired
   guests handling, progressive context, thin-profile warnings and unused output
   names. Reuse those sections only; do not run decision deliberation or its close.
3. Require at least one attending participant with `vote: true` for rankings.
   If none attend, stop and offer an approved attendee/team update through
   **define-team**, not a leader-only or advisor ballot.
4. Use the shared [leader](../evaluate/references/team-leader.md) and
   [participant](../evaluate/references/team-participant.md) resources plus
   **profile-context** and **memory-management**. Inject the complete round
   contract below into each native `leadership-specialist` task alongside the
   account, team, resolved identity/assignment, own memory path and run reference.
   Use the shared dispatch contract: fresh calls with full labelled history,
   `mode: "sync"`, batch independent calls, omit `model`; no unscoped fallback.
   Generation calls receive framing and advisor briefings but no peers' generated
   ideas. Later rounds receive the complete history and current idea catalogue.
   Specialists write no memory until a separate post-check instruction.

## Generate, develop, prioritize

1. **Frame (`framing`):** the leader states an open-ended challenge, desired
   outcome, scope, constraints, unknowns and priority criteria. Default criteria
   are impact, feasibility and evidence/confidence. Agree requested criteria
   before generating ideas; do not start with a preferred solution or an approval
   motion. Record criteria and constraints as text in `framing`.
2. **Advisor briefings (`briefing`):** advisors brief in parallel on domain facts
   with source/period, constraints and opportunities, without ranking solutions.
   The leader acknowledges gaps without closing the solution space.
3. **Independent generation (`idea_generation`):** all participants, advisors,
   configured archetypes and the leader propose distinct ideas from their lenses.
   Ask for a practical option and a bolder alternative, each with a title,
   beneficiary, mechanism and assumptions. Defer critique and ranking. The
   leader records their own contribution separately from facilitation.
   Save every verbatim response before sharing the generation batch.
4. **Catalogue:** assign stable IDs (`idea-1`, etc.) to every distinct proposal.
   Record `id`, `title`, `description`, `proposer`, `assumptions` and `experiment`
   (a small next test). Store the IDs extracted from each generation response on
   its turn as `idea_ids`. Do not invent proposals absent from those responses.
   Keep all original IDs, including lower-priority ideas. Group similar ideas in
   facilitation prose; discuss combinations without deleting their components.
5. **Develop (`refinement`):** run at least two numbered refinement rounds. Every
   attending seat must speak in refinement. First build on ideas, combine
   mechanisms and surface alternatives; then stress-test value, feasibility,
   dependencies, evidence gaps and a cheap experiment. Each call names idea IDs
   and a specific challenge; return concrete improvements and disagreements,
   not a recap or approve/deny position. The leader responds to challenges and
   records what changed. Update catalogue descriptions/assumptions/experiments
   from the recorded discussion while preserving IDs and proposer provenance.
   New proposals need a recorded `idea_generation` turn before ranking, then
   refinement; do not silently add ideas during prioritization.
6. **Prioritize (`prioritization`):** freeze and share the catalogue. In parallel,
   each voting participant independently returns `order` (every idea ID exactly
   once, most preferred first) and `reason` explaining trade-offs against the
   framed criteria, including uncertainty and their top choice's next test.
   Record these fields both on the verbatim turn and in `rankings` with `speaker`.
   Advisors give final advice, safeguards and experiment guidance instead;
   archetypes give separate challenges/opportunities. Both have `position: null`
   and no `order`. The leader does not submit a ballot.
7. **Synthesize (`synthesis`):** tally only voting participants using Borda points:
   for N ideas, first gets N-1, last gets 0. Report totals and ties without
   presenting ordinal preferences as measured impact. The leader produces a
   final full `order` and `rationale`. Preserve the participant tally separately;
   explain every reversal of an unequal total in `differences`, and explain
   tie-breaking there too. Surface minority favorites and address every advisor
   and configured archetype. Priorities remain recommendations for exploration,
   with escalation identified where applicable; do not imply committed owners,
   spending or permission to implement.

## Transcript contract

Use the shared transcript session identity, clocks, cost limitations, frozen
`team_snapshot`, `effective_room` and `roster` from evaluate. Set `session.workflow`
to `"brainstorm"` and `session.refinement_rounds` to the actual count.
Initialize `framing: null`, `turns: []`, `ideas: []`, `rankings: []`,
`prioritization: null`, `final_votes: []`, `archetype_positions: []`, `decision: null`.
Save under `{team}/decisions/YYYY-MM-DD-{topic-slug}-brainstorm-transcript.json`;
use that same unused basename for the memo and rendered discussion.

Turns retain timestamp, speaker, role, prompt and full unedited content.
Allowed rounds are `framing`, `briefing`, `idea_generation`, `refinement`,
`prioritization`, `synthesis`. Every `position` is null; refinement turns also
carry positive integer `refinement_round` starting at 1. Generation turns carry
`idea_ids`. Ballot turns carry `order` and `reason`.
Save the complete JSON after each turn; collect every batch's full responses
and verify dispatched speaker IDs before advancing.

Each idea has nonempty text fields `id`, `title`, `description`, `proposer`,
`assumptions`, `experiment`; `proposer` names a roster seat with a generation
turn containing that ID. Each ranking has `speaker`, `order`, `reason`.
`prioritization` has `order`, `rationale`, `differences` (text, empty only if no
tie or reversal needs explaining) and `authority: "recommendation"`.
The renderer calculates totals directly from rankings; do not store a second tally.

## Close and verify

1. Set actual end time/duration; record costs only if measured. Run
   `python3 scripts/render_transcript.py {transcript-path} --check`.
   Completion requires the frozen room, advisor briefings, everyone's generation
   and refinement, two numbered refinement rounds, all final rankings/advice,
   valid catalogue provenance and full leader priorities. Never manufacture
   missing responses. A structural pass does not certify creative quality.
2. If interrupted or a tool fails, preserve the partial record, set
   `session.status: incomplete` and `session.incomplete_reason`, render it and
   report unfinished work. Leave input pending; publish no completed brainstorm
   memo and append no brainstorm memory.
3. After a passing check, write `{basename}.md` with: simulation disclaimer;
   challenge/criteria; grouped idea backlog with IDs, assumptions and experiments;
   discussion improvements and unresolved differences; participant rankings and
   Borda totals/ties; advisor advice and synthetic perspectives separately;
   leader's prioritized shortlist plus remaining backlog and reasons for changes;
   proposed next experiments with proposed owner, capacity and timeline (unknown
   stays unknown); context gaps and escalation. Do not use **memo-format**'s
   approval/deny decision template.
4. Render with `python3 scripts/render_transcript.py {transcript-path}`. Collect
   and append deduplicated context gaps using evaluate's gaps-log format.
5. Append the leader's own BRAINSTORM memory and explicitly instruct each seat
   to append only its own memory now, using **memory-management** with team/run
   provenance. Verify returned write confirmations; report any failure explicitly.
6. Archive input to an unused destination in the selected team's `questions/done/`
   only after outputs and memory writes are verified. Report memo/discussion paths
   and gaps. Use **evaluate** on a fresh question if approval is subsequently needed;
   brainstorming preferences are not real outcomes for **record-outcome**.
   Once an idea has a move-forward basis, use **scope** for boundaries, a
   high-level plan and blockers/mitigations; priorities alone are not that basis.

Reruns reserve fresh input/output names and preserve the original. Withhold the
prior memo/transcript from seats until new priorities are recorded, then compare
ideas and rankings. Disclose that eligible memory may mention the old run.
