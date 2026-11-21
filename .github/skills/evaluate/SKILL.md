---
name: evaluate
description: Evaluate a proposal with an explicitly selected named team. Its profile-backed leader facilitates deliberation among participants and advisors and produces a decision memo, transcript and discussion. Use for proposal assessment, approval decisions and trade-off evaluation, not brainstorming.
---

# Evaluate a Proposal With a Named Team

Produce a decision memo and verbatim readable discussion for the explicitly selected
team. Everything is a simulation based on public and supplied account context,
never statements or predictions by the real people.

For explicit idea-generation/brainstorming intent or `workflow: brainstorm`, use
**brainstorm** instead of this approval-oriented deliberation. Clarify conflicting
workflow selections through decision-input. Existing decision requests are unchanged.
For scoping and high-level planning of an idea moving forward, use **scope**;
it produces boundaries, phases and blocker mitigations, not another approval vote.

## Select and validate before running

1. Run **account-scope**. `{account}` is the explicitly selected account and `{slug}` its slug.
   `{team}` is `{account}/teams/{team-slug}`. Do not access another customer.
2. Read the question with **decision-input**. Resolve the team's slug from the
   user's request and/or question `team:`. If both specify different teams, stop
   and ask which is intended. If neither specifies one, list teams with
   `python3 scripts/teams.py list {slug}` and ask, even if only one exists.
   Never assume the core leadership team or infer a team from the topic.
   If `account:` is present, require it to match the selection and question path
   before resolving the team or reading dossiers. A question never selects or
   changes the account automatically. Existing questions without `account:` use
   the explicitly selected account; check their physical account/team path too.
3. Run `python3 scripts/teams.py resolve {slug} {team-slug}`. When the input has
   `team:`, pass it with `--input-team {input-team}` to detect conflicts. Pass each
   requested participant subset as `--attendee {profile-id}`. The leader always
   attends; `attendees` names participants only. Unknown/duplicate attendees, missing profiles, invalid teams
   or team conflicts block the run. Use **define-team** to fix them; no fallback.
4. The resolved JSON is authoritative for identities, leader, voter/advisor flags,
   archetypes and workspace. Do not add people or perspectives silently. If needed
   expertise is missing, use **define-team** to propose a membership change and
   await approval, then resolve the team again. Advisors are participants with
   `vote: false`, not question-only guests. Stop on retired `guests:` input and
   follow decision-input's explicit update procedure; do not silently ignore it.
   Thin profiles require a warning and an offer of **person-profile**, not
   fabricated identities. No shared per-person role prompt is required.
5. Read `{account}/company/index.md`; if absent or still `account: TBD`, stop and
   offer **company-research**. Read profiles progressively using **profile-context**.
6. Save free-text input as `{team}/questions/{topic-slug}.yaml`, including
   `account:`, `team:` and `workflow: evaluate`. The question path, account field and team field must
   agree with the explicit selection. Account metadata describes scope; it does
   not acquire a runtime lock.
   Reserve unused date/topic output names (suffix `-2`, `-3`,
   etc. on collisions); never overwrite prior runs.

If the selected team has no definition, use **define-team** before evaluating.

## Roles, context and memory

You are the selected leader, not necessarily the CEO. Read
`references/team-leader.md`, your resolved dossier and the **profile-context** and
**memory-management** skills. Use your profile ID as speaker; mark facilitation turns
`role: facilitator` so your own position stays distinguishable.

For every other seat, read `references/team-participant.md` and inject its body plus
the profile-context and memory-management skill bodies into a native
`leadership-specialist` task. Include:

```text
Account workspace: {account}. Team workspace: {team}.
Read company context only inside this account, progressively through indexes.
Your profile ID and speaker ID: {profile-id or archetype-id}.
Your resolved name/title, dossier and default areas: {resolved values}.
Your assignment: {voting participant | advisor, no vote | synthetic archetype, separate position}.
Leader: {leader profile ID and resolved name}.
Team purpose/authority and escalation: {values from resolved team}.
Your only writable path: {account}/{resolved person memory path}, or
{team}/memories/{archetype-id}.md for a synthetic archetype only.
{Round-specific prompt and full conversation history labelled by speaker and round}
Return your response as the task's final output. Do not delegate.
```

