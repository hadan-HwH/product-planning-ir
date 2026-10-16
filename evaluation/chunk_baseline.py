"""A deterministic chunk-RAG baseline (plan8 Phase 5).

Models what a naive retrieval-augmented reader does with the same source corpus:
chunk each Source's captured text, retrieve the freshest topical passages, and
read the "current decision" off the most recent one. It has NO model of
governance events, supersession, or authority — so a late signal that merely
*mentions* a superseded option ("a is needed again") is taken as the current
answer. That is the failure mode the DecisionGraph reducer avoids.

No embeddings / network / randomness — retrieval is recency ranking with keyword
option extraction, so the benchmark is reproducible.
"""
from __future__ import annotations

import re

_DATE_RE = re.compile(r"(\d{4})_(\d{2})_(\d{2})")


def _date(source_id: str) -> str:
    m = _DATE_RE.search(source_id)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else "0000-00-00"


def _options_for(atoms: dict, target_id: str):
    """(slug, option_id) for the target's options, longest slug first so 'a2'
    is matched before 'a'."""
    opts = [(e["data"]["id"].split(".")[-1], e["data"]["id"])
            for e in atoms.values()
            if e["data"].get("kind") == "SolutionOption"
            and e["data"].get("target_ref") == target_id]
    return sorted(opts, key=lambda t: len(t[0]), reverse=True)


def _option_in(text: str, opts) -> str | None:
    for slug, oid in opts:
        # slug as a standalone token, not the prefix of a longer one (a vs a2).
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(slug)}(?![A-Za-z0-9])", text):
            return oid
    return None


def chunk_sources(atoms: dict, target_id: str) -> list:
    """One chunk per Source in the target's feature, chronological."""
    opts = _options_for(atoms, target_id)
    tscope = (atoms.get(target_id, {}).get("data", {}).get("scope") or {})
    feature = tscope.get("feature")
    chunks = []
    for e in atoms.values():
        d = e["data"]
        if d.get("kind") != "Source":
            continue
        if feature and (d.get("scope") or {}).get("feature") != feature:
            continue
        text = d.get("captured_text", "")
        chunks.append({"id": d["id"], "date": _date(d["id"]),
                       "text": text, "option": _option_in(text, opts)})
    return sorted(chunks, key=lambda c: c["date"])


def retrieve(chunks: list, as_of: str | None = None, k: int | None = None) -> list:
    """Naive retrieval: passages up to `as_of`, freshest first, top-k."""
    pool = [c for c in chunks if not as_of or c["date"] <= as_of]
    pool = sorted(pool, key=lambda c: c["date"], reverse=True)
    return pool[:k] if k else pool


def answer(chunks: list, as_of: str | None = None) -> str | None:
    """The baseline's 'current decision': the option named by the freshest
    retrieved passage that names one."""
    for c in retrieve(chunks, as_of=as_of):
        if c["option"]:
            return c["option"]
    return None
