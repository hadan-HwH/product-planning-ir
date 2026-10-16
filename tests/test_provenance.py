"""Compiled-view provenance stamp (P1-2). Deterministic (hash + version); no
generated_at by default so committed compiled/ stays reproducible.
"""
from __future__ import annotations

from compilers import provenance


def _atoms(*datas):
    return {d["id"]: {"path": None, "data": d} for d in datas}


A = _atoms({"id": "SHOP.RULE.x", "kind": "Rule", "commitment_level": "accepted"})
B = _atoms({"id": "SHOP.RULE.x", "kind": "Rule", "commitment_level": "deprecated"})


def test_hash_is_deterministic():
    assert provenance.graph_hash(A) == provenance.graph_hash(A)


def test_hash_changes_when_an_atom_changes():
    assert provenance.graph_hash(A) != provenance.graph_hash(B)


def test_line_carries_compiler_version_and_hash_and_is_html_by_default():
    ln = provenance.line("screen_definition", A)
    assert ln.startswith("<!--") and ln.endswith("-->")
    assert f"compiler=screen_definition@{provenance.COMPILER_VERSION}" in ln
    assert f"source_graph_hash={provenance.graph_hash(A)}" in ln
    assert "generated_at" not in ln          # off by default → reproducible


def test_yaml_style_uses_hash_comment():
    ln = provenance.line("decision_projection", A, style="yaml")
    assert ln.startswith("# provenance:")
    assert "<!--" not in ln


def test_generated_at_is_included_only_when_injected():
    ln = provenance.line("traceability", A, generated_at="2026-07-07T00:00:00Z")
    assert "generated_at=2026-07-07T00:00:00Z" in ln


def test_stamp_prepends_above_existing_banner():
    banner = "<!-- DO NOT EDIT -->"
    out = provenance.stamp(banner + "\n# body", "screen_definition", A)
    lines = out.split("\n")
    assert lines[0].startswith("<!-- provenance:")
    assert lines[1] == banner               # original banner preserved intact
