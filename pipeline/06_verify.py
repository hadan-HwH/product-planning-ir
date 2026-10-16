"""STEP 6 — verify (docs/08): the human-facing verification gate that runs AFTER
merge/graph/compile. It does three things and fails (exit 1) if any hard gate breaks:

  1. audit         — Level 0 hard validators (schema…lifecycle, evidence, graph-health).
  2. traceability  — Level 1 report → compiled/reports/traceability-report.md;
                     hard-fails on a broken근거 chain (orphan/dangling/idle).
  3. tests         — the pytest suite (regression + mutation) if pytest is present.

Advisory ([warn]) findings are printed but do not block. This is Gate 1+3 of the
merge-gate policy; human approval (Gate 6) stays outside the script.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT                        # noqa: E402
from ppir.atoms import load_atoms                        # noqa: E402
from runtime import audit                                # noqa: E402
from compilers import compile_traceability as tr         # noqa: E402
from compilers import provenance                         # noqa: E402


def main() -> int:
    ir = REPO_ROOT / "ir"
    failed = False

    # 1. audit
    violations = audit.run_all(ir)
    hard = [v for v in violations if not v.startswith("[warn]")]
    warn = [v for v in violations if v.startswith("[warn]")]
    if hard:
        failed = True
        print(f"STEP 6 verify — audit FAIL ({len(hard)} hard):")
        for v in hard:
            print(f"  - {v}")
    else:
        print(f"STEP 6 verify — audit PASS (0 hard, {len(warn)} advisory)")

    # 2. traceability
    atoms = load_atoms(ir)
    report = tr.build(atoms)
    out = REPO_ROOT / "compiled" / "reports" / "traceability-report.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(provenance.stamp(tr.render(report), "traceability", atoms), encoding="utf-8")
    chain_issues = sum(len(v) for v in report["issues"].values())
    if chain_issues:
        failed = True
        print(f"STEP 6 verify — traceability FAIL ({chain_issues} broken chain(s)) "
              f"→ {out.relative_to(REPO_ROOT)}")
        for name, ids in report["issues"].items():
            for i in ids:
                print(f"  - {name}: {i}")
    else:
        print(f"STEP 6 verify — traceability PASS "
              f"→ {out.relative_to(REPO_ROOT)} ({len(report['atoms'])} atoms)")

    # 3. tests
    tests_dir = REPO_ROOT / "tests"
    if tests_dir.exists() and any(tests_dir.glob("test_*.py")):
        rc = subprocess.run([sys.executable, "-m", "pytest", str(tests_dir), "-q"],
                            cwd=REPO_ROOT).returncode
        if rc != 0:
            failed = True
            print("STEP 6 verify — tests FAIL")
        else:
            print("STEP 6 verify — tests PASS")

    if failed:
        print("STEP 6 verify — FAIL")
        return 1
    print("STEP 6 verify — PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
