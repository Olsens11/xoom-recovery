#!/usr/bin/env python3
"""Check that project documentation changes roll up to all DIRECTORY.md ancestors.

This is a consistency helper, not a claim that factual content can be validated
without review. Use before publishing a coherent documentation round.
"""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "project-archive"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Check staged changes only (normal pre-commit mode)")
    parser.add_argument("--base", help="Check committed branch changes against this ref")
    args = parser.parse_args()
    if args.staged and args.base:
        parser.error("Specify either --staged or --base, not both.")
    if args.base:
        changed = set(git("diff", "--name-only", "--diff-filter=ACMR", f"{args.base}...HEAD").splitlines())
    elif args.staged:
        changed = set(git("diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines())
    else:
        changed = set(git("diff", "--name-only", "--diff-filter=ACMR", "HEAD").splitlines())
        changed.update(git("ls-files", "--others", "--exclude-standard").splitlines())
    if not changed:
        print("No changed files to check.")
        return 0
    problems = []
    required = set()
    affected = sorted(x for x in changed if x.startswith(PROJECT + "/"))
    for name in affected:
        current = Path(name).parent
        while current.parts and str(current) != ".":
            if not (str(current) == PROJECT or str(current).startswith(PROJECT + "/")):
                break
            path = current / "DIRECTORY.md"
            required.add(path.as_posix())
            if str(current) == PROJECT:
                break
            current = current.parent
    # Changes to root onboarding or project operations also require the project summary.
    crosscut = any(name in ("AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", "README.md")
                   or name.startswith(".github/") or name.startswith("scripts/")
                   for name in changed)
    if crosscut:
        required.add("project-archive/DIRECTORY.md")
    for name in sorted(required):
        if not (ROOT / name).is_file():
            problems.append(f"MISSING authoritative directory record: {name}")
        elif name not in changed:
            problems.append(f"UNUPDATED ancestor in this documentation round: {name}")
    if not affected and any(x.startswith("twrp-research/") for x in changed):
        if "project-archive/DIRECTORY.md" not in changed:
            problems.append("Historical source/research change has no project-root documentation update")
    print(f"Checked {len(changed)} changed files; {len(affected)} project-archive changes; "
          f"{len(required)} ancestor records expected.")
    if problems:
        for msg in problems:
            print("FAIL:", msg)
        print("Update the affected leaf and every intermediate DIRECTORY.md to the project root.")
        return 1
    print("PASS: all required ancestor DIRECTORY.md files are present in this change set.")
    print("This checks presence only. Review contents, evidence, status and supersession manually.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
