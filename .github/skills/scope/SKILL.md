---
name: scope
description: Build a scope and high-level plan for an idea a named team is moving forward on. Facilitates boundaries, sequencing, dependencies and blockers with mitigation strategies, then produces one plan and verbatim discussion without formal votes.
---

# Scope an Idea With a Named Team

Produce one scope and high-level plan, including potential blockers, mitigation
strategies and unresolved decisions. The leader synthesizes the team's discussion
and preserves dissent; no formal votes or implementation commitments are made.
All contributions are simulations, never statements or predictions by real people.

## Select the idea and room

1. Run **account-scope**, then **decision-input**. Require an explicitly selected
   team and a specific idea to scope. Persist `workflow: scope`.
2. Accept either a linked completed **evaluate** result or explicit user direction
   that the idea should move forward. Do not treat a brainstorm ranking as approval.
   If the idea or move-forward basis is unclear, ask before running.
   For linked input, validate the account-relative path inside the selected account,
   read that transcript and run `render_transcript.py {source} --check`. Require an
   evaluate/legacy decision workflow, a SUPPORT decision, or CONDITIONAL with the
   conditions explicitly addressed in framing. An OPPOSE/incomplete result requires
   clarification or explicit user direction to proceed despite it. A recommendation
   to escalate is not approval by the escalation authority; retain that dependency.
   If using user direction, preserve the user's words in `source.basis`. A supplied
   link may refer to another team in this account, but never changes this run's
   explicitly selected team. Never access another account.
3. Follow **Select and validate before running** and **Roles, context and memory**
   in [evaluate](../evaluate/SKILL.md) for scope validation, team resolution,
   attendees, retired guests, progressive context, thin profiles and unused names.
   For this workflow save `workflow: scope`, not evaluate. Read only those shared
   sections; do not run decision phases or decision close.
4. Reuse the shared [leader](../evaluate/references/team-leader.md) and
   [participant](../evaluate/references/team-participant.md) resources with
   **profile-context** and **memory-management**. Inject this scope round contract,
   source basis, current draft plan and full labelled history into native
   `leadership-specialist` tasks. Include explicit account, team, identity,
   assignment, own memory path and run reference. Use fresh synchronous calls,
   batch independent calls, omit `model`, and stop on unavailable/denied native
   dispatch rather than using an unscoped fallback.
   All participants contribute, including advisors; `vote` flags remain in the
   snapshot but are not used for ballots. All-advisor teams can scope.
   Defer every seat's memory write until explicit post-check confirmation.

## Team discussion

1. **Frame (`framing`):** the leader states the selected idea, move-forward basis,
   beneficiary/outcome, success measures, known constraints, approval conditions,
   authority and unknowns. Distinguish a simulated decision or user direction from
   evidence of actual organizational approval. Do not reopen ideation by default.
2. **Advisor briefings (`briefing`):** advisors brief first on facts with source/
   period, dependencies, feasibility, regulatory/operational constraints and
   potential blockers. Do not silently add missing expertise.
3. **Boundary proposals (`scoping`):** every seat and the leader proposes what is
   in/out of scope, minimum useful deliverables, assumptions and success evidence.
   Surface competing boundaries and ownership/capacity gaps. The leader records
   their own contribution separately from facilitation.
4. **Build the plan (`planning`):** run at least two numbered planning rounds;
   every attending seat must speak in planning.
   - First, challenge scope creep and sequence high-level phases, dependencies,
     milestones and exit criteria. Prefer a smallest useful first phase.
   - Then stress-test capacity, access, funding, approvals and delivery assumptions.
     Identify potential blockers, mitigations, fallback/de-scope options, proposed
     owners, and evidence/decisions needed to clear each blocker.
   Calls name specific draft elements and challenges. Ask seats to engage peers'
   arguments, explain changes and identify what cannot safely proceed yet.
   Contrarian tests failure modes; Moonshot finds simpler or better approaches
   within the chosen outcome, not an unrelated idea backlog.
5. **Maintain blockers:** give each blocker a stable ID; record originating turns
   using `blocker_ids`. Preserve all raised blockers through final synthesis,
   including resolved ones. A blocker prevents a named phase (or `start`) until
   a condition is met; other uncertainty belongs in risks/open questions.
   For each capture description, impact, mitigation, proposed owner, gate,
   clearance criterion, evidence and `status: open | resolved`.
   Mitigation is a proposed strategy, not proof of resolution. Unknown owner or
   evidence stays explicitly unknown; never mark resolved without recorded
   clearance evidence. If no feasible mitigation is known, state that, propose
   the next investigation/escalation and keep the blocker open.
