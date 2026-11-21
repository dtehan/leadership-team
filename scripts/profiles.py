#!/usr/bin/env python3
"""Scaffold and structurally check reusable profiles in one selected account.

Examples:
    python3 scripts/profiles.py new <account> <profile> --person "Alex Example" --title "Database Lead" --area technical
    python3 scripts/profiles.py new <account> <profile> --generic --title "Database Lead" --area technical
    python3 scripts/profiles.py check <account> <profile>
    python3 scripts/profiles.py migrate-memory <account> <profile> --team <team>
"""
import argparse
import datetime
import hashlib
import re
import sys
from pathlib import Path
from typing import List

from build_index import docs_in, parse_front_matter
from teams import RESERVED, account_path, inside, profile, slug


def scalar(value: str) -> str:
    value = value.strip()
    if (not value or any(ord(char) < 32 for char in value)
            or any(char in value for char in ('"', "\\"))
            or value[0] == "'" or value[-1] == "'"):
        raise ValueError("Metadata must be non-empty, single-line text without double quotes, "
                         "backslashes, control characters or surrounding single quotes")
    return f'"{value}"'


def directory(account: Path, identifier: str) -> Path:
    slug(identifier)
    if identifier in RESERVED:
        raise ValueError(f"'{identifier}' is a facilitation identifier, not a person profile")
    path = account
    for part in ("company", "profiles", identifier):
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Profile paths must not be symlinks: {path}")
    return inside(account, f"company/profiles/{identifier}")


def create(account: Path, identifier: str, person: str, title: str, areas: List[str],
           generic: bool = False) -> Path:
    target = directory(account, identifier)
    if target.exists():
        raise ValueError(f"Profile '{identifier}' already exists; reuse it or request a refresh")
    if not generic and person.strip().lower() in ("tbd", "archetype"):
        raise ValueError("Use --generic for an unknown person; archetypes are not people")
    name = "TBD" if generic else person.strip()
    title = title.strip()
    name_value, title_value = scalar(name), scalar(title)
    if not areas:
        raise ValueError("At least one company area is required")
    area_list = ", ".join(dict.fromkeys(slug(area) for area in areas))
    template = inside(account, "company/_templates/persona.md")
    headings = re.findall(r"^## .+$", template.read_text(encoding="utf-8"), re.M)
    if "## Snapshot" not in headings or "## Evidence" not in headings:
        raise ValueError("Persona template must include Snapshot and Evidence sections")
    status = "generic" if generic else "pending"
    index = (
        f"---\nperson: {name_value}\ntitle: {title_value}\nareas: [{area_list}]\n"
        f"evidence_status: {status}\n---\n\n# {title} dossier\n\n"
        "Public-professional-source simulation, not statements by the real person.\n"
        f"Evidence status: {status}. A structural check does not verify research.\n"
    )
    source = "Explicit generic role requested by user" if generic else "Not yet researched"
    persona = (
        f"---\ntitle: {scalar(f'Persona - {name}, {title}')}\n"
        f"summary: {scalar(f'Unverified profile scaffold for {title}; person-specific evidence absent.')}\n"
        f"tags: [persona]\nas_of: {datetime.date.today().isoformat()}\n"
        f"source: {scalar(source)}\nconfidence: low\nroles: [{identifier}]\nload: always\n---\n\n"
        "> Simulation only. Unknown sections are not evidence of personal traits.\n\n"
    )
    for heading in headings:
        if heading == "## Snapshot":
            content = (f"Explicit generic {title} role; identity unknown." if generic else
                       f"User-supplied identity: {name}, {title}. Not independently verified.")
        elif heading == "## Evidence":
            content = "No person-specific evidence collected."
        else:
            content = "Unknown; no person-specific evidence collected."
        persona += f"{heading}\n{content}\n\n"
    target.mkdir(exist_ok=False)
    with (target / "index.md").open("x", encoding="utf-8") as file:
        file.write(index)
    with (target / "persona.md").open("x", encoding="utf-8") as file:
        file.write(persona)
    (target / "sources").mkdir()
    return target


