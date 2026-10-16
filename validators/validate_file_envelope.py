"""File-envelope guard: every YAML under ir/ must be a dict carrying a top-level
`id`, EXCEPT Proposal wrapper files under ir/proposals/ (which are {proposal:…}).

load_atoms() silently skips id-less files, so a real omission or typo would go
unnoticed. This validator is the audit-level backstop that turns that silence
into a HARD violation.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from ppir.config import REPO_ROOT

_PROPOSALS_DIR = "proposals"   # ir/proposals/** wrappers are the only id-less exception


def _is_proposal_wrapper(rel_parts: tuple) -> bool:
    return len(rel_parts) > 0 and rel_parts[0] == _PROPOSALS_DIR


def check_files(ir_dir: Path) -> list:
    out = []
    for path in sorted(ir_dir.rglob("*.yaml")):
        rel_parts = path.relative_to(ir_dir).parts
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            out.append(f"{path.relative_to(ir_dir.parent)}: YAML parse error ({exc.__class__.__name__})")
            continue
        if _is_proposal_wrapper(rel_parts):
            continue                       # proposal wrappers legitimately lack a top-level id
        if not isinstance(data, dict):
            out.append(f"{path.relative_to(ir_dir.parent)}: not a YAML mapping (expected an atom)")
        elif "id" not in data:
            out.append(f"{path.relative_to(ir_dir.parent)}: missing top-level 'id' (only ir/proposals/ may omit it)")
    return out


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check_files(ir_dir)
