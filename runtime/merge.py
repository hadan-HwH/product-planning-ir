"""Merge an approved Proposal as a transaction: snapshot ir/, apply, rebuild
graph, audit. On any HARD audit violation, roll back and leave the proposal in
approved/. Only status=approved merges.

Usage: python runtime/merge.py <PROP id>
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT       # noqa: E402
from ppir import patch                  # noqa: E402
from runtime import audit, graph_query  # noqa: E402


def _find(proposal_id: str, repo: Path):
    for status in ("approved", "pending", "rejected", "merged"):
        p = repo / "ir" / "proposals" / status / f"{proposal_id}.yaml"
        if p.exists():
            return status, p
    return None, None


def run(proposal_id: str, repo: Path = REPO_ROOT) -> dict:
    status, path = _find(proposal_id, repo)
    if path is None:
        return {"merged": False, "reason": "proposal not found"}
    body = yaml.safe_load(path.read_text(encoding="utf-8"))
    proposal = body["proposal"] if "proposal" in body else body
    if proposal.get("status") != "approved" or status != "approved":
        return {"merged": False, "reason": "proposal not approved"}

    ir_dir = repo / "ir"
    stage = Path(tempfile.mkdtemp(prefix="ppir-merge-"))
    backup = stage / "ir"
    shutil.copytree(ir_dir, backup)
    try:
        applied = patch.apply(proposal, ir_dir)
        graph = graph_query.build(ir_dir)
        hard = audit._hard(audit.run_all(ir_dir))
        if hard:
            shutil.rmtree(ir_dir)
            shutil.copytree(backup, ir_dir)
            return {"merged": False, "reason": "audit failed post-apply",
                    "violations": hard, "applied": applied}
        graph_query.write(graph, repo / "graph")
        merged_dir = repo / "ir" / "proposals" / "merged"
        merged_dir.mkdir(parents=True, exist_ok=True)
        (ir_dir / "proposals" / status / path.name).rename(merged_dir / path.name)
        return {"merged": True, "applied": applied, "violations": []}
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proposal_id")
    args = parser.parse_args()
    result = run(args.proposal_id)
    if not result["merged"]:
        print(f"NOT MERGED: {result['reason']}")
        for v in result.get("violations", []):
            print(f"  - {v}")
        return 1
    print(f"MERGED — applied {len(result['applied'])} atom(s):")
    for a in result["applied"]:
        print(f"  + {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
