---
name: convene-group
description: Convene a defined working group (e.g. a middle-management team) on a question - a chair runs a multi-round deliberation among the member twins (plus optional Contrarian/Moonshot), then produces a decision memo and a readable discussion. Use when the user poses a decision or scenario for a group they defined, or points at a file in the group's questions/.
---

# Convene a Group

> **Account scope:** run the **account-scope** skill first. This session works on one customer only; `{account}` = `accounts/{slug}`. Never touch another account.

Same process as the leadership `convene` skill, with the cast taken from a **roster** instead of
the fixed executive team. `{group}` = `{account}/groups/{group-slug}`. Everything is a
simulation built from public and supplied context under `{account}/company/`; say so in
anything you hand the user. Leadership agents (`cfo`, `cto`, ...) are **not** part of the room;
members may *report to* them, which only shapes how the member thinks.

## Before you start

1. Run **account-scope**. Then `python3 scripts/groups.py list {slug}`; pick the group (ask if
   several and the question does not say; confirm even when there is one).
2. Run `python3 scripts/groups.py check {slug} {group-slug}`. If the roster is missing, has no
   members, or the chair is unknown, stop and run **define-group**. If profiles are stubs,
   tell the user the twins will be generic and offer **company-research** first. Warnings
   about thin profiles do not block; a missing roster or empty purpose does.
3. Read `{account}/company/index.md`. If it is the empty template (`account: TBD`), stop and
   offer **company-research**.

## The room

- Read `{group}/roster.md`: front-matter (`purpose`, `chair`, `facilitation`, `escalates_to`)
  and the member table.
- **Attendees**: the question may list `attendees: [slug, ...]` to call a subset (not every
  manager is relevant to every question). If absent, the whole roster attends. If the
  question clearly concerns functions not in the room, **propose** adding them or running
  with a different `attendees:` and wait for a yes; do not change the room silently.
- **Voters** are attendees with `vote: yes`. Attendees with `vote: no` are **advisors**:
  they speak, give final advice, and are not in the tally. A member chair also votes.
- **Chair**: if `chair` is a member slug, that member's twin chairs (and is also a member);
  if `neutral`, the chair is a facilitator with no function and no vote.
- **Archetype seats** from `facilitation:` (`contrarian`, `moonshot`) join as voters-in-name
  only for the tally: they speak and give a final position, but list them separately from
  members in the tally as `ARCHETYPES`.
- Record the room in the transcript (`session.roster`, below).

## Calling the room

Orchestrate with the **Agent tool**, one agent per seat.
1. **Chair**: read `.pi/agents/group-chair.md`, use only the body. The chair is *you* (the
   orchestrating assistant), reading that file as your role, as the Leader does in `convene`.
   For a member chair, also load that member's dossier (below) so you keep their voice.
2. **Each other seat**: read `.pi/agents/group-member.md` (body only) and
   `.pi/skills/profile-context/SKILL.md`. Call the Agent tool with `subagent_type: general-purpose`,
   `name: "{member-slug}"`, `model: "sonnet"`, and a prompt made of: the two files, then
   ```
   Your slug is {member-slug}. You are {Name}, {Title}. [archetype seats: "You are the {contrarian|moonshot} archetype seat; no dossier."]
   Account workspace: {account}. Group workspace: {group}. Read and write only inside them.
   Your dossier: {profile link as resolved: folder, file, or "none yet - stay generic"}.
   You report to: {reports_to, or none}. Your memory file: {group}/memories/{member-slug}.md.
   The group's purpose: {purpose}. It escalates to: {escalates_to}. Your vote: {yes | advisor, no vote}.
   {round-specific message}
   ```
   Where the profile is an http(s) URL only, tell the member there is no dossier yet. Where it
   is a single file, tell them to read that file in place of the dossier folder.
3. **Parallel broadcast** (opening and final rounds): one Agent call per attendee with
   `run_in_background: true`, all in a single response; wait for all.

Specialists may end with `Context gaps: ...`: keep them in the transcript and collect them.

## Process

1. **Load your context** as chair: **profile-context** skill as a guest-style reader: the
   account brief and all area indexes; if a member chair, also their dossier (`load: always`
   docs). Read memory `{group}/memories/chair.md` (neutral) or `{group}/memories/{chair-slug}.md`
   (member chair), especially **Peer Patterns**.
2. **Parse the input** from the group's `questions/` file (see **decision-input**; `attendees:`
   is an optional extra field here). If the user asks in free text, write it to
   `{group}/questions/{slug}.yaml` first.
3. **Initialise the transcript** `{group}/decisions/YYYY-MM-DD-{topic-slug}-transcript.json` and
   rewrite it in full after every step:
   ```json
   {
     "session": {
       "topic": "", "slug": "", "date": "", "started_at": 0, "ended_at": null,
       "duration_seconds": null, "time_limit_seconds": 0, "cost_limit_usd": 0, "total_cost_usd": 0,
       "deliberation_rounds": 0, "account": "{slug}", "group": "{group-slug}", "group_name": "{name} group",
       "chair": "{member-slug | neutral}",
       "roster": {"chair": "Chair", "{member-slug}": "{Name} ({Title})"}
     },
     "framing": null, "turns": [], "final_votes": [], "decision": null
   }
   ```
   Speakers in turns are `chair` (facilitation turns) or member/archetype slugs. A member
   chair's own contributions are recorded under their slug, their facilitation under `chair`.
