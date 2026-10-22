#!/usr/bin/env python3
"""Build the packages to send to account managers.

Usage:
    python3 scripts/package.py            # Claude Desktop: one zip per skill in desktop-skill/ + START-HERE.html
    python3 scripts/package.py --code     # Claude Code folder tool: dist/leadership-team-<version>.zip

Desktop package (default): each skill in desktop-skill/, uploaded one by one under
Settings > Capabilities > Skills, plus the how-to guide. No scripts, hooks or folders needed;
one Claude Project per customer is the account boundary.

Code package (--code) contains the tool only: skills, agents, scripts, the company template and the
START-HERE.html guide. It never contains customer data (accounts/*), git history, session
locks or caches. Symlinks (.claude/skills -> .pi/skills) are written as real files so the
zip works on any OS and with any unzip tool.
"""
import datetime
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
FOLDER = "leadership-team"
SKIP_DIRS = {".git", "dist", "__pycache__", "account-locks", "node_modules"}
SKIP_FILES = {".DS_Store"}


def version():
    day = datetime.date.today().isoformat()
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                           text=True, check=True).stdout.strip()
        return f"{day}-{h}"
    except (OSError, subprocess.CalledProcessError):
        return day


def files():
    for dirpath, dirnames, filenames in os.walk(ROOT, followlinks=True):
        rel = Path(dirpath).relative_to(ROOT)
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        if rel.parts[:1] == ("accounts",):
            dirnames[:] = []          # never descend into customer data
            continue
        for name in sorted(filenames):
            if name in SKIP_FILES or name.endswith(".pyc"):
                continue
            yield rel / name


def build_desktop():
    skills_dir = ROOT / "desktop-skill"
    guide = ROOT / "docs" / "START-HERE.html"
    skills = sorted(d for d in skills_dir.iterdir() if (d / "SKILL.md").exists()) if skills_dir.exists() else []
    if not skills or not guide.exists():
        sys.exit("no skills under desktop-skill/ or docs/START-HERE.html is missing")
    DIST.mkdir(exist_ok=True)
    for old in DIST.glob("*.zip"):
        old.unlink()
    for skill in skills:
        out = DIST / f"{skill.name}.zip"
        n = 0
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for src in sorted(p for p in skill.rglob("*") if p.is_file() and p.name not in SKIP_FILES):
                z.write(src, f"{skill.name}/{src.relative_to(skill).as_posix()}")
                n += 1
        print(f"{out.relative_to(ROOT)}  ({n} files, {out.stat().st_size // 1024} KB)")
    (DIST / "START-HERE.html").write_bytes(guide.read_bytes())
    print("dist/START-HERE.html")
    print(f"Send all {len(skills) + 1} files. Recipients read START-HERE.html and upload each zip (without unzipping) as a skill.")


def main():
    if "--code" not in sys.argv[1:]:
        return build_desktop()
    if not (ROOT / "docs" / "START-HERE.html").exists():
        sys.exit("docs/START-HERE.html is missing")
    DIST.mkdir(exist_ok=True)
    out = DIST / f"leadership-team-{version()}.zip"
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in files():
            src = ROOT / rel
            info = zipfile.ZipInfo.from_file(src, f"{FOLDER}/{rel.as_posix()}")
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, src.read_bytes())
            n += 1
        z.write(ROOT / "docs" / "START-HERE.html", f"{FOLDER}/START-HERE.html")
        z.writestr(f"{FOLDER}/accounts/.gitkeep", "")
    print(f"{out.relative_to(ROOT)}  ({n + 1} files, {out.stat().st_size // 1024} KB)")
    print("Send this one file. Recipients open START-HERE.html inside the unzipped folder.")


if __name__ == "__main__":
    main()
