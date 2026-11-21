#!/usr/bin/env python3
"""Build a Copilot CLI workspace ZIP without traversing customer data.

Usage:
    python3 scripts/package.py
    python3 scripts/package.py --output-dir <directory>

Only explicitly selected shared assets are packaged. Skill and template resources are
Markdown files; customer folders, local state, symlinks and unrelated files are not inputs.
"""
import argparse
import datetime
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
FOLDER = "leadership-team"
SHARED_FILES = (
    ".github/copilot-instructions.md",
    ".github/agents/leadership-specialist.agent.md",
    ".gitignore", "README.md", "LICENSE", "docs/TEAMS-USER-GUIDE.md",
    "scripts/accounts.py", "scripts/teams.py", "scripts/profiles.py",
    "scripts/build_index.py", "scripts/render_transcript.py", "scripts/package.py",
    "tests/test_package.py", "tests/test_workspace.py", "tests/test_teams.py",
    "tests/test_profiles.py",
)
RESOURCE_DIRS = (".github/skills", "company-template")


def version():
    day = datetime.date.today().isoformat()
    try:
        h = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                           text=True, check=True).stdout.strip()
        return f"{day}-{h}"
    except (OSError, subprocess.CalledProcessError):
        return day


def checked(path):
    for candidate in (path, *path.parents):
        if candidate == ROOT:
            break
        if candidate.is_symlink():
            raise ValueError(f"Package input must not be a symlink: {candidate}")
    return path


def resources(directory):
    for path in sorted(checked(directory).iterdir()):
        checked(path)
        if path.name.startswith(".") or path.name == "__pycache__":
            continue
        if path.is_dir():
            yield from resources(path)
        elif path.suffix == ".md":
            yield path.relative_to(ROOT)


def files():
    for name in SHARED_FILES:
        path = checked(ROOT / name)
        if not path.is_file():
            raise ValueError(f"Required package input is missing: {name}")
        yield Path(name)
    for name in RESOURCE_DIRS:
        yield from resources(ROOT / name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DIST)
    args = parser.parse_args()
    try:
        inputs = list(files())
        output = args.output_dir.resolve()
        customer_root = ROOT.resolve() / "accounts"
        if output == customer_root or customer_root in output.parents:
            parser.error("output directory must be outside customer workspaces")
        output.mkdir(parents=True, exist_ok=True)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    out = output / f"leadership-team-{version()}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in inputs:
            src = ROOT / rel
            info = zipfile.ZipInfo.from_file(src, f"{FOLDER}/{rel.as_posix()}")
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, src.read_bytes())
    print(f"{out}  ({len(inputs)} files, {out.stat().st_size // 1024} KB)")
    print("Extract the ZIP, read README.md, then run copilot from the extracted folder.")


if __name__ == "__main__":
    main()
