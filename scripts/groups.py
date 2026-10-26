#!/usr/bin/env python3
"""Define a working group (e.g. a middle-management team) inside one account, and link member profiles.

Usage:
    python3 scripts/groups.py list  <account>
    python3 scripts/groups.py new   <account> <group>
    python3 scripts/groups.py add   <account> <group> <member> "<Name>" "<Title>" [--reports-to ROLE] [--profile TARGET] [--chair] [--advisor]
    python3 scripts/groups.py link  <account> <group> <member> <TARGET>
    python3 scripts/groups.py check <account> <group>      # also prints the resolved roster

A group lives at accounts/<account>/groups/<group>/ and holds its own roster.md, questions/,
decisions/ and memories/. Company knowledge is shared with the account (company/).

roster.md is the single definition of who is in the group: front-matter (name, purpose, chair,
facilitation, escalates_to) plus a table, one row per member. The `profile` column links the member
to their dossier: blank = accounts/<account>/company/profiles/<member>/ (created as a stub by `add`);
a path inside the account (folder or file); or an http(s) URL not yet researched.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCOUNTS = ROOT / "accounts"
SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")
COLS = ["slug", "name", "title", "reports_to", "profile", "vote"]
MARKER = "<!-- ROSTER -->"
LEADERSHIP = {"leader", "cfo", "cto", "coo", "moonshot", "contrarian"}

ROSTER_TEMPLATE = """---
name: {name}
purpose: TBD — what this group is for and what kinds of decisions it makes
chair: neutral
facilitation: [contrarian]
escalates_to: TBD
---

# {name}

Who is in the group. One row per member. `slug` is the agent name and the dossier folder name.
`reports_to` is a leadership role (`leader`, `cfo`, `cto`, `coo`) or another member's slug.
`profile` links the member to their dossier: blank = `company/profiles/{{slug}}/`; or a path inside this
account (folder or file); or an http(s) URL (not yet researched). `vote` = yes | no (no = advisor).

`chair` (front-matter) is a member slug, or `neutral` for a facilitator who is not a member.
`facilitation` lists archetypes added to the room: `contrarian`, `moonshot` (or leave empty).

{marker}
| slug | name | title | reports_to | profile | vote |
|---|---|---|---|---|---|
"""


def die(msg):
    sys.exit(msg)


def paths(account, group=None):
    if not SLUG.fullmatch(account) or not (ACCOUNTS / account).is_dir():
        die(f"No account '{account}'. Run: python3 scripts/accounts.py list")
    acc = ACCOUNTS / account
    if group is None:
        return acc, None
    if not SLUG.fullmatch(group):
        die("group must be lowercase letters, digits and hyphens")
    return acc, acc / "groups" / group


def parse(roster_path):
    text = roster_path.read_text(encoding="utf-8")
    meta, members = {}, []
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
            if kv:
                v = kv.group(2).strip()
                if v.startswith("[") and v.endswith("]"):
                    v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
                meta[kv.group(1)] = v
    after = text.split(MARKER, 1)[1] if MARKER in text else ""
    for line in after.splitlines():
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        cells += [""] * (len(COLS) - len(cells))
        row = dict(zip(COLS, cells))
        if row["slug"] and row["slug"] != "slug":
            members.append(row)
    return meta, text, members


def write_members(roster_path, text, members):
    head = text.split(MARKER, 1)[0]
    lines = [MARKER, "| " + " | ".join(COLS) + " |", "|" + "---|" * len(COLS)]
    lines += ["| " + " | ".join(m.get(c, "") for c in COLS) + " |" for m in members]
    roster_path.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


def need_group(account, group):
    acc, g = paths(account, group)
    r = g / "roster.md"
    if not r.exists():
        die(f"No group '{group}' in {account}. Create it: python3 scripts/groups.py new {account} {group}")
    return acc, g, r


def dossier_target(acc, member):
    """Resolve a member's profile link -> (kind, detail)."""
    p = member["profile"]
    if re.match(r"https?://", p):
        return "url", p
    rel = p or f"company/profiles/{member['slug']}"
    t = acc / rel
    if not t.exists():
        return "missing", rel
    if t.is_dir():
        docs = [d for d in t.glob("*.md") if d.name != "index.md"]
        persona = (t / "persona.md").exists()
        return ("dossier" if persona else "stub"), f"{rel} ({len(docs)} document(s){'' if persona else ', no persona.md'})"
    return "file", rel


def cmd_list(account):
    acc, _ = paths(account)
    base = acc / "groups"
    found = sorted(p for p in base.iterdir() if (p / "roster.md").exists()) if base.exists() else []
    if not found:
        print(f"No groups in {account}. Create one: python3 scripts/groups.py new {account} <group>")
    for g in found:
        meta, _, members = parse(g / "roster.md")
        print(f"{g.name}\t{meta.get('name', '')}\t{len(members)} member(s)")


def cmd_new(account, group):
    acc, g = paths(account, group)
    if g.exists():
        die(f"{g.relative_to(ROOT)} already exists")
    for d in ("questions/done", "decisions", "memories"):
        (g / d).mkdir(parents=True)
    (g / "roster.md").write_text(
        ROSTER_TEMPLATE.format(name=group.replace("-", " ").title(), marker=MARKER), encoding="utf-8")
    print(f"Created {g.relative_to(ROOT)}/ — next, run the define-group skill to fill in the roster.")


