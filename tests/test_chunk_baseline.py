"""The chunk-RAG baseline (plan8 Phase 5): chunk the same source corpus, retrieve
by recency, and read the 'current' answer off the freshest topical passage. It has
no notion of governance events, so the 07-15 signal ("a needed again") fools it."""
from ppir.atoms import load_atoms
from ppir.config import REPO_ROOT
from evaluation import chunk_baseline as cb

FIXTURE = REPO_ROOT / "tests" / "fixtures" / "decision-evolution-a-to-a2"
TARGET = "SHOP.TARGET.business_need_x_resolution"


def _atoms():
    return load_atoms(FIXTURE)


def test_chunks_one_per_source_with_dates():
    chunks = cb.chunk_sources(_atoms(), TARGET)
    assert len(chunks) == 5
    assert {c["date"] for c in chunks} == {
        "2026-07-01", "2026-07-05", "2026-07-10", "2026-07-12", "2026-07-15"}


def test_option_extraction_prefers_a2_over_a():
    chunks = {c["date"]: c for c in cb.chunk_sources(_atoms(), TARGET)}
    assert chunks["2026-07-12"]["option"] == "SHOP.OPTION.business_need_x.a2"
    assert chunks["2026-07-15"]["option"] == "SHOP.OPTION.business_need_x.a"


def test_retrieve_filters_by_as_of_and_ranks_recent_first():
    chunks = cb.chunk_sources(_atoms(), TARGET)
    got = cb.retrieve(chunks, as_of="2026-07-11")
    assert got[0]["date"] == "2026-07-10"                 # freshest ≤ as_of first
    assert all(c["date"] <= "2026-07-11" for c in got)


def test_answer_now_is_fooled_into_a():
    # The whole point: latest topical passage (07-15) says 'a'.
    assert cb.answer(cb.chunk_sources(_atoms(), TARGET)) == "SHOP.OPTION.business_need_x.a"


def test_answer_as_of_before_signal_is_a2():
    chunks = cb.chunk_sources(_atoms(), TARGET)
    assert cb.answer(chunks, as_of="2026-07-13") == "SHOP.OPTION.business_need_x.a2"
