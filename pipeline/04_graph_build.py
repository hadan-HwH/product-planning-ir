"""STEP 4 — graph: build dependency/reverse indexes into graph/ from atom refs."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT   # noqa: E402
from runtime import graph_query     # noqa: E402


def main() -> int:
    graph = graph_query.build(REPO_ROOT / "ir")
    graph_query.write(graph, REPO_ROOT / "graph")
    print(f"STEP 4 graph — built index for {len(graph['atom_index'])} atoms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