def cmd_add(account, group, args):
    flags = {"--reports-to": None, "--profile": None}
    chair = advisor = False
    pos, i = [], 0
    while i < len(args):
        a = args[i]
        if a in flags and i + 1 < len(args):
            flags[a] = args[i + 1]
            i += 2
            continue
        if a == "--chair":
            chair = True
        elif a == "--advisor":
            advisor = True
        else:
            pos.append(a)
        i += 1
    if len(pos) != 3:
        die(__doc__)
    slug, name, title = pos
    if not SLUG.fullmatch(slug) or slug in LEADERSHIP:
        die("member slug must be kebab-case and not a leadership role name (leader, cfo, cto, coo, moonshot, contrarian)")
    acc, g, r = need_group(account, group)
    meta, text, members = parse(r)
    if any(m["slug"] == slug for m in members):
        die(f"'{slug}' is already in {group}. Use `link` to change their profile.")
    row = {"slug": slug, "name": name, "title": title, "reports_to": flags["--reports-to"] or "",
           "profile": flags["--profile"] or "", "vote": "no" if advisor else "yes"}
    members.append(row)
    write_members(r, text, members)
    if chair:
        text = r.read_text(encoding="utf-8")
        text = re.sub(r"^chair:.*$", f"chair: {slug}", text, count=1, flags=re.M)
        r.write_text(text, encoding="utf-8")
    if not row["profile"]:  # default dossier folder: create a stub so the member can be loaded
        d = acc / "company" / "profiles" / slug
        if not d.exists():
            d.mkdir(parents=True)
            (d / "index.md").write_text(
                f"---\nperson: {name}\ntitle: {title}\ntype: member\nareas: [strategy, technical, financial]\n"
                f"focus: Member of {group}\n---\n\n# {title} dossier\n\nDocuments about {name}. Start with `persona.md` "
                "(copy `company/_templates/persona.md`). Public professional information only.\n", encoding="utf-8")
    print(f"Added {slug} ({title}) to {group}" + (" as chair" if chair else "") + ("" if row["vote"] == "yes" else " as advisor (no vote)"))
    print(f"Next: python3 scripts/groups.py check {account} {group}")


def cmd_link(account, group, member, target):
    acc, g, r = need_group(account, group)
    meta, text, members = parse(r)
    row = next((m for m in members if m["slug"] == member), None)
    if row is None:
        die(f"'{member}' is not in {group}")
    if not re.match(r"https?://", target) and not (acc / target).exists():
        die(f"{target} does not exist inside {account}. Give a path relative to accounts/{account}/ or an http(s) URL.")
    row["profile"] = target
    write_members(r, text, members)
    print(f"Linked {member} -> {target}")


def cmd_check(account, group):
    acc, g, r = need_group(account, group)
    meta, _, members = parse(r)
    problems = []
    slugs = [m["slug"] for m in members]
    print(f"Group: {meta.get('name', group)}   chair: {meta.get('chair')}   facilitation: {meta.get('facilitation')}")
    print(f"Purpose: {meta.get('purpose')}   escalates to: {meta.get('escalates_to')}\n")
    if not members:
        problems.append("roster has no members")
    if meta.get("purpose", "TBD").startswith("TBD"):
        problems.append("roster purpose is still TBD")
    chair = meta.get("chair", "neutral")
    if chair != "neutral" and chair not in slugs:
        problems.append(f"chair '{chair}' is not in the roster")
    if len(slugs) != len(set(slugs)):
        problems.append("duplicate member slugs")
    for m in members:
        kind, detail = dossier_target(acc, m)
        rt = m["reports_to"]
        if rt and rt not in slugs and not (acc / "company" / "profiles" / rt / "index.md").exists():
            problems.append(f"{m['slug']}: reports_to '{rt}' is neither a member nor a leadership profile in this account")
        if kind == "missing":
            problems.append(f"{m['slug']}: profile link {detail} does not exist")
        elif kind in ("stub", "url"):
            problems.append(f"{m['slug']}: profile is {'only a link' if kind == 'url' else 'a stub'} — research it (company-research) or the twin will be generic")
        vote = "votes" if m["vote"].lower() != "no" else "advisor"
        print(f"- {m['slug']:<22} {m['title']:<34} {vote:<8} reports to {rt or '-':<8} profile: {kind} {detail}")
    print()
    for p in problems:
        print("WARN", p)
    print(f"{len(problems)} warning(s)" if problems else "Roster OK")


def main():
    a = sys.argv[1:]
    try:
        if a[:1] == ["list"] and len(a) == 2:
            cmd_list(a[1])
        elif a[:1] == ["new"] and len(a) == 3:
            cmd_new(a[1], a[2])
        elif a[:1] == ["add"] and len(a) >= 6:
            cmd_add(a[1], a[2], a[3:])
        elif a[:1] == ["link"] and len(a) == 5:
            cmd_link(*a[1:])
        elif a[:1] == ["check"] and len(a) == 3:
            cmd_check(a[1], a[2])
        else:
            die(__doc__)
    except BrokenPipeError:
        pass


if __name__ == "__main__":
    main()
