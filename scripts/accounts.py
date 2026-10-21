#!/usr/bin/env python3
"""List or create customer account workspaces under accounts/.

Usage:
    python3 scripts/accounts.py list
    python3 scripts/accounts.py new <slug>     # slug: lowercase letters, digits, hyphens
    python3 scripts/accounts.py lock <slug>    # lock this session to one account (see account_guard.py)

Each account is a self-contained workspace, git-ignored:
    accounts/<slug>/company/     what the twins know (copied from company-template/)
    accounts/<slug>/questions/   pending questions (+ done/)
    accounts/<slug>/decisions/   memos, transcripts, discussions, outcomes
    accounts/<slug>/memories/    each twin's episodic memory
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACCOUNTS = ROOT / "accounts"


def brief(slug):
    idx = ACCOUNTS / slug / "company" / "index.md"
    if idx.exists():
        m = re.search(r"^account:\s*(.+)$", idx.read_text(encoding="utf-8"), re.M)
        if m:
            return m.group(1).strip()
    return "TBD"


def main():
    cmd = sys.argv[1:2]
    if cmd == ["list"]:
        slugs = sorted(p.name for p in ACCOUNTS.iterdir() if p.is_dir()) if ACCOUNTS.exists() else []
        if not slugs:
            print("No accounts yet. Create one: python3 scripts/accounts.py new <slug>")
        for slug in slugs:
            print(f"{slug}\t{brief(slug)}")
    elif cmd == ["new"] and len(sys.argv) == 3:
        slug = sys.argv[2]
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
            sys.exit("slug must be lowercase letters, digits and hyphens")
        dest = ACCOUNTS / slug
        if dest.exists():
            sys.exit(f"{dest} already exists")
        shutil.copytree(ROOT / "company-template", dest / "company")
        for d in ("questions/done", "decisions", "memories"):
            (dest / d).mkdir(parents=True)
        print(f"Created {dest.relative_to(ROOT)}/ — next, run the company-research skill for this account.")
    elif cmd == ["lock"] and len(sys.argv) == 3:
        slug = sys.argv[2]
        if not (ACCOUNTS / slug).is_dir():
            sys.exit(f"No account '{slug}'. Run: python3 scripts/accounts.py list")
        # The PreToolUse hook (scripts/account_guard.py) records the lock for the session
        # before this runs and refuses a second, different lock.
        print(f"Session locked to '{slug}' ({brief(slug)}). To work on another customer, start a new session.")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