4. **Frame the question**: the core tension, what makes it hard, what the group can and cannot
   decide on its own versus what it must escalate. Write `framing`.
5. **Opening round** (parallel, all attendees): instincts only, short.
   ```
   OPENING ROUND - Your immediate read, keep it short: {framed question with full context}
   Return your response as your final output - the chair will collect it.
   ```
6. **Record responses** verbatim as turns (`round: opening`). Never edit them.
7. **Read the room**: 3-5 distinct tensions, listed in a facilitation turn. Include **who is
   missing from the conversation** (functions with no voice yet) and any sign of deference.
   Do not move toward consensus.
8. **Deliberation loop**, as in `convene`: call one to three attendees per round with the full
   history; first two rounds favour the most divergent positions; **every attendee speaks at
   least once**; prioritise the function most affected and anyone who has not yet answered a
   key challenge. Prompt:
   ```
   DELIBERATION - Round {N}. Full conversation so far:
   [Speaker, Round X]: {response}
   ...
   {Your specific question or challenge for this seat}
   Keep your response tight - 2 to 4 paragraphs, no headers. Advance the argument, don't recap it.
   Return your response as your final output - the chair will collect it.
   ```
   After each response: append the turn, write the file, add a facilitation turn (what
   shifted, what hardened, what is still unresolved, who is next).
   **Stop** only when all are true: at least **4 deliberation rounds**; **all attendees** have
   spoken in deliberation; positions have evolved or hardened; remaining disagreement is
   clearly articulated and needs new information; you can decide with confidence.
9. **Final round** (parallel, all attendees). Voters:
   ```
   FINAL VOTE. Full conversation: {history labelled by speaker and round}
   State your final position (SUPPORT / OPPOSE / CONDITIONAL), your single most important reason,
   and any condition that would change your vote.
   Return your response as your final output - the chair will collect it.
   ```
   Advisors (`vote: no`):
   ```
   FINAL ADVICE. Full conversation: {history}
   You have no vote. Give final advice in 3-5 sentences: what the decision must account for from
   your domain, the one safeguard you would insist on, and the risk if it is ignored.
   Return your response as your final output - the chair will collect it.
   ```
   Show the tally: `MEMBERS` (voters), `ARCHETYPES` (if any), then `ADVISOR ADVICE` (one line
   each). Record votes in `final_votes` (members and archetypes; advisor advice goes in `turns`
   with `round: final_vote`, `position: null`). `vote_tally` counts members only.
10. **Decide**: the binding call, as chair. Not a majority count. State what is decided, why,
    and any overruled dissent. **Scope check**: if it exceeds the group's authority or budget
    or touches `escalates_to`, state the decision as the group's recommendation and list what
    the escalation must ask for. Write `decision`.
11. **Produce the memo** at `{group}/decisions/YYYY-MM-DD-{topic-slug}.md`, following
    `.pi/skills/convene-group/memo-format.md`.
12. **Close the transcript** (`date +%s`, duration, cost), then run
    `python3 scripts/render_transcript.py {group}/decisions/YYYY-MM-DD-{topic-slug}-transcript.json`
    to produce the `-discussion.md` (the script reads `session.roster` for display names).
13. **Capture context gaps**: append each `Context gaps:` line (and your own) to
    `{account}/company/gaps.md` as `- [open] YYYY-MM-DD · {area} · {fact} · raised by {slug} · {topic-slug}`
    (skip duplicates); list them in the memo.
14. **Update memory**: append **Past Decisions** and **Peer Patterns** entries for the chair
    (same formats as `convene` step 14) to the chair's memory file. Members write their own.
15. Prefix the question file with `YYYY-MM-DD-` and move it to `{group}/questions/done/`.

## Rerunning with a different room

To rerun a question with different attendees (a member added, a function dropped), copy it to
`{group}/questions/{name}-with-{change}.yaml`, set `attendees:` and `rerun_of:`, never edit the
original, and run a fresh deliberation **without showing the original transcript or memo**.
Afterwards fill the memo's *Comparison With Prior Run*.

## Decision quality standards

- Name the core trade-off. Never dismiss a member's concern without addressing it.
- Quantify where possible; attach an **owner and capacity** to every next step.
- Flag dissent prominently. If it is close, say what would tip it.
- The Contrarian's pre-mortem must be addressed in risk mitigation (if present).

## After the decision

Tell the user in plain terms: where the memo and discussion are (`{group}/decisions/...`);
any open context gaps (offer **company-research**); and that **record-group-outcome** will
compare the simulation with what the real group decided and calibrate each twin.
