"""Load kind-registry.yaml and expose the per-kind metadata that used to be
duplicated across ppir.config.yaml, ppir/patch.py, and the validators.

Deliberately imports nothing from ppir.config to avoid an import cycle
(config.py imports this module).
"""
from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_registry(repo_root: Path = REPO_ROOT) -> dict:
    data = yaml.safe_load((repo_root / "kind-registry.yaml").read_text(encoding="utf-8"))
    return data["kinds"]


KINDS = load_registry()


def token_map() -> dict:
    """{token -> kind}. Was ppir.config.yaml kind_token_map."""
    return {spec["token"]: kind for kind, spec in KINDS.items() if "token" in spec}


def folders() -> dict:
    """{kind -> folder}. Was ppir/patch.py _KIND_FOLDER."""
    return {kind: spec["folder"] for kind, spec in KINDS.items() if "folder" in spec}


def lifecycle_matrix() -> dict:
    """{kind -> (required_track, {allowed_commitment_levels})}. Was _MATRIX.
    Kinds without a `lifecycle:` block are omitted (lifecycle-unconstrained)."""
    out = {}
    for kind, spec in KINDS.items():
        lc = spec.get("lifecycle")
        if lc:
            out[kind] = (lc["track"], set(lc["commitment_levels"]))
    return out


def typed_ref_rules() -> list:
    """[(kind, dotted_field_path, {allowed_kinds})]. Was _RULES."""
    out = []
    for kind, spec in KINDS.items():
        for path, allowed in (spec.get("typed_refs") or {}).items():
            out.append((kind, path, set(allowed)))
    return out


def schema_files() -> dict:
    """{kind -> schema filename} for kinds that declare one (non-reserved)."""
    return {kind: spec["schema"] for kind, spec in KINDS.items() if "schema" in spec}


def reserved_kinds() -> set:
    return {kind for kind, spec in KINDS.items() if spec.get("reserved")}


def deprecated_kinds() -> set:
    """Kinds kept for back-compat but not to be authored anew (plan9)."""
    return {kind for kind, spec in KINDS.items() if spec.get("deprecated")}
