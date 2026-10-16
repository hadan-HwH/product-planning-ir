"""Run all deterministic validators over the IR and report violations.

Usage: python runtime/audit.py --scope all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT                # noqa: E402
from ppir.atoms import load_atoms                # noqa: E402
from validators import (validate_schema, validate_ids, validate_refs,  # noqa: E402
                        validate_typed_refs, validate_lifecycle,
                        validate_file_envelope, validate_evidence,
                        validate_graph_health, validate_decision_projection,
                        validate_product_isolation, validate_deprecated_kinds,
                        validate_drift)


def run_all(ir_dir: Path) -> list:
    atoms = load_atoms(ir_dir)
    violations = []
    violations += validate_file_envelope.run(ir_dir)
    violations += validate_schema.run(ir_dir)
    violations += validate_ids.run(ir_dir)
    violations += validate_refs.check(atoms)
    violations += validate_typed_refs.check(atoms)
    violations += validate_lifecycle.check(atoms)
    violations += validate_evidence.check(atoms)
    violations += validate_graph_health.check(atoms)
    violations += validate_decision_projection.check(atoms)
    violations += validate_product_isolation.check(atoms)
    violations += validate_deprecated_kinds.check(atoms)
    violations += validate_drift.check(atoms)
    return violations


def _hard(violations: list) -> list:
    return [v for v in violations if not v.startswith("[warn]")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", default="all")
    args = parser.parse_args()
    violations = run_all(REPO_ROOT / "ir")
    hard = _hard(violations)
    warn = [v for v in violations if v.startswith("[warn]")]
    for w in warn:
        print(f"  ~ {w}")
    if hard:
        print(f"AUDIT FAIL — {len(hard)} violation(s):")
        for v in hard:
            print(f"  - {v}")
        return 1
    print(f"AUDIT PASS — 0 hard violations" + (f" ({len(warn)} advisory)" if warn else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
