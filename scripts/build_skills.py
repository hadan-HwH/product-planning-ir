"""Distribute shared skill references from a single source (P1-4).

`skills-shared/` holds the canonical copy of each reference file that is shared
across skills (ppir-core.md, runtime-commands.md, review-packet-template.md).
Each skill needs its own physical copy under `references/` (a skill is loaded
from its own directory at runtime), so those copies are GENERATED from the
single source by this script — edit `skills-shared/`, never the copies.

Distribution is presence-based: for each skill, any reference file whose name
matches a shared file is refreshed from the canonical copy. To give a new skill
a shared reference, create the file once (any content) and re-run build.

Usage:
    python scripts/build_skills.py           # write: refresh every copy from source
    python scripts/build_skills.py --check    # verify in sync; exit 1 on drift (CI/verify)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = REPO_ROOT / "skills-shared"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"


def _shared_files() -> dict:
    return {p.name: p for p in sorted(SHARED_DIR.glob("*.md"))}


def _targets(shared: dict) -> list:
    """(skill_name, filename, dest_path, canonical_path) for every existing copy."""
    out = []
    for skill in sorted(SKILLS_DIR.glob("*/")):
        refs = skill / "references"
        if not refs.is_dir():
            continue
        for name, canonical in shared.items():
            dest = refs / name
            if dest.exists():
                out.append((skill.name, name, dest, canonical))
    return out


def check() -> int:
    shared = _shared_files()
    drift = []
    for skill, name, dest, canonical in _targets(shared):
        if dest.read_text(encoding="utf-8") != canonical.read_text(encoding="utf-8"):
            drift.append(f"{skill}/references/{name}")
    if drift:
        print(f"SKILLS DRIFT — {len(drift)} copy(ies) differ from skills-shared/:")
        for d in drift:
            print(f"  - {d}")
        print("Run `python scripts/build_skills.py` to resync.")
        return 1
    print(f"skills in sync — {len(_targets(shared))} shared copy(ies) match skills-shared/")
    return 0


def build() -> int:
    shared = _shared_files()
    written = 0
    for skill, name, dest, canonical in _targets(shared):
        text = canonical.read_text(encoding="utf-8")
        if dest.read_text(encoding="utf-8") != text:
            dest.write_text(text, encoding="utf-8")
            written += 1
    print(f"skills built — refreshed {written} copy(ies) from skills-shared/ "
          f"({len(_targets(shared))} total)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="verify copies are in sync; exit 1 on drift")
    args = parser.parse_args()
    return check() if args.check else build()


if __name__ == "__main__":
    raise SystemExit(main())