6. **Final review (`plan_review`):** share the complete draft. In parallel every
   participant/advisor/archetype returns corrections, unresolved blockers,
   safeguards and dissent. No SUPPORT/OPPOSE positions, rankings or endorsement
   tally. New material concerns require another planning round and fresh final
   reviews before synthesis; retain the original reviews in the transcript.
7. **Synthesize (`synthesis`):** the leader records final boundaries, high-level
   phases and rationale, explicitly addressing each advisor/archetype and
   unresolved disagreement. Use readiness `blocked` if an open blocker gates
   `start`, `conditional` if open blockers gate later phases, otherwise
   `ready_for_review`. A complete discussion may produce a blocked plan; that is
   not an incomplete run or an implementation approval.
   Preserve approval dependencies and required escalation. Material changes to
   the approved idea's outcome, budget or authority go back to **evaluate**.

## Transcript and combined outcome

Reuse evaluate's session clocks, cost limitations, full `team_snapshot`,
`effective_room` and `roster`. Set `session.workflow: "scope"` and actual
`session.planning_rounds`. Save under the selected team's existing `decisions/`
using unused `YYYY-MM-DD-{topic-slug}-scope` basenames for memo, transcript and
discussion. Preserve input and prior runs; scope never edits its source decision.

Initialize `framing: null`, `turns: []`, `plan: null`, `blockers: []`,
`final_votes: []`, `archetype_positions: []`, `decision: null`.
`source` has nonempty text `kind` (`evaluate` or `user_direction`), `idea`,
`basis` and `reference` (account-relative transcript path for evaluate,
`user request` for unlinked direction). User direction remains labelled as such.
Turns have timestamp, speaker, role, prompt, unedited content and `position: null`.
Allowed rounds: `framing`, `briefing`, `scoping`, `planning`, `plan_review`,
`synthesis`. Planning turns have positive `planning_round` starting at 1.
Turns raising blockers carry `blocker_ids` with corresponding catalogue IDs.
Persist the complete JSON after each return and verify every dispatched speaker.

Each blocker has nonempty text `id`, `description`, `impact`, `mitigation`, `owner`,
`gate`, `clearance`, `evidence`, `status`. `gate` is `start` or a phase's `name`.
Resolved status requires evidence beyond an unverified mitigation proposal.
`plan` has nonempty text:
`outcome`, `success_measures`, `in_scope`, `out_of_scope`, `deliverables`,
`assumptions`, `constraints`, `dependencies`, `risks`, `open_questions`,
`next_steps`, `dissent`, `rationale`, `authority` (`recommendation`), `readiness`.
Use explicit `None identified after review` where appropriate, not blank fields.
`phases` is a nonempty list of unique names, each with nonempty text `name`,
`deliverable`, `exit_criteria`, `owner`, `timing`, `dependencies`.
All owners are proposed; unknown capacity, dates and estimates remain unknown.
No detailed task backlog, tickets, deployment or implementation is produced.

Write one combined Markdown document using the final recorded plan and blockers:
simulation/source basis; intended outcome and success measures; in/out of scope;
deliverables, assumptions and constraints; high-level phases/milestones with
proposed owners, timing, dependencies and exit criteria; risks; **blockers and
mitigation strategies** including gate, clearance evidence and unresolved owners;
readiness and what can/cannot proceed; dissent and leader rationale; open
questions, immediate next steps and escalation. Do not use the approval-oriented
**memo-format** or fabricate dates, commitments or a real approved project plan.

## Close and verify

1. Close actual clock/duration and run
   `python3 scripts/render_transcript.py {transcript-path} --check`.
   This validates the frozen room, source shape, discussion participation,
   numbered planning, final reviews, plan fields and blocker/readiness consistency.
   It does not prove source approval, evidence truth or mitigation effectiveness;
   the facilitator must assess those separately.
2. If interrupted, preserve the partial record with `session.status: incomplete`
   and `session.incomplete_reason`, render it and report unfinished work. Leave
   input pending, publish no completed scope memo and append no scope memory.
3. After a passing check, write the combined document and render the discussion.
   Collect gaps and append deduplicated entries using evaluate's gaps-log format.
4. Append the leader's own SCOPE memory and send each seat a separate post-check
   instruction to append only its own memory. Use **memory-management**, preserving
   team/run and source provenance, blockers and uncertainty, not approval votes.
5. Verify outputs and memory confirmations, then archive input to an unused
   selected-team `questions/done/` destination. Report plan/discussion paths,
   readiness, blocking gates, mitigation strategies and any failed writes.
   A structurally complete blocked plan may be archived; open blockers remain
   explicitly open in it. Subsequent changes use fresh runs linked by `rerun_of`;
   never rewrite the source decision or historical scope.
