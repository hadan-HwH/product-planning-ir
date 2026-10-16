"""STEP 3 — audit: run all deterministic validators over ir/ (schema, id, ref,
typed_ref, lifecycle). Exit 1 on any hard violation."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT   # noqa: E402
from runtime import audit           # noqa: E402


def main() -> int:
    violations = audit.run_all(REPO_ROOT / "ir")
    hard = audit._hard(violations)
    warn = [v for v in violations if v.startswith("[warn]")]
    for w in warn:
        print(f"  ~ {w}")
    if hard:
        print(f"STEP 3 audit — FAIL ({len(hard)} hard violation(s)):")
        for v in hard:
            print(f"  - {v}")
        return 1
    print(f"STEP 3 audit — PASS (0 hard" + (f", {len(warn)} advisory)" if warn else ")"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