Use `task` with `agent_type: "leadership-specialist"`, `name` = speaker ID and
`mode: "sync"`. Omit the `model` parameter from every specialist call so the
subagent inherits the orchestrator's current session model. Do not pin a model,
reuse a model from a prior run or assign a different model by seat. Batch independent synchronous
calls using the parallel wrapper. Wait for all responses before advancing.
If background calls are used, await notifications and collect known IDs once;
never poll or mistake a launch acknowledgement for a response.
Use fresh calls carrying the full history each round.
If the native agent is unavailable or scope is denied, stop and preserve the error;
restart Copilot if needed, not an unscoped general-purpose fallback.

Only the selected leader and participants use person dossiers. Archetypes read the
company brief and relevant area indexes, not a fictional biography. Each person's
resolved `memory` path is account-relative:
`company/profiles/{profile-id}/memory.md`, shared across their teams. Archetype
memory stays at `{team}/memories/{archetype-id}.md`.
If absent, proceed without prior memory. Validate paths remain inside this account;
read only your own memory, not peers' files or another team's archetype memory.
Do not fall back to legacy team-local person memory; offer the explicit import
in **memory-management** before running when older history needs to be retained.
Team definitions alone determine membership and voting.

## Transcript

Create `{team}/decisions/YYYY-MM-DD-{topic-slug}-transcript.json` before the meeting.
Rewrite the complete JSON after every step and response:
For a parallel batch, save every returned response before starting the next batch
or phase. A task completion is not recorded until its full output is in `turns`;
verify the speaker IDs against the dispatched seats, not just a response count.

```json
{
  "session": {
    "account": "{account-slug}", "team": "{team-slug}", "team_name": "{display name}",
    "workflow": "evaluate",
    "leader": "{leader-profile-id}", "topic": "{topic}", "slug": "{topic-slug}",
    "date": "{YYYY-MM-DD}", "started_at": 0, "ended_at": null,
    "duration_seconds": null, "time_limit_seconds": null,
    "cost_limit_usd": null, "total_cost_usd": null, "deliberation_rounds": 0,
    "team_snapshot": {}, "effective_room": {}, "roster": {}, "rerun_of": null
  },
  "framing": null, "turns": [], "final_votes": [], "archetype_positions": [],
  "decision": null
}
```

Set `started_at` from the actual clock, not the example zero. Copy `team_snapshot`
and `roster` from resolution. Set `effective_room` to the resolved `leader`,
`participants` (including vote flags), `facilitation` and `escalates_to` values.
Keep the individual objects and identities, not counts or placeholder descriptions.
This freezes the room independently of later edits.
Record supplied time limits; costs are measured runtime values only, otherwise
null with the limitation disclosed. Do not claim a hard spending limit.

Each turn contains `round` (`briefing`, `opening`, `deliberation`, `final_vote`),
`timestamp`, `speaker`, `role` (`specialist` or `facilitator`), `prompt`, full unedited
`content`, and `position` (`SUPPORT`, `OPPOSE`, `CONDITIONAL` or null).
Every deliberation turn also has an integer `deliberation_round`, starting at 1.
Never summarise or truncate a specialist response in the transcript.

## Deliberation

1. **Frame:** state the core trade-off, constraints, decision authority and missing
   expertise. Record the framing and a leader facilitation turn.
2. **Advisor briefings:** if non-voting team participants are attending,
   ask them in parallel for a considered briefing before anyone's opening reaction:
   domain facts with source/period, options, constraints, risks and what the team
   should debate (typically 4-8 paragraphs). Record verbatim and then a short leader
   facilitation turn naming the claims without rebutting them.
3. **Opening:** ask voting participants and archetypes in parallel for short first
   reactions, giving them the full advisor briefings. The leader records their own
   initial position. Advisors do not repeat their briefing as an opening.
4. **Read the room:** record 3-5 tensions, absent functions and any deference to rank.
   Open the argument; do not jump to consensus.
