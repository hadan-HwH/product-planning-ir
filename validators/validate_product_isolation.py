"""Product isolation guard (D2IR decision, 2026-07-08).

`load_atoms` flattens all of ir/ into ONE global graph — folders are organization,
not isolation. Products are separated only by their DOMAIN id-prefix (SHOP, D2IR, …)
plus the convention that they don't reference each other. This validator enforces
that convention: a product-domain atom may not reference another product's atoms.

Shared foundation domains (config `shared_domains`: PROD/UI/TERM/TONE/MSG) are the
escape hatch — any product may reference them; they may not reference a product.
"""
from __future__ import annotations

from pathlib import Path

from ppir.config import REPO_ROOT, SHARED_DOMAINS
from ppir.atoms import load_atoms, iter_id_refs


def _domain(atom_id: str) -> str:
    return atom_id.split(".")[0]


def check(atoms: dict) -> list:
    out = []
    for atom_id, entry in atoms.items():
        src = _domain(atom_id)
        if src in SHARED_DOMAINS:
            # a foundation may reference other foundations, but not a product
            allowed = SHARED_DOMAINS
        else:
            # a product may reference its own domain + shared foundations
            allowed = {src} | SHARED_DOMAINS
        for ref in {r for r in iter_id_refs(entry["data"]) if r != atom_id}:
            if _domain(ref) not in allowed:
                out.append(f"{atom_id} ({src}) references {ref} "
                           f"({_domain(ref)}) — cross-product reference not allowed")
    return sorted(out)


def run(ir_dir: Path = REPO_ROOT / "ir") -> list:
    return check(load_atoms(ir_dir))
