"""Validate each atom against its merged (envelope + kind) schema, and detect
unknown properties (typo guard) per schema_mode."""
from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from ppir import schemas
from ppir.config import REPO_ROOT, schema_mode
from ppir.atoms import load_atoms


def check_atom(atom: dict, envelope: dict, kinds: dict) -> list:
    kind = atom.get("kind")
    if kind not in kinds:
        return [f"{atom.get('id', '<no id>')}: unknown kind {kind!r}"]
    schema = schemas.merged_schema(envelope, kinds[kind])
    validator = Draft202012Validator(schema)
    out = []
    for err in sorted(validator.iter_errors(atom), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) or "<root>"
        out.append(f"{atom.get('id', '<no id>')}: schema[{loc}] {err.message}")
    # unknown-property detection
    allowed = schemas.allowed_props(envelope, kinds[kind])
    for k in atom:
        if k not in allowed:
            msg = f"{atom.get('id')}: unknown property '{k}' (not in {kind} schema)"
            out.append(msg if schema_mode() == "strict" else f"[warn] {msg}")
    return out


def run(ir_dir: Path = REPO_ROOT / "ir", schemas_dir: Path = REPO_ROOT / "schemas") -> list:
    envelope, kinds = schemas.load_schemas(schemas_dir)
    violations = []
    for entry in load_atoms(ir_dir).values():
        violations.extend(check_atom(entry["data"], envelope, kinds))
    return violations
