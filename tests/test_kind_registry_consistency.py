"""kind-registry.yaml is the single source of truth for per-kind metadata
(P1-1). These checks lock the invariants that used to drift when the same
information lived in ppir.config.yaml, patch.py, and the validators.
"""
from __future__ import annotations

import yaml

from ppir import registry
from ppir.config import REPO_ROOT

SCHEMAS_DIR = REPO_ROOT / "schemas"


def _schema_kinds() -> set:
    kinds = set()
    for path in SCHEMAS_DIR.glob("*.schema.yaml"):
        if path.name == "_envelope.schema.yaml":
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        kinds.add(data["x-kind"])
    return kinds


def test_tokens_are_unique():
    tokens = [spec["token"] for spec in registry.KINDS.values() if "token" in spec]
    assert len(tokens) == len(set(tokens)), "duplicate token in kind-registry.yaml"


def test_every_non_reserved_kind_has_an_existing_schema():
    reserved = registry.reserved_kinds()
    for kind, spec in registry.KINDS.items():
        if kind in reserved:
            assert "schema" not in spec, f"{kind} is reserved but declares a schema"
            continue
        schema = spec.get("schema")
        assert schema, f"{kind} has no schema and is not marked reserved"
        assert (SCHEMAS_DIR / schema).exists(), f"{kind}: schema file {schema} missing"


def test_schema_xkind_matches_registry_declaration():
    """Every kind's declared schema file must actually carry that x-kind."""
    for kind, schema in registry.schema_files().items():
        data = yaml.safe_load((SCHEMAS_DIR / schema).read_text(encoding="utf-8"))
        assert data["x-kind"] == kind, (
            f"{schema} declares x-kind={data['x-kind']!r} but registry maps it to {kind!r}")


def test_every_schema_kind_is_registered():
    """No schema file may exist for a kind absent from the registry (drift guard)."""
    missing = _schema_kinds() - set(registry.KINDS)
    assert not missing, f"schemas without a registry entry: {sorted(missing)}"


def test_non_reserved_kinds_have_a_folder():
    """Every kind that can be created as an atom needs a storage folder, except
    Proposal (a wrapper stored under ir/proposals/, never via _path_for)."""
    reserved = registry.reserved_kinds()
    folders = registry.folders()
    for kind, spec in registry.KINDS.items():
        if kind in reserved or kind == "Proposal":
            continue
        assert kind in folders, f"{kind} has no folder in kind-registry.yaml"


def test_typed_ref_targets_are_known_kinds():
    known = set(registry.KINDS)
    for kind, path, allowed in registry.typed_ref_rules():
        assert kind in known, f"typed_ref rule on unknown kind {kind}"
        unknown = allowed - known
        assert not unknown, f"{kind}.{path} allows unknown kinds {sorted(unknown)}"


def test_lifecycle_tracks_and_levels_are_valid():
    from ppir.config import TRACKS, COMMITMENT_LEVELS
    for kind, (track, levels) in registry.lifecycle_matrix().items():
        assert track in TRACKS, f"{kind}: unknown track {track!r}"
        bad = levels - COMMITMENT_LEVELS
        assert not bad, f"{kind}: unknown commitment_levels {sorted(bad)}"
