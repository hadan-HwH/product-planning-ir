"""Evidence checks (docs/08 §3 — Level 0). Every accepted atom must carry a
provenance chain; normative rules should name the Decision that justifies them
and a TestCase that verifies them.

- source_required  (HARD): accepted atom must have source_refs or decision_refs.
- decision_required (warn): MUST/MUST_NOT Rule should have decision_refs.
- test_required     (warn): Rule should be covered by a TestCase, or state
                            no_test_reason.

decision_required/test_required are advisory because the legacy pilot legitimately
carries law-from-source rules without a separate Decision and rules not yet
backed by a TestCase. Promote to HARD once the data warrants it.
"""
from __future__ import annotations

_NORMATIVE_STRONG = {"MUST", "MUST_NOT"}


def _tested_rule_ids(atoms: dict) -> set:
    tested: set = set()
    for entry in atoms.values():
        data = entry["data"]
        if data.get("kind") == "TestCase":
            tested.update(data.get("target_refs") or [])
    return tested


def check(atoms: dict) -> list:
    out: list = []
    tested = _tested_rule_ids(atoms)
    for atom_id, entry in atoms.items():
        data = entry["data"]
        kind = data.get("kind")
        accepted = data.get("commitment_level") == "accepted"

        # source_required (HARD)
        if accepted and not data.get("source_refs") and not data.get("decision_refs"):
            out.append(f"{atom_id}: accepted {kind} has neither source_refs "
                       f"nor decision_refs (evidence chain missing)")

        if kind == "Rule" and accepted:
            # decision_required (warn)
            if data.get("normative") in _NORMATIVE_STRONG and not data.get("decision_refs"):
                out.append(f"[warn] {atom_id}: {data.get('normative')} Rule has "
                           f"no decision_refs (unjustified normative claim)")
            # test_required (warn)
            if atom_id not in tested and not data.get("no_test_reason"):
                out.append(f"[warn] {atom_id}: Rule has no TestCase and no "
                           f"no_test_reason")
    return out