def check(account: Path, identifier: str) -> str:
    target = directory(account, identifier)
    profile(account, identifier)
    index = inside(account, f"company/profiles/{identifier}/index.md")
    meta = parse_front_matter(index)
    for field in ("person", "title"):
        value = meta.get(field)
        if not isinstance(value, str):
            raise ValueError(f"{identifier}/index.md: missing scalar {field}")
        scalar(value)
    if not isinstance(meta.get("areas"), list):
        raise ValueError(f"{identifier}/index.md: areas must be an inline list")
    for area in meta["areas"]:
        slug(area)
    persona = inside(account, f"company/profiles/{identifier}/persona.md")
    if not persona.is_file():
        raise ValueError(f"{identifier}: missing persona.md")
    sources = inside(account, f"company/profiles/{identifier}/sources")
    if sources.exists() and not sources.is_dir():
        raise ValueError(f"{identifier}: sources must be a directory")
    for doc in docs_in(target):
        doc = inside(account, doc.relative_to(account).as_posix())
        fields = parse_front_matter(doc)
        for field in ("summary", "as_of", "source", "confidence"):
            if not isinstance(fields.get(field), str) or not fields[field].strip():
                raise ValueError(f"{identifier}/{doc.name}: missing scalar {field}")
        try:
            if datetime.date.fromisoformat(fields["as_of"]).isoformat() != fields["as_of"]:
                raise ValueError("Non-canonical date")
        except ValueError:
            raise ValueError(f"{identifier}/{doc.name}: as_of must be YYYY-MM-DD") from None
        if fields["confidence"] not in ("low", "medium", "high"):
            raise ValueError(f"{identifier}/{doc.name}: invalid confidence")
        for field in ("tags", "roles"):
            values = fields.get(field)
            if not isinstance(values, list) or not values:
                raise ValueError(f"{identifier}/{doc.name}: {field} must be a non-empty inline list")
        if identifier not in fields["roles"]:
            raise ValueError(f"{identifier}/{doc.name}: roles must include {identifier}")
    return meta.get("evidence_status", "legacy (not assessed)")


def migrate_memory(account: Path, identifier: str, team: str) -> bool:
    person = profile(account, identifier)
    source_relative = f"teams/{slug(team)}/memories/{identifier}.md"
    source = inside(account, source_relative)
    if (account / source_relative).is_symlink():
        raise ValueError(f"Team memory must not be a symlink: {source_relative}")
    content = source.read_bytes()
    target = inside(account, person["memory"])
    existing = target.read_bytes() if target.exists() else b""
    prefix = f"<!-- imported-team-memory: {source_relative} sha256: ".encode("utf-8")
    marker = prefix + hashlib.sha256(content).hexdigest().encode("ascii") + b" -->"
    if marker in existing:
        return False
    if prefix in existing:
        raise ValueError("This team's memory changed after import; reconcile it manually "
                         "rather than duplicating history")
    heading = b"" if existing else b"# Simulation memory\n\n## Past Decisions\n\n## Peer Patterns\n"
    entry = (b"\n\n" + marker + f"\n\n## Imported history - team {team}\n\n".encode("utf-8")
             + content + b"\n")
    with target.open("ab") as file:
        file.write(heading + entry)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("new", "check", "migrate-memory"):
        cmd = sub.add_parser(command)
        cmd.add_argument("account")
        cmd.add_argument("profile")
        if command == "new":
            identity = cmd.add_mutually_exclusive_group(required=True)
            identity.add_argument("--person")
            identity.add_argument("--generic", action="store_true")
            cmd.add_argument("--title", required=True)
            cmd.add_argument("--area", action="append", required=True)
        if command == "migrate-memory":
            cmd.add_argument("--team", required=True)
    args = parser.parse_args()
    try:
        account = account_path(args.account)
        if args.command == "new":
            target = create(account, args.profile, args.person or "TBD", args.title,
                            args.area, args.generic)
            print(f"Created {target.relative_to(account)}; "
                  f"evidence_status: {'generic' if args.generic else 'pending'}. "
                  "Research is not complete. Run person-profile.")
        elif args.command == "check":
            status = check(account, args.profile)
            print(f"Structural check passed: {args.profile}; evidence_status: {status}. "
                  "This does not verify research or index freshness.")
        else:
            changed = migrate_memory(account, args.profile, args.team)
            print(f"{'Imported' if changed else 'Already imported'} team memory for "
                  f"{args.profile}; original team file preserved.")
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
