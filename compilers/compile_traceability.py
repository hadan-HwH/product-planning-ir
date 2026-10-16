"""Compile a Traceability Report (docs/08 §4 — Level 1). Generated output.

For every atom it answers: where did this come from (source/decision) and what
does it affect (reverse index)? It also surfaces the four broken-chain issues a
human reviewer must see even though they cannot read the raw graph:

- orphan          — accepted policy atom that nothing references.
- dangling_source — a Source no atom cites.
- idle_decision   — an accepted Decision that justifies no atom.
- idle_test       — a TestCase that verifies no existing Rule.

Usage: python compilers/compile_traceability.py [--feature warehouses]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT               # noqa: E402
from ppir.atoms import load_atoms, iter_id_refs  # noqa: E402
from compilers import provenance                 # noqa: E402

BANNER = "<!-- DO NOT EDIT — generated from ir/ atoms. Change the atoms, not this file. -->"

# Kinds that are graph roots/leaves — legitimately unreferenced (mirror of
# validators.validate_graph_health._ROOT_KINDS).
_ROOT_KINDS = {
    "Screen", "TestCase", "Supersession", "OpenQuestion",
    "Source", "ClaimSet", "LegacyExtractionMap", "Proposal", "Relation",
    # Decision Evolution Graph: event-log leaves + entry points, not broken chains.
    "DecisionEvent", "DecisionTarget", "DecisionRelation", "CurrentDecisionProjection",
    "ImplementationFact",   # Reality leaf
}
# Kinds whose reference to a Decision makes that Decision "live".
_DECISION_CONSUMERS = {
    "Rule", "Field", "DerivedField", "Action", "Screen", "Component", "Validator",
}


def _reverse_index(atoms: dict) -> dict:
    rev: dict = {}
    for atom_id, entry in atoms.items():
        for ref in {r for r in iter_id_refs(entry["data"]) if r != atom_id}:
            rev.setdefault(ref, []).append(atom_id)
    for k in rev:
        rev[k] = sorted(rev[k])
    return rev


def build(atoms: dict) -> dict:
    rev = _reverse_index(atoms)
    entries: dict = {}
    for atom_id, entry in atoms.items():
        data = entry["data"]
        entries[atom_id] = {
            "kind": data.get("kind"),
            "track": data.get("track"),
            "commitment_level": data.get("commitment_level"),
            "sources": list(data.get("source_refs") or []),
            "decisions": list(data.get("decision_refs") or []),
            "affects": rev.get(atom_id, []),
        }

    issues = {"orphan": [], "dangling_source": [],
              "idle_decision": [], "idle_test": []}

    for atom_id, entry in atoms.items():
        data = entry["data"]
        kind = data.get("kind")
        accepted = data.get("commitment_level") == "accepted"
        referrers = rev.get(atom_id, [])

        if accepted and kind not in _ROOT_KINDS and not referrers:
            issues["orphan"].append(atom_id)

        if kind == "Source" and not referrers:
            issues["dangling_source"].append(atom_id)

        if kind == "Decision" and accepted:
            consumed = any(atoms[r]["data"].get("kind") in _DECISION_CONSUMERS
                           for r in referrers)
            if not consumed:
                issues["idle_decision"].append(atom_id)

        if kind == "TestCase":
            targets = data.get("target_refs") or []
            verifies_rule = any(
                t in atoms and atoms[t]["data"].get("kind") == "Rule"
                for t in targets)
            if not verifies_rule:
                issues["idle_test"].append(atom_id)

    for k in issues:
        issues[k].sort()
    return {"atoms": entries, "issues": issues}


def render(report: dict) -> str:
    L = [BANNER, "# Traceability Report", ""]

    issues = report["issues"]
    total_issues = sum(len(v) for v in issues.values())
    L += ["## 근거 체인 이슈",
          f"- orphan: {len(issues['orphan'])}",
          f"- dangling_source: {len(issues['dangling_source'])}",
          f"- idle_decision: {len(issues['idle_decision'])}",
          f"- idle_test: {len(issues['idle_test'])}",
          ""]
    if total_issues:
        for name, ids in issues.items():
            for i in ids:
                L.append(f"  - **{name}**: `{i}`")
        L.append("")
    else:
        L += ["> 근거 체인 완전 — 끊긴 곳 없음.", ""]

    L += ["## atom별 추적", "",
          "| Atom | Kind | Commit | Source | Decision | Affects |",
          "|---|---|---|---|---|---|"]
    for atom_id in sorted(report["atoms"]):
        e = report["atoms"][atom_id]
        src = ", ".join(f"`{s}`" for s in e["sources"]) or "—"
        dec = ", ".join(f"`{d}`" for d in e["decisions"]) or "—"
        aff = str(len(e["affects"])) if e["affects"] else "0"
        L.append(f"| `{atom_id}` | {e['kind']} | {e['commitment_level']} "
                 f"| {src} | {dec} | {aff} |")
    L.append("")
    return "\n".join(L)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature", default=None,
                        help="filter atoms by scope.feature")
    parser.add_argument("--out", default=None, help="output path")
    args = parser.parse_args()

    atoms = load_atoms(REPO_ROOT / "ir")
    if args.feature:
        atoms = {i: e for i, e in atoms.items()
                 if (e["data"].get("scope") or {}).get("feature") == args.feature}
    report = build(atoms)
    md = provenance.stamp(render(report), "traceability", atoms)

    out = Path(args.out) if args.out else \
        REPO_ROOT / "compiled" / "reports" / "traceability-report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")

    issues = sum(len(v) for v in report["issues"].values())
    print(f"traceability report → {out.relative_to(REPO_ROOT)} "
          f"({len(report['atoms'])} atoms, {issues} chain issue(s))")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
