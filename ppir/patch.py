"""Apply a Proposal's changes to the IR tree. create -> accepted atom file;
update -> merge+overwrite; deprecate -> flip status, never delete."""
from __future__ import annotations

from pathlib import Path

import yaml

from ppir.atoms import load_atoms
from ppir import registry

_KIND_FOLDER = registry.folders()   # single source: kind-registry.yaml


def _path_for(atom: dict, ir_dir: Path) -> Path:
    """Folder spine = product -> foundations -> platforms/{platform}/{app} ->
    features/{feature} (or shared/). track/kind are atom metadata, NOT the path."""
    scope = atom.get("scope") or {}
    domain = atom["id"].split(".")[0]
    slug = ".".join(atom["id"].split(".")[1:])
    folder = _KIND_FOLDER.get(atom["kind"], atom["kind"].lower())
    app, feature = scope.get("app"), scope.get("feature")
    if domain == "PROD":
        base = ir_dir / "product" / folder
    elif not app:
        base = ir_dir / "foundations" / folder
    elif feature:
        base = ir_dir / "apps" / app / "features" / feature / folder
    else:
        base = ir_dir / "apps" / app / "shared" / folder
    return base / f"{slug}.yaml"


def _existing_path(atom_id: str, ir_dir: Path):
    entry = load_atoms(ir_dir).get(atom_id)
    return entry["path"] if entry else None


def _dump(path: Path, atom: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(atom, allow_unicode=True, sort_keys=False), encoding="utf-8")


def apply(proposal: dict, ir_dir: Path) -> list:
    touched = []
    for change in proposal.get("changes", []):
        op, atom = change["operation"], change["atom"]
        if op == "create":
            atom = {**atom, "status": atom.get("status_on_merge", "accepted")}
            atom.pop("status_on_merge", None)
            _dump(_path_for(atom, ir_dir), atom)
            touched.append(atom["id"])
        elif op == "update":
            path = _existing_path(atom["id"], ir_dir) or _path_for(atom, ir_dir)
            current = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
            _dump(path, {**current, **atom})
            touched.append(atom["id"])
        elif op == "deprecate":
            path = _existing_path(atom["id"], ir_dir)
            if path:
                current = yaml.safe_load(path.read_text(encoding="utf-8"))
                current["status"] = atom.get("status", "deprecated")
                _dump(path, current)
                touched.append(atom["id"])
    return touched
