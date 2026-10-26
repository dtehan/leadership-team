#!/usr/bin/env python3
"""PreToolUse hook: keep a session inside one customer account.

Claude Code runs this before Read/Edit/Write/Glob/Grep/Bash/NotebookEdit calls and passes
the call as JSON on stdin. Exit 2 (message on stderr) blocks the call.

Lock: when the session runs `python3 scripts/accounts.py lock <slug>`, this hook records
<slug> for the session in .claude/account-locks/<session_id>. From then on any access to
accounts/<other-slug>/ is blocked, and so is any access to accounts/<slug>/ before a lock.
A different customer needs a new session (new session_id), i.e. /clear or a fresh `claude`.

File tools are checked by resolved path. Bash is checked by pattern matching on the command
text, which is best effort: it cannot see paths built at run time (variables, command
substitution). Treat it as a strong guardrail, not a security boundary.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parent.parent).resolve()
ACCOUNTS = ROOT / "accounts"
LOCKS = ROOT / ".claude" / "account-locks"
SLUG = r"[a-z0-9][a-z0-9-]*"
NEW_SESSION = ("Changing customer needs a new session so the twins don't mix accounts. "
               "Start a new session (/clear, or exit and run `claude` again) and name the account.")


def deny(msg):
    print(f"Blocked by account guard: {msg}", file=sys.stderr)
    sys.exit(2)


def locked_slug(session_id):
    f = LOCKS / session_id
    try:
        return f.read_text().strip() or None
    except OSError:
        return None


def prune_locks():
    cutoff = time.time() - 30 * 86400
    try:
        for f in LOCKS.iterdir():
            if f.stat().st_mtime < cutoff:
                f.unlink()
    except OSError:
        pass


def check_slug(slug, lock):
    if lock is None:
        deny(f"no account selected for this session. Run the account-scope skill: pick the "
             f"customer, then `python3 scripts/accounts.py lock <slug>`. (Tried to reach accounts/{slug}.)")
    if slug != lock:
        deny(f"this session is locked to '{lock}' and cannot touch accounts/{slug}. {NEW_SESSION}")


def check_path(raw, cwd, lock, scans):
    """scans=True for Glob/Grep: also refuse paths that would sweep every account."""
    p = Path(raw)
    p = (Path(cwd) / p if not p.is_absolute() else p)
    p = Path(os.path.realpath(p))
    try:
        rel = p.relative_to(ACCOUNTS)
    except ValueError:
        if scans and (p == ROOT or ACCOUNTS.is_relative_to(p)):
            deny("this search would sweep every customer account. Set `path` to a specific "
                 "folder (for example the active account's folder or .pi/).")
        return
    if not rel.parts:
        if scans:
            deny("searching accounts/ would sweep every customer account. Use the active account's folder.")
        return
    if not rel.parts[0].startswith("."):
        check_slug(rel.parts[0], lock)


def check_bash(cmd, lock):
    m = re.search(rf"accounts\.py\s+lock\s+({SLUG})\b", cmd)
    if m:
        return m.group(1)  # handled by caller
    for m in re.finditer(r"accounts/([^\s/'\";&|)]*)", cmd):
        seg = m.group(1)
        if seg.startswith("."):
            continue
        if re.search(r"[*?\[{$`]", seg) or seg == "":
            deny("wildcards or variables under accounts/ could reach other customers. Name the active account explicitly.")
        check_slug(seg, lock)
    if re.search(r"\bcd\s+\S*accounts/?\s*($|[;&|])", cmd):
        deny("don't cd into accounts/; use paths under the active account instead.")
    m = re.search(rf"build_index\.py\s+({SLUG})\b", cmd)
    if m:
        check_slug(m.group(1), lock)
    m = re.search(rf"groups\.py\s+(?:list|new|add|link|check)\s+({SLUG})\b", cmd)
    if m:
        check_slug(m.group(1), lock)
    m = re.search(rf"accounts\.py\s+new\s+({SLUG})\b", cmd)
    if m and lock is not None and m.group(1) != lock:
        deny(f"this session is locked to '{lock}'. {NEW_SESSION}")
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    session = data.get("session_id") or "unknown"
    tool = data.get("tool_name", "")
    ti = data.get("tool_input") or {}
    cwd = data.get("cwd") or str(ROOT)
    lock = locked_slug(session)

    if tool == "Bash":
        cmd = ti.get("command", "")
        want = check_bash(cmd, lock)
        if want:
            if not (ACCOUNTS / want).is_dir():
                deny(f"account '{want}' does not exist. Run `python3 scripts/accounts.py list`.")
            if lock and lock != want:
                deny(f"this session is already locked to '{lock}'. {NEW_SESSION}")
            if not lock:
                LOCKS.mkdir(parents=True, exist_ok=True)
                (LOCKS / session).write_text(want)
                prune_locks()
        return

    scans = tool in ("Glob", "Grep")
    seen = False
    for key in ("file_path", "path", "notebook_path"):
        if ti.get(key):
            seen = True
            check_path(ti[key], cwd, lock, scans)
    rooted = False
    if tool == "Glob" and ti.get("pattern"):
        for m in re.finditer(r"(?:^|/)accounts/([^/]*)", ti["pattern"]):
            if re.search(r"[*?\[{]", m.group(1)) or not m.group(1):
                deny("wildcards under accounts/ could reach other customers.")
            check_slug(m.group(1), lock)
            rooted = rooted or ti["pattern"].lstrip("./").startswith("accounts/")
    if scans and not seen and not rooted:
        check_path(cwd, cwd, lock, scans)


if __name__ == "__main__":
    main()
