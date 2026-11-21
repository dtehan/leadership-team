#!/usr/bin/env python3
"""Render an evaluation, brainstorming or scope transcript as a readable discussion.

Usage: python3 scripts/render_transcript.py <team-transcript.json> [--check]
Writes a readable discussion, explicitly marking incomplete runs.
--check requires a complete recorded discussion and writes nothing.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROUNDS = {"briefing": "Advisor briefing", "opening": "Opening round", "deliberation": "Deliberation", "final_vote": "Final vote"}
BRAINSTORM_ROUNDS = {
    "framing": "Challenge and criteria", "briefing": "Advisor briefing",
    "idea_generation": "Idea generation", "refinement": "Idea development",
    "prioritization": "Prioritization", "synthesis": "Leader synthesis",
}
SCOPE_ROUNDS = {
    "framing": "Idea and move-forward basis", "briefing": "Advisor briefing",
    "scoping": "Scope boundaries", "planning": "High-level planning",
    "plan_review": "Final plan review", "synthesis": "Leader synthesis",
}
PLAN_SECTIONS = {
    "outcome": "Intended outcome", "success_measures": "Success measures",
    "in_scope": "In scope", "out_of_scope": "Out of scope", "deliverables": "Deliverables",
    "assumptions": "Assumptions", "constraints": "Constraints", "dependencies": "Dependencies",
    "risks": "Risks", "open_questions": "Open questions", "next_steps": "Next steps",
    "dissent": "Dissent and advice", "rationale": "Leader rationale",
}
PHASE_FIELDS = ("name", "deliverable", "exit_criteria", "owner", "timing", "dependencies")
BLOCKER_FIELDS = ("id", "description", "impact", "mitigation", "owner", "gate",
                  "clearance", "evidence", "status")


SPEAKERS = {}  # profile or archetype ID -> snapshotted display name
POSITIONS = ("SUPPORT", "OPPOSE", "CONDITIONAL")


def full_order(order, ids):
    return (isinstance(order, list) and all(isinstance(i, str) for i in order)
            and len(order) == len(ids) and set(order) == ids)


def priority_totals(ideas, rankings):
    totals = {idea["id"]: 0 for idea in ideas}
    for ranking in rankings:
        for index, idea_id in enumerate(ranking["order"]):
            totals[idea_id] += len(ideas) - index - 1
    return totals


def brainstorm_issues(t, people, archetypes):
    s, turns = t["session"], t["turns"]
    issues = []
    seats = set(people) | set(archetypes)
    voters = {p for p, vote in people.items() if vote}
    if not voters:
        issues.append("Brainstorm requires at least one voting participant to rank ideas")
    if not isinstance(t.get("framing"), str) or not t["framing"].strip():
        issues.append("Missing brainstorm challenge and priority criteria")
    for phase, expected in (
            ("briefing", {p for p, vote in people.items() if not vote}),
            ("idea_generation", seats | {s["leader"]}),
            ("refinement", seats), ("prioritization", seats)):
        spoken = {turn["speaker"] for turn in turns if turn["round"] == phase
                  and turn.get("role") != "facilitator"}
        missing = expected - spoken
        if missing:
            issues.append(f"Missing {phase} responses: {', '.join(sorted(missing))}")
    for phase in ("framing", "synthesis"):
        if not any(turn["speaker"] == s["leader"] and turn["round"] == phase
                   and turn.get("role") == "facilitator" for turn in turns):
            issues.append(f"Missing leader {phase} turn")
    if any(turn.get("position") is not None for turn in turns):
        issues.append("Brainstorm turns must not carry approve/deny positions")
    if t.get("final_votes") or t.get("archetype_positions") or t.get("decision") is not None:
        issues.append("Brainstorm must not contain decision votes or an approval decision")
    refinement = [turn for turn in turns if turn["round"] == "refinement"]
    declared = s.get("refinement_rounds")
    numbers = {turn.get("refinement_round") for turn in refinement
               if type(turn.get("refinement_round")) is int and turn["refinement_round"] > 0}
    actual = {turn.get("refinement_round") for turn in refinement
              if type(turn.get("refinement_round")) is int
              and turn.get("role") != "facilitator" and turn["speaker"] in seats}
    if (type(declared) is not int or declared < 2
            or any(type(turn.get("refinement_round")) is not int
                   or turn["refinement_round"] < 1 for turn in refinement)
            or numbers != set(range(1, len(numbers) + 1))
            or len(numbers) != declared or actual != numbers):
        issues.append("At least two numbered refinement rounds with recorded seat responses are required")
    phases = [turn["round"] for turn in turns]
    if phases and phases[0] != "framing":
        issues.append("Brainstorm must begin with leader framing")
    if "prioritization" in phases:
        first = phases.index("prioritization")
        if any(phase in ("framing", "briefing", "idea_generation", "refinement")
               for phase in phases[first + 1:]):
            issues.append("Ideas and refinement must be frozen before prioritization")
    if "idea_generation" in phases and any(
            phase == "briefing" for phase in phases[phases.index("idea_generation") + 1:]):
        issues.append("Advisor briefings must precede idea generation")
    if "synthesis" in phases and any(
            phase != "synthesis" for phase in phases[phases.index("synthesis") + 1:]):
        issues.append("Leader synthesis must follow all other phases")
    ideas = t.get("ideas", [])
    ids = {idea["id"] for idea in ideas}
    if not ideas or len(ids) != len(ideas):
        issues.append("Brainstorm requires a nonempty idea catalogue with unique IDs")
    for idea in ideas:
        if not any(turn["round"] == "idea_generation"
                   and turn["speaker"] == idea["proposer"]
                   and turn.get("role") != "facilitator"
                   and idea["id"] in turn.get("idea_ids", []) for turn in turns):
            issues.append(f"Missing recorded proposal provenance for {idea['id']}")
    for turn in turns:
        if turn["round"] == "idea_generation":
            references = turn.get("idea_ids")
            if (not isinstance(references, list) or not references
                    or any(not isinstance(i, str) or i not in ids for i in references)
                    or len(references) != len(set(references))):
                issues.append("Generation responses must reference their catalogued idea IDs")
    rankings = t.get("rankings", [])
    valid_rankings = (len(rankings) == len(voters)
                      and {r["speaker"] for r in rankings} == voters
                      and all(full_order(r["order"], ids) and r["reason"].strip() for r in rankings))
    if not valid_rankings:
        issues.append("Rankings must include exactly voting participants and every idea once with reasons")
    for ranking in rankings:
        matching = [turn for turn in turns if turn["round"] == "prioritization"
                    and turn["speaker"] == ranking["speaker"] and turn.get("role") != "facilitator"]
        if (len(matching) != 1 or matching[0].get("order") != ranking["order"]
                or matching[0].get("reason") != ranking["reason"]):
            issues.append(f"Missing or inconsistent ranking response for {ranking['speaker']}")
    if any(turn.get("order") is not None for turn in turns
           if turn["round"] == "prioritization" and turn["speaker"] not in voters):
        issues.append("Leader, advisors and archetypes must not submit ranking ballots")
    priority = t.get("prioritization")
    if (not isinstance(priority, dict) or not full_order(priority.get("order"), ids)
            or not priority.get("rationale", "").strip()
            or priority.get("authority") != "recommendation"):
        issues.append("Missing full leader priorities and rationale as an exploration recommendation")
    elif valid_rankings and ideas:
        totals = priority_totals(ideas, rankings)
        scores = [totals[i] for i in priority["order"]]
        if (scores != sorted(scores, reverse=True) or len(set(scores)) != len(scores)):
            if not priority.get("differences", "").strip():
                issues.append("Leader must explain ranking reversals and tie-breaking")
    return issues


def scope_issues(t, people, archetypes):
    s, turns = t["session"], t["turns"]
    issues = []
    seats = set(people) | set(archetypes)
    source = t.get("source")
    if (not isinstance(source, dict) or source.get("kind") not in ("evaluate", "user_direction")
            or any(not isinstance(source.get(key), str) or not source[key].strip()
                   for key in ("idea", "basis", "reference"))):
        issues.append("Scope requires a selected idea and explicit evaluate or user-direction basis")
    if not isinstance(t.get("framing"), str) or not t["framing"].strip():
        issues.append("Missing scope framing")
    for phase, expected in (
            ("briefing", {p for p, vote in people.items() if not vote}),
            ("scoping", seats | {s["leader"]}), ("planning", seats), ("plan_review", seats)):
        spoken = {turn["speaker"] for turn in turns if turn["round"] == phase
                  and turn.get("role") != "facilitator"}
        missing = expected - spoken
        if missing:
            issues.append(f"Missing {phase} responses: {', '.join(sorted(missing))}")
    for phase in ("framing", "synthesis"):
        if not any(turn["speaker"] == s["leader"] and turn["round"] == phase
                   and turn.get("role") == "facilitator" for turn in turns):
            issues.append(f"Missing leader {phase} turn")
    if (any(turn.get("position") is not None or turn.get("order") is not None for turn in turns)
            or any(t.get(field) for field in ("final_votes", "archetype_positions", "rankings"))
            or t.get("decision") is not None):
        issues.append("Scope must not contain approval positions, votes or rankings")
    planning = [turn for turn in turns if turn["round"] == "planning"]
    declared = s.get("planning_rounds")
    numbers = {turn["planning_round"] for turn in planning
               if type(turn.get("planning_round")) is int and turn["planning_round"] > 0}
    actual = {turn["planning_round"] for turn in planning
              if type(turn.get("planning_round")) is int
              and turn.get("role") != "facilitator" and turn["speaker"] in seats}
    if (type(declared) is not int or declared < 2
            or any(type(turn.get("planning_round")) is not int
                   or turn["planning_round"] < 1 for turn in planning)
            or numbers != set(range(1, len(numbers) + 1))
            or len(numbers) != declared or actual != numbers):
        issues.append("At least two numbered planning rounds with recorded seat responses are required")
    phases = [turn["round"] for turn in turns]
    if phases and phases[0] != "framing":
        issues.append("Scope must begin with leader framing")
    if "scoping" in phases and "briefing" in phases[phases.index("scoping") + 1:]:
        issues.append("Advisor briefings must precede scope proposals")
    last_planning = max((i for i, phase in enumerate(phases) if phase == "planning"), default=-1)
    reviewed = {turn["speaker"] for turn in turns[last_planning + 1:]
                if turn["round"] == "plan_review" and turn.get("role") != "facilitator"}
    if seats - reviewed:
        issues.append("Every seat must review the plan after the last planning round")
    if "synthesis" in phases and any(phase != "synthesis"
                                    for phase in phases[phases.index("synthesis") + 1:]):
        issues.append("Leader synthesis must follow all scope discussion and reviews")
    plan = t.get("plan")
    blockers = t.get("blockers", [])
    ids = {b["id"] for b in blockers}
    if len(ids) != len(blockers):
        issues.append("Scope blocker IDs must be unique")
    for blocker in blockers:
        if not any(blocker["id"] in turn.get("blocker_ids", []) for turn in turns):
            issues.append(f"Missing recorded blocker provenance for {blocker['id']}")
    for turn in turns:
        references = turn.get("blocker_ids", [])
        if any(i not in ids for i in references) or len(references) != len(set(references)):
            issues.append("Raised blocker IDs must be retained in the blocker register")
    if plan is None or not plan["phases"]:
        issues.append("Missing complete scope and high-level plan with phases")
        return issues
    names = {p["name"] for p in plan["phases"]}
    if len(names) != len(plan["phases"]) or "start" in names:
        issues.append("Phase names must be unique and must not use the reserved start gate")
    for blocker in blockers:
        if blocker["status"] not in ("open", "resolved"):
            issues.append(f"Invalid blocker status for {blocker['id']}")
        if blocker["gate"] not in names | {"start"}:
            issues.append(f"Unknown blocking gate for {blocker['id']}")
    open_blockers = [b for b in blockers if b["status"] == "open"]
    expected = ("blocked" if any(b["gate"] == "start" for b in open_blockers)
                else "conditional" if open_blockers else "ready_for_review")
    if plan["readiness"] != expected:
        issues.append(f"Scope readiness must be {expected} for the recorded blockers")
    if plan["authority"] != "recommendation":
        issues.append("Scope plan must be a recommendation, not implementation approval")
    return issues


def completion_issues(t):
    s = t["session"]
    issues = []
    if s.get("status") == "incomplete":
        issues.append(s.get("incomplete_reason") or "Run explicitly marked incomplete")
    room = s.get("effective_room")
    snapshot = s.get("team_snapshot")
    if (not isinstance(room, dict) or not isinstance(room.get("leader"), dict)
            or room["leader"].get("profile") != s["leader"]
            or not isinstance(room.get("participants"), list) or not room["participants"]
            or any(not isinstance(p, dict) or not isinstance(p.get("profile"), str)
                   or not p["profile"] or type(p.get("vote")) is not bool
                   for p in room["participants"])):
        return issues + ["Missing full effective room with leader and individual vote/advisor assignments"]
    people = {p["profile"]: p["vote"] for p in room["participants"]}
    archetypes = room.get("facilitation", [])
    if (not isinstance(archetypes, list)
            or any(not isinstance(a, str) or not a for a in archetypes)):
        return issues + ["Invalid effective-room facilitation list"]
    seats = set(people) | set(archetypes)
    if (len(people) != len(room["participants"]) or len(set(archetypes)) != len(archetypes)
            or set(people) & set(archetypes) or s["leader"] in seats):
        issues.append("Effective room contains duplicate or overlapping seats")
    if (not isinstance(snapshot, dict) or snapshot.get("leader") != s["leader"]
            or not isinstance(snapshot.get("participants"), list)
            or any(not isinstance(p, dict) or not isinstance(p.get("profile"), str)
                   or type(p.get("vote")) is not bool for p in snapshot["participants"])):
        issues.append("Missing full team definition snapshot")
    else:
        configured = {p["profile"]: p["vote"] for p in snapshot["participants"]}
        if any(configured.get(p) != vote for p, vote in people.items()):
            issues.append("Effective participants or vote flags disagree with the team snapshot")
        if archetypes != snapshot.get("facilitation", []):
            issues.append("Effective facilitation disagrees with the team snapshot")
    if set(s["roster"]) != seats | {s["leader"]}:
        issues.append("Roster must name every effective seat individually, without placeholders")
    turns = t["turns"]
    if not turns:
        issues.append("No conversation turns recorded")
    if s.get("workflow") == "brainstorm":
        return issues + brainstorm_issues(t, people, archetypes)
    if s.get("workflow") == "scope":
        return issues + scope_issues(t, people, archetypes)
    for phase, expected in (
            ("opening", {p for p, vote in people.items() if vote} | set(archetypes)),
            ("briefing", {p for p, vote in people.items() if not vote}),
            ("deliberation", seats),
            ("final_vote", seats)):
        spoken = {turn["speaker"] for turn in turns if turn["round"] == phase
                  and turn.get("role") != "facilitator"}
        missing = expected - spoken
        if missing:
            issues.append(f"Missing {phase} responses: {', '.join(sorted(missing))}")
    if not any(turn["speaker"] == s["leader"] and turn.get("role") == "facilitator"
               for turn in turns):
        issues.append("Missing leader facilitation turn")
    if not any(turn["speaker"] == s["leader"] and turn["round"] == "opening"
               and turn.get("role") != "facilitator" for turn in turns):
        issues.append("Missing leader opening position")
    debate = [turn for turn in turns if turn["round"] == "deliberation"]
    numbers = {turn["deliberation_round"] for turn in debate
               if type(turn.get("deliberation_round")) is int and turn["deliberation_round"] > 0}
    actual = {turn.get("deliberation_round") for turn in debate
              if type(turn.get("deliberation_round")) is int
              and turn.get("role") != "facilitator" and turn["speaker"] in seats}
    declared = s.get("deliberation_rounds")
    if (any(type(turn.get("deliberation_round")) is not int
            or turn["deliberation_round"] < 1 for turn in debate)
            or type(declared) is not int or declared < 4
            or numbers != set(range(1, len(numbers) + 1))
            or len(numbers) != declared or actual != numbers):
        issues.append("At least four numbered deliberation rounds with recorded seat responses are required")
    for field, expected in (
            ("final_votes", {p for p, vote in people.items() if vote}),
            ("archetype_positions", set(archetypes))):
        votes = t.get(field)
        if (not isinstance(votes, list)
                or any(not isinstance(v, dict) or not isinstance(v.get("speaker"), str)
                       or v.get("position") not in POSITIONS
                       or not isinstance(v.get("reason"), str) or not v["reason"].strip()
                       for v in votes)):
            issues.append(f"Invalid or missing {field}")
            continue
        if len(votes) != len(expected) or {v["speaker"] for v in votes} != expected:
            issues.append(f"{field} must include exactly the assigned seats, with no leader or advisors")
        for vote in votes:
            matching = [turn for turn in turns if turn["round"] == "final_vote"
                        and turn["speaker"] == vote["speaker"] and turn.get("role") != "facilitator"]
            if len(matching) != 1 or matching[0].get("position") != vote["position"]:
                issues.append(f"Missing or inconsistent final response for {vote['speaker']}")
    if any(turn.get("position") is not None for turn in turns
           if turn["round"] == "final_vote" and turn["speaker"] in people
           and not people[turn["speaker"]]):
        issues.append("Advisor final advice must not carry a voting position")
    decision = t.get("decision")
    if (not isinstance(decision, dict) or decision.get("position") not in POSITIONS
            or not isinstance(decision.get("rationale"), str) or not decision["rationale"].strip()):
        issues.append("Missing final leader decision and rationale")
    else:
        votes = t.get("final_votes")
        if isinstance(votes, list) and all(isinstance(v, dict) for v in votes):
            tally = {position.lower(): sum(v.get("position") == position
                                          and v.get("speaker") in people
                                          and people[v["speaker"]] for v in votes)
                     for position in POSITIONS}
            if decision.get("vote_tally") not in (tally, {key.upper(): value for key, value in tally.items()}):
                issues.append("Decision vote tally does not match participant-only final votes")
    return issues


def who(s):
    return SPEAKERS.get(s) or s.title()


def cell(v):
    return (v or "—").replace("|", "/").replace("\n", " ")


def main(path, check=False):
    src = Path(path)
    t = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(t, dict):
        raise ValueError("Transcript must contain a JSON object")
    s = t.get("session", {})
    if not isinstance(s, dict) or any(
            not isinstance(s.get(field), str) or not s[field].strip()
            for field in ("team", "team_name", "leader")):
        raise ValueError("Transcript session must specify team, team_name and leader")
    roster = s.get("roster")
    if (not isinstance(roster, dict) or s["leader"] not in roster
            or any(not isinstance(key, str) or not isinstance(value, str) or not value.strip()
                   for key, value in roster.items())):
        raise ValueError("Transcript session must include a display-name roster containing its leader")
    workflow = s.get("workflow", "evaluate")
    if workflow not in ("evaluate", "convene", "brainstorm", "scope"):
        raise ValueError("Transcript workflow must be evaluate, brainstorm or scope (legacy convene is accepted)")
    rounds = {"brainstorm": BRAINSTORM_ROUNDS, "scope": SCOPE_ROUNDS}.get(workflow, ROUNDS)
    turns = t.get("turns")
    if (not isinstance(turns, list)
            or any(not isinstance(turn, dict) or not isinstance(turn.get("round"), str)
                   or turn["round"] not in rounds
                   or not isinstance(turn.get("speaker"), str) or turn["speaker"] not in roster
                   or not isinstance(turn.get("content"), str) or not turn["content"].strip()
                   for turn in turns)):
        raise ValueError("Transcript turns must have a known round, roster speaker and nonempty content")
    if t.get("framing") is not None and not isinstance(t["framing"], str):
        raise ValueError("Transcript framing must be text or null")
    if t.get("decision") is not None and not isinstance(t["decision"], dict):
        raise ValueError("Transcript decision must be an object or null")
    for field in ("final_votes", "archetype_positions"):
        votes = t.get(field, [])
        if (not isinstance(votes, list)
                or any(not isinstance(vote, dict)
                       or any(vote.get(key) is not None and not isinstance(vote[key], str)
                              for key in ("speaker", "position", "reason", "condition"))
                       for vote in votes)):
            raise ValueError(f"Transcript {field} must be a list of positions with text fields")
    if workflow == "brainstorm":
        ideas = t.get("ideas", [])
        if (not isinstance(ideas, list)
                or any(not isinstance(idea, dict)
                       or any(not isinstance(idea.get(key), str) or not idea[key].strip()
                              for key in ("id", "title", "description", "proposer", "assumptions", "experiment"))
                       or idea["proposer"] not in roster for idea in ideas)):
            raise ValueError("Brainstorm ideas must have nonempty text fields and a roster proposer")
        rankings = t.get("rankings", [])
        if (not isinstance(rankings, list)
                or any(not isinstance(r, dict) or not isinstance(r.get("speaker"), str)
                       or not isinstance(r.get("order"), list)
                       or any(not isinstance(i, str) for i in r["order"])
                       or not isinstance(r.get("reason"), str) for r in rankings)):
            raise ValueError("Brainstorm rankings must contain speaker, idea order and text reason")
        priority = t.get("prioritization")
        if priority is not None and (
                not isinstance(priority, dict) or not isinstance(priority.get("order"), list)
                or any(not isinstance(i, str) for i in priority["order"])
                or any(not isinstance(priority.get(key), str)
                       for key in ("rationale", "differences", "authority"))):
            raise ValueError("Brainstorm prioritization must contain order, rationale, differences and authority")
        if any("idea_ids" in turn and (
                not isinstance(turn["idea_ids"], list)
                or any(not isinstance(i, str) for i in turn["idea_ids"])) for turn in turns):
            raise ValueError("Brainstorm turn idea_ids must be a list of text IDs")
    if workflow == "scope":
        source = t.get("source")
        if source is not None and not isinstance(source, dict):
            raise ValueError("Scope source must be an object or null")
        plan = t.get("plan")
        if plan is not None and (
                not isinstance(plan, dict)
                or any(not isinstance(plan.get(key), str) or not plan[key].strip()
                       for key in (*PLAN_SECTIONS, "authority", "readiness"))
                or not isinstance(plan.get("phases"), list)
                or any(not isinstance(phase, dict)
                       or any(not isinstance(phase.get(key), str) or not phase[key].strip()
                              for key in PHASE_FIELDS) for phase in plan["phases"])):
            raise ValueError("Scope plan must have nonempty outcome fields and a list of complete phases")
        blockers = t.get("blockers", [])
        if (not isinstance(blockers, list)
                or any(not isinstance(b, dict)
                       or any(not isinstance(b.get(key), str) or not b[key].strip()
                              for key in BLOCKER_FIELDS) for b in blockers)):
            raise ValueError("Scope blockers must include impact, mitigation, owner, gate, clearance, evidence and status")
        if any("blocker_ids" in turn and (
                not isinstance(turn["blocker_ids"], list)
                or any(not isinstance(i, str) for i in turn["blocker_ids"])) for turn in turns):
            raise ValueError("Scope turn blocker_ids must be a list of text IDs")
    issues = completion_issues(t)
    if check:
        if issues:
            raise ValueError("Incomplete transcript:\n- " + "\n- ".join(issues))
        print(f"Transcript complete: {src}")
        return
    if issues:
        print("WARNING: Incomplete transcript:\n- " + "\n- ".join(issues), file=sys.stderr)
    SPEAKERS.clear()
    SPEAKERS.update(roster)
    count_key, label = {
        "brainstorm": ("refinement_rounds", "refinement"),
        "scope": ("planning_rounds", "planning"),
    }.get(workflow, ("deliberation_rounds", "deliberation"))
    round_summary = f"{s.get(count_key, 0)} {label} rounds"
    out = [f"# Discussion: {s.get('topic', src.stem)}", "",
           f"*{s.get('date', '')} · {round_summary} · "
           f"simulation of {s['team_name']}, not statements by real people*", "",
           f"**Team:** {s['team']} · **Leader:** {who(s['leader'])}", ""]
    if issues:
        outcome = workflow if workflow in ("brainstorm", "scope") else "team decision"
        out += ["## Incomplete run", "",
                f"**This is a partial record, not a completed {outcome}.**", ""]
        out += [f"- {issue}" for issue in issues]
        out.append("")
    if t.get("framing"):
        out += ["## Framing", "", t["framing"], ""]
    current = None
    for turn in t.get("turns", []):
        r = turn.get("round")
        if r != current:
            current = r
            out += [f"## {rounds.get(r, r)}", ""]
        facilitator = turn.get("role") == "facilitator"
        stamp = ""
        if turn.get("timestamp"):
            stamp = " · " + datetime.fromtimestamp(turn["timestamp"]).strftime("%H:%M")
        pos = f" — **{turn['position']}**" if turn.get("position") else ""
        label = " (facilitating)" if facilitator else ""
        out += [f"### {who(turn.get('speaker', '?'))}{label}{pos}{stamp}", ""]
        if turn.get("prompt") and not facilitator:
            out += [f"> *Asked:* {turn['prompt'].strip()[:600]}", ""]
        out += [turn.get("content", "").strip(), ""]
    for heading, votes in (
            ("Participant votes", t.get("final_votes") or []),
            ("Synthetic perspectives (not participant votes)", t.get("archetype_positions") or [])):
        if not votes:
            continue
        out += [f"## {heading}", "", "| Role | Position | Reason | Would change if |", "|---|---|---|---|"]
        for v in votes:
            out.append(f"| {who(v.get('speaker', ''))} | {cell(v.get('position'))} | "
                       f"{cell(v.get('reason'))} | {cell(v.get('condition'))} |")
        out.append("")
    d = t.get("decision")
    if d:
        heading = "Recorded recommendation (incomplete run)" if issues else "Decision"
        out += [f"## {heading}", "", f"**{d.get('position', '')}**", "", d.get("rationale", ""), ""]
        if d.get("overrule_explanation"):
            out += [f"**Overruled dissent:** {d['overrule_explanation']}", ""]
    if workflow == "brainstorm":
        out += ["## Idea backlog", ""]
        for idea in t.get("ideas", []):
            out += [f"### {idea['id']}: {idea['title']}", "",
                    f"**Proposed by:** {who(idea['proposer'])}", "", idea["description"], "",
                    f"**Assumptions:** {idea['assumptions']}", "",
                    f"**Next experiment:** {idea['experiment']}", ""]
        out += ["## Participant rankings (not approval votes)", "",
                "| Participant | Preferred order | Reason |", "|---|---|---|"]
        for ranking in t.get("rankings", []):
            out.append(f"| {cell(who(ranking['speaker']))} | {cell(', '.join(ranking['order']))} | "
                       f"{cell(ranking['reason'])} |")
        out.append("")
        if not issues:
            totals = priority_totals(t["ideas"], t["rankings"])
            out += ["## Participant Borda totals", "",
                    "Ordinal preferences only; ties are retained. Advisors, archetypes and leader are not tallied.",
                    "", "| Idea | Points |", "|---|---|"]
            for idea_id, points in sorted(totals.items(), key=lambda item: -item[1]):
                out.append(f"| {cell(idea_id)} | {points} |")
            out.append("")
        priority = t.get("prioritization")
        if priority:
            heading = "Recorded priorities (incomplete run)" if issues else "Leader priorities"
            out += [f"## {heading}", "", "**Exploration recommendations, not implementation approval.**", "",
                    " > ".join(priority["order"]), "", priority["rationale"], "",
                    f"**Differences and tie-breaking:** {priority['differences']}", ""]
    if workflow == "scope":
        source = t.get("source")
        if source:
            out += ["## Selected idea and move-forward basis", "",
                    str(source.get("idea", "")), "",
                    f"**Source kind:** {source.get('kind', '')}", "",
                    f"**Reference:** {source.get('reference', '')}", "",
                    str(source.get("basis", "")), ""]
        plan = t.get("plan")
        if plan:
            heading = "Recorded scope and plan (incomplete run)" if issues else "Scope and high-level plan"
            out += [f"## {heading}", "",
                    "**Proposed plan, not implementation approval or a real organizational commitment.**", "",
                    f"**Readiness:** {plan['readiness']}", ""]
            for key, title in PLAN_SECTIONS.items():
                out += [f"### {title}", "", plan[key], ""]
            out += ["### High-level phases", "",
                    "| Phase | Deliverable | Exit criteria | Proposed owner | Timing | Dependencies |",
                    "|---|---|---|---|---|---|"]
            for phase in plan["phases"]:
                out.append("| " + " | ".join(cell(phase[key]) for key in PHASE_FIELDS) + " |")
            out.append("")
        out += ["## Blockers and mitigation strategies", ""]
        for blocker in t.get("blockers", []):
            out += [f"### {blocker['id']}: {blocker['description']}", ""]
            for key in BLOCKER_FIELDS[2:]:
                out += [f"**{key.title()}:** {blocker[key]}", ""]
        if not t.get("blockers"):
            out += ["No blockers recorded" + (" in this partial record." if issues else " after team review."), ""]
    dest = src.with_name(src.name.replace("-transcript.json", "-discussion.md"))
    if dest == src:
        dest = src.with_suffix(".md")
    dest.write_text("\n".join(out), encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript")
    parser.add_argument("--check", action="store_true", help="Require a complete transcript; write nothing")
    args = parser.parse_args()
    try:
        main(args.transcript, check=args.check)
    except (OSError, ValueError) as exc:
        sys.exit(f"ERROR: {exc}")
