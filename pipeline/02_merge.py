"""STEP 2 — merge: apply every APPROVED proposal into ir/ (transactional:
snapshot -> apply -> audit -> rollback on any hard violation)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT   # noqa: E402
from runtime import merge           # noqa: E402


def main() -> int:
    approved = sorted((REPO_ROOT / "ir/proposals/approved").glob("*.yaml"))
    if not approved:
        print("STEP 2 merge — no approved proposals")
        return 0
    rc = 0
    for p in approved:
        result = merge.run(p.stem)
        if result["merged"]:
            print(f"STEP 2 merge — {p.stem}: MERGED ({len(result['applied'])} atoms)")
        else:
            rc = 1
            print(f"STEP 2 merge — {p.stem}: NOT MERGED ({result['reason']})")
            for v in result.get("violations", []):
                print(f"  - {v}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
