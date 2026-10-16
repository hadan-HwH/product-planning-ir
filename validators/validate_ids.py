"""Check atom IDs: format, domain, kind-token agreement, duplicate files."""
from __future__ import annotations

from pathlib import Path

import yaml

from ppir.config import ID_RE, DOMAINS, KIND_TOKEN_MAP, REPO_ROOT
from ppir.atoms import load_atoms


def check(atoms: dict) -> list:
    out = []
    for atom_id, entry in atoms.items():
        data = entry["data"]
        if not ID_RE.match(atom_id):
            out.append(f"{atom_id}: bad ID format")
            continue
        domain, token = atom_id.split(".")[0], atom_id.split(".")[1]
        if domain not in DOMAINS:
            out.append(f"{atom_id}: unknown domain {domain!r}")
        expected = KIND_TOKEN_MAP.get(token)
        if expected is None:
            out.append(f"{atom_id}: unknown kind token {token!r}")
        elif data.get("kind") != expected:
            out.append(f"{atom_id}: kind token {token!r} expects {expected!r} "
                       f"but atom.kind={data.get('kind')!r}")
    return out


def check_duplicate_files(ir_dir: Path) -> list:
    seen, out = {}, []
    for path in sorted(ir_dir.rglob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "id" not in data:
            continue
        if data["id"] in seen:
            out.append(f"{data['id']}: duplicate ID in {path} and {seen[data['id']]}")
        seen[data["id"]] = path
    return out


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check(load_atoms(ir_dir)) + check_duplicate_files(ir_dir)
