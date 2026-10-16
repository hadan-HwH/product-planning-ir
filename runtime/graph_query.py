"""Build dependency/reverse indexes from atom refs and query them.

Usage:
    python runtime/graph_query.py build
    python runtime/graph_query.py deps  <atom_id>
    python runtime/graph_query.py reverse <atom_id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT                # noqa: E402
from ppir.atoms import load_atoms, iter_id_refs  # noqa: E402


def build(ir_dir: Path) -> dict:
    atoms = load_atoms(ir_dir)
    atom_index, dependency_graph, reverse_index = {}, {}, {}
    for atom_id, entry in atoms.items():
        data = entry["data"]
        atom_index[atom_id] = {
            "kind": data.get("kind"),
            "track": data.get("track"),
            "status": data.get("status"),
            "path": str(entry["path"].relative_to(ir_dir.parent)),
        }
        refs = sorted({r for r in iter_id_refs(data) if r != atom_id})
        dependency_graph[atom_id] = refs
        for ref in refs:
            reverse_index.setdefault(ref, []).append(atom_id)
    for ref in reverse_index:
        reverse_index[ref].sort()
    return {"atom_index": atom_index, "dependency_graph": dependency_graph,
            "reverse_index": reverse_index}


def write(graph: dict, graph_dir: Path) -> None:
    graph_dir.mkdir(parents=True, exist_ok=True)
    for name in ("atom_index", "dependency_graph", "reverse_index"):
        (graph_dir / f"{name.replace('_', '-')}.json").write_text(
            json.dumps(graph[name], ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8")


def deps(graph: dict, atom_id: str) -> list:
    return graph["dependency_graph"].get(atom_id, [])


def reverse(graph: dict, atom_id: str) -> list:
    return graph["reverse_index"].get(atom_id, [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "deps", "reverse"])
    parser.add_argument("atom_id", nargs="?")
    args = parser.parse_args()
    graph = build(REPO_ROOT / "ir")
    if args.command == "build":
        write(graph, REPO_ROOT / "graph")
        print(f"graph built: {len(graph['atom_index'])} atoms")
    elif args.command == "deps":
        for r in deps(graph, args.atom_id):
            print(r)
    elif args.command == "reverse":
        for r in reverse(graph, args.atom_id):
            print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
