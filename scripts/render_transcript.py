#!/usr/bin/env python3
"""Render a deliberation transcript (JSON) as a readable markdown discussion.

Usage: python3 scripts/render_transcript.py decisions/2026-10-21-topic-transcript.json
Writes decisions/2026-10-21-topic-discussion.md next to it.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

NAMES = {"leader": "CEO (Leader)", "cfo": "CFO", "cto": "CTO", "coo": "COO",
         "moonshot": "Moonshot", "contrarian": "Contrarian"}
ROUNDS = {"briefing": "Guest briefing", "opening": "Opening round", "deliberation": "Deliberation", "final_vote": "Final vote"}


def who(s):
    return NAMES.get(s, s.title())


def cell(v):
    return (v or "—").replace("|", "/").replace("\n", " ")


def main(path):
    src = Path(path)
    t = json.loads(src.read_text(encoding="utf-8"))
    s = t.get("session", {})
    out = [f"# Discussion: {s.get('topic', src.stem)}", "",
           f"*{s.get('date', '')} · {s.get('deliberation_rounds', 0)} deliberation rounds · "
           "simulation of the leadership team, not statements by real people*", ""]
    if t.get("framing"):
        out += ["## Framing", "", t["framing"], ""]
    current = None
    for turn in t.get("turns", []):
        r = turn.get("round")
        if r != current:
            current = r
            out += [f"## {ROUNDS.get(r, r)}", ""]
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
    votes = t.get("final_votes") or []
    if votes:
        out += ["## Final vote", "", "| Role | Position | Reason | Would change if |", "|---|---|---|---|"]
        for v in votes:
            out.append(f"| {who(v.get('speaker', ''))} | {cell(v.get('position'))} | "
                       f"{cell(v.get('reason'))} | {cell(v.get('condition'))} |")
        out.append("")
    d = t.get("decision")
    if d:
        out += ["## Decision", "", f"**{d.get('position', '')}**", "", d.get("rationale", ""), ""]
        if d.get("overrule_explanation"):
            out += [f"**Overruled dissent:** {d['overrule_explanation']}", ""]
    dest = src.with_name(src.name.replace("-transcript.json", "-discussion.md"))
    if dest == src:
        dest = src.with_suffix(".md")
    dest.write_text("\n".join(out), encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
