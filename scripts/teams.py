#!/usr/bin/env python3
"""Define and resolve named teams from profiles in one account.

Examples:
    python3 scripts/teams.py profiles <account>
    python3 scripts/teams.py list <account>
    python3 scripts/teams.py new <account> <team> --leader leader --participant cfo --purpose "Strategic decisions"
    python3 scripts/teams.py check <account> <team>
    python3 scripts/teams.py resolve <account> <team>
"""
import argparse
import json
import re
from pathlib import Path

from build_index import parse_front_matter

ROOT = Path(__file__).resolve().parent.parent
ACCOUNTS = ROOT / "accounts"
SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")
ARCHETYPES = ("contrarian", "moonshot")
RESERVED = set(ARCHETYPES)


def slug(value: str) -> str:
    if not isinstance(value, str) or not SLUG.fullmatch(value):
        raise ValueError(f"Invalid slug: {value!r}; use lowercase letters, digits and hyphens")
    return value


def inside(base: Path, relative: str) -> Path:
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Path must be relative and inside the account: {relative}")
    target = (base / path).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        raise ValueError(f"Path escapes the account: {relative}") from None
    return target


def account_path(account: str) -> Path:
    if ACCOUNTS.is_symlink():
        raise ValueError("The accounts directory must not be a symlink")
    identifier = slug(account)
    if (ACCOUNTS / identifier).is_symlink():
        raise ValueError("An account directory must not be a symlink")
    path = inside(ACCOUNTS, identifier)
    if not path.is_dir():
        raise ValueError(f"No account '{account}'. Run the account-scope skill first.")
    return path


def team_path(account: Path, team: str) -> Path:
    return inside(account, f"teams/{slug(team)}")


def profile(account: Path, identifier: str) -> dict:
    slug(identifier)
    if identifier in RESERVED:
        raise ValueError(f"'{identifier}' is a facilitation identifier, not a person profile")
    directory = inside(account, f"company/profiles/{identifier}")
    index = inside(account, f"company/profiles/{identifier}/index.md")
    if not index.is_file():
        raise ValueError(f"Missing profile '{identifier}': company/profiles/{identifier}/index.md")
    meta = parse_front_matter(index)
    name = meta.get("person", "")
    title = meta.get("title", "")
    if not isinstance(name, str) or not isinstance(title, str):
        raise ValueError(f"Profile '{identifier}' must have scalar person and title fields")
    if name.lower() == "archetype":
        raise ValueError(f"Profile '{identifier}' is an archetype, not a person")
    areas = meta.get("areas", [])
    if not isinstance(areas, list):
        raise ValueError(f"Profile '{identifier}' areas must be an inline list")
    evidence = meta.get("evidence_status")
    if evidence is not None and evidence not in ("pending", "thin", "grounded", "generic"):
        raise ValueError(f"Profile '{identifier}' has invalid evidence_status")
    persona = inside(account, f"company/profiles/{identifier}/persona.md")
    memory = inside(account, f"company/profiles/{identifier}/memory.md")
    if (directory / "memory.md").is_symlink():
        raise ValueError(f"Profile memory must not be a symlink: {identifier}/memory.md")
    return {
        "profile": identifier,
        "name": name if name and name != "TBD" else f"Generic {title or identifier}",
        "title": title or identifier,
        "dossier": directory.relative_to(account).as_posix(),
        "memory": memory.relative_to(account).as_posix(),
        "areas": areas,
        "thin": (not persona.is_file() or not name or name == "TBD"
                 or evidence in ("pending", "thin", "generic")),
    }


def validate(account: Path, definition: dict) -> dict:
    if not isinstance(definition, dict):
        raise ValueError("team.json must contain an object")
    allowed = {"name", "purpose", "leader", "participants", "facilitation", "escalates_to"}
    unknown = set(definition) - allowed
    if unknown:
        raise ValueError(f"Unknown team fields: {', '.join(sorted(unknown))}")
    for field in ("name", "purpose"):
        value = definition.get(field)
        if not isinstance(value, str) or not value.strip() or value.strip().startswith("TBD"):
            raise ValueError(f"Team {field} must be a non-empty, non-TBD string")
    leader = profile(account, definition.get("leader"))
    members = definition.get("participants")
    if not isinstance(members, list) or not members:
        raise ValueError("A team needs at least one participant in addition to its leader")
    seen = {leader["profile"]}
    participants = []
    for member in members:
        if not isinstance(member, dict) or set(member) - {"profile", "vote"}:
            raise ValueError("Each participant must contain profile and optional vote fields only")
        person = profile(account, member.get("profile"))
        identifier = person["profile"]
        if identifier in seen:
            raise ValueError(f"Duplicate profile '{identifier}' (the leader cannot also be a participant)")
        seen.add(identifier)
        vote = member.get("vote", True)
        if not isinstance(vote, bool):
            raise ValueError(f"Participant '{identifier}' vote must be true or false")
        participants.append({**person, "vote": vote})
    facilitation = definition.get("facilitation", [])
    if (not isinstance(facilitation, list)
            or any(not isinstance(item, str) or item not in ARCHETYPES for item in facilitation)
            or len(facilitation) != len(set(facilitation))):
        raise ValueError("facilitation must be a unique list containing contrarian and/or moonshot")
    escalation = definition.get("escalates_to")
    if escalation is not None and (not isinstance(escalation, str) or not escalation.strip()):
        raise ValueError("escalates_to must be a non-empty string or null")
    return {"leader": leader, "participants": participants}


