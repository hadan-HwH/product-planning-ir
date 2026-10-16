"""Provenance stamp for compiled views (P1-2).

Every generated file carries WHICH graph state and compiler produced it, so
staleness ("was this regenerated after the atoms changed?") is machine-checkable
and any compiled line can be traced back to an atom-graph fingerprint.

- `source_graph_hash` and `compiler_version` are deterministic (stable given the
  same atoms) → compiled outputs stay diff-clean and golden tests are unaffected.
- `generated_at` is non-deterministic and therefore OFF by default; a build/CI
  may inject it explicitly (see docs/07 P1-2). Keeping it off keeps committed
  compiled/ reproducible.
"""
from __future__ import annotations

import hashlib
import json

COMPILER_VERSION = "1"


def graph_hash(atoms: dict) -> str:
    """12-char deterministic fingerprint of the atom graph that fed a view."""
    payload = json.dumps(
        {aid: entry["data"] for aid, entry in sorted(atoms.items())},
        sort_keys=True, ensure_ascii=False, default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def line(compiler: str, atoms: dict, generated_at: str | None = None,
         style: str = "html") -> str:
    """One provenance comment line. style 'html' for Markdown, 'yaml' for YAML."""
    parts = [f"compiler={compiler}@{COMPILER_VERSION}",
             f"source_graph_hash={graph_hash(atoms)}"]
    if generated_at:
        parts.append(f"generated_at={generated_at}")
    body = "provenance: " + " ".join(parts)
    return f"<!-- {body} -->" if style == "html" else f"# {body}"


def stamp(text: str, compiler: str, atoms: dict, generated_at: str | None = None,
          style: str = "html") -> str:
    """Prepend a provenance line above the existing content (banner stays intact)."""
    return line(compiler, atoms, generated_at, style) + "\n" + text