5. **Deliberate:** each round call 1-3 relevant seats with the full labelled history
   and a specific challenge. Prefer the sharpest divergent positions in the first
   two rounds, then affected functions and unanswered challenges. Ask for 2-4 tight
   paragraphs that advance the argument. After each response, save it and record
   what shifted, hardened and remains unresolved, plus who should answer next.
   The leader must also address challenges to their own position.
6. **Stop only when:** at least four deliberation rounds have occurred, every
   attending participant/advisor/archetype has spoken in deliberation, positions
   evolved or hardened, remaining disagreement needs new evidence, and the leader
   can decide. If an explicit time limit or tool failure prevents this, preserve
   the partial transcript and report the incomplete run, not a completed decision.
7. **Final positions:** in parallel, ask voters for SUPPORT/OPPOSE/CONDITIONAL, their
   single most important reason and what would change it. Ask advisors instead for
   3-5 sentences of final advice, a required safeguard and the risk if ignored.
   Archetypes give separate final positions, not member votes.
   Save all final responses as turns; advisors have `position: null`. Store only
   voting participants in `final_votes` (speaker, position, reason, condition).
   Store archetypes in `archetype_positions` with the same shape. Show `PARTICIPANTS`,
   `ARCHETYPES` and `ADVISOR ADVICE` separately. The leader is not tallied.
8. **Decide:** weigh arguments, not majority count. Record `decision` with position,
   rationale, participant-only `vote_tally`, overrule_explanation and authority
   (`decision` or `recommendation to escalate`). Explain overruled dissent and how
   every advisor's advice was addressed. Anything beyond the team's purpose,
   authority or budget is a recommendation with an explicit escalation request.

## Close and verify

1. Run `python3 scripts/render_transcript.py {transcript-path} --check` before
   publishing a completed memo, appending decision memories or archiving the question.
   This read-only completion gate checks the frozen room, recorded responses,
   numbered rounds, final positions and participant-only tally. Correct missing
   recording from actual task returns; never manufacture missing debate or votes.
   If the run cannot finish, set `session.status` to `incomplete` and record
   `session.incomplete_reason`; render and report the partial run, leave the question
   pending, and do not publish a completed decision or append decision memories.
   A passing structural check does not replace assessing argument quality.
   Write `{team}/decisions/YYYY-MM-DD-{topic-slug}.md` using **memo-format**.
   Quantify where evidence permits; attach owner, capacity and timeline to next
   steps; address the Contrarian pre-mortem if present.
2. Close the transcript using the actual end clock and duration; record only measured
   runtime costs. Run `python3 scripts/render_transcript.py {transcript-path}`.
3. Collect every `Context gaps:` line and your own gaps. Append deduplicated
   `- [open] YYYY-MM-DD - {area} - {fact} - raised by {speaker} - {topic-slug}`
   entries to `{account}/company/gaps.md` and list them in the memo. This gaps log
   and own profile memory are the only company-context writes by the facilitator;
   researched dossier documents remain read-only.
4. Append leader decision memory and notable peer patterns to their profile memory.
   Participants write only their own memory after their final turn. Include the
   team, run reference and topic in entries; do not rewrite older entries or invent
   memories. Archetypes append only to their selected team's archetype memory.
5. Move the team question to `{team}/questions/done/YYYY-MM-DD-{name}.yaml` using an
   unused destination.
6. Verify outputs exist, all expected final positions/advice and four-round
   participation are recorded, and the archived input and memory writes completed.
   Report memo/discussion paths, simulation status, gaps and any incomplete work.
   Offer **record-outcome** for comparison with the real decision.

## Reruns and different teams

Copy the original input to a fresh question, set the explicitly selected `team:`
and `rerun_of` to the original account-relative transcript path. Apply approved
team-definition or attendee changes; never edit the original or silently change
the saved team. Translate retired `guests:` only through an approved team update.
The leader and participants must not read the previous memo/transcript until the
new decision is made. Existing eligible memory may mention it; disclose that this
is not a blind test. After deciding, compare the two rooms, arguments, vote shifts
and decisions in the memo's Comparison With Prior Run. Preserve both runs.