def load(account: Path, team: str) -> dict:
    path = inside(account, f"teams/{slug(team)}/team.json")
    if not path.is_file():
        raise ValueError(f"No team '{team}'. Use define-team first.")
    definition = json.loads(path.read_text(encoding="utf-8"))
    validate(account, definition)
    return definition


def resolve(account: Path, team: str, definition: dict, attendees=None) -> dict:
    people = validate(account, definition)
    configured = people["participants"]
    if attendees is not None:
        if len(attendees) != len(set(attendees)):
            raise ValueError("Duplicate attendees")
        unknown = set(attendees) - {p["profile"] for p in configured}
        if unknown:
            raise ValueError(f"Unknown participant attendees: {', '.join(sorted(unknown))}")
        configured = [p for p in configured if p["profile"] in attendees]
        if not configured:
            raise ValueError("At least one participant must attend; the leader always attends")
    people["participants"] = list(configured)
    room = [people["leader"], *people["participants"]]
    roster = {p["profile"]: f"{p['name']} ({p['title']})" for p in room}
    roster.update({a: a.title() for a in definition.get("facilitation", [])})
    warnings = [f"{p['profile']}: thin profile; reason generically without inventing biography"
                for p in room if p["thin"]]
    return {
        "account": account.name,
        "team": slug(team),
        "team_name": definition["name"],
        "workspace": f"teams/{team}",
        "team_snapshot": definition,
        **people,
        "facilitation": definition.get("facilitation", []),
        "escalates_to": definition.get("escalates_to"),
        "roster": roster,
        "warnings": warnings,
    }


def create(account: Path, team: str, definition: dict) -> None:
    validate(account, definition)
    directory = team_path(account, team)
    directory.mkdir(parents=True, exist_ok=False)
    with (directory / "team.json").open("x", encoding="utf-8") as file:
        file.write(json.dumps(definition, indent=2) + "\n")
    for relative in ("questions/done", "decisions"):
        (directory / relative).mkdir(parents=True)
    if definition.get("facilitation"):
        (directory / "memories").mkdir()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("profiles", "list", "new", "check", "resolve"):
        cmd = sub.add_parser(command)
        cmd.add_argument("account")
        if command not in ("profiles", "list"):
            cmd.add_argument("team")
        if command == "new":
            cmd.add_argument("--leader", required=True)
            cmd.add_argument("--participant", action="append", default=[])
            cmd.add_argument("--advisor", action="append", default=[])
            cmd.add_argument("--facilitation", choices=ARCHETYPES, action="append", default=[])
            cmd.add_argument("--escalates-to")
            cmd.add_argument("--name")
            cmd.add_argument("--purpose", required=True)
        if command in ("check", "resolve"):
            cmd.add_argument("--input-team", help="Team declared in the question; must match the selected team")
            cmd.add_argument("--attendee", action="append")
    args = parser.parse_args()
    try:
        account = account_path(args.account)
        if args.command == "profiles":
            base = inside(account, "company/profiles")
            for entry in sorted(base.iterdir()):
                if not entry.is_dir() or not SLUG.fullmatch(entry.name) or entry.name in RESERVED:
                    continue
                person = profile(account, entry.name)
                print(f"{entry.name}\t{person['name']}\t{person['title']}"
                      + ("\tTHIN" if person["thin"] else ""))
        elif args.command == "list":
            base = inside(account, "teams")
            found = False
            for entry in sorted(base.iterdir()) if base.exists() else []:
                if entry.is_dir() and SLUG.fullmatch(entry.name):
                    definition = load(account, entry.name)
                    print(f"{entry.name}\t{definition['name']}\tleader: {definition['leader']}"
                          f"\t{len(definition['participants'])} participant(s)")
                    found = True
            if not found:
                print("No named teams. Use define-team.")
        elif args.command == "new":
            definition = {
                "name": args.name or args.team.replace("-", " ").title(),
                "purpose": args.purpose,
                "leader": args.leader,
                "participants": ([{"profile": p, "vote": True} for p in args.participant]
                                 + [{"profile": p, "vote": False} for p in args.advisor]),
                "facilitation": args.facilitation,
                "escalates_to": args.escalates_to,
            }
            create(account, args.team, definition)
            print(f"Created teams/{args.team}/team.json")
        else:
            if args.input_team is not None and slug(args.input_team) != slug(args.team):
                raise ValueError(f"Team conflict: selected '{args.team}' but question declares '{args.input_team}'")
            room = resolve(account, args.team, load(account, args.team), args.attendee)
            if args.command == "resolve":
                print(json.dumps(room, indent=2))
            else:
                print(f"Team: {room['team_name']}   leader: {room['leader']['profile']}")
                for person in room["participants"]:
                    print(f"- {person['profile']}: {person['name']} ({person['title']})"
                          + (" [voter]" if person["vote"] else " [advisor]"))
                print(f"Facilitation: {', '.join(room['facilitation']) or 'none'}")
                for warning in room["warnings"]:
                    print(f"WARN {warning}")
                print("Team OK" if not room["warnings"] else "Team valid with profile warnings")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()
