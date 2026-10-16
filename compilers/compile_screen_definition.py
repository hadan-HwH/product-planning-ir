"""Compile a Screen atom (+ its components, fields, derived fields, validators,
actions, rules, messages, relations, decisions, open questions) into a Markdown
screen definition. Generated output — never hand-edited.

Usage: python compilers/compile_screen_definition.py SHOP.SCREEN.warehouses
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ppir.config import REPO_ROOT            # noqa: E402
from ppir.atoms import load_atoms            # noqa: E402
from compilers.loaders import AtomStore      # noqa: E402
from compilers import provenance             # noqa: E402

BANNER = "<!-- DO NOT EDIT — generated from ir/ atoms. Change the atoms, not this file. -->"


def _t(atom: dict) -> str:
    t = atom.get("title") or {}
    return t.get("ko") or t.get("en") or atom["id"]


def render(ir_dir: Path, screen_id: str) -> str:
    s = AtomStore(ir_dir)
    screen = s.get(screen_id)
    if not screen:
        raise KeyError(f"screen not found: {screen_id}")
    app = (screen.get("scope") or {}).get("app")
    L = [BANNER, f"# {_t(screen)} — 화면 정의", ""]

    # 1. Metadata
    L += ["## 1. 개요",
          f"- Screen: `{screen_id}`",
          f"- Route: `{screen.get('route', '')}`",
          f"- 진입점: " + (", ".join(screen.get("entry_points", [])) or "—"),
          ""]

    # 2. 데이터 — only fields this screen actually uses (columns + component fields)
    field_ids = list(screen.get("columns", []))
    for c in s.many(screen.get("components", [])):
        field_ids += c.get("fields", [])
    seen, rows = set(), []
    for fid in field_ids:
        if fid in seen:
            continue
        seen.add(fid)
        a = s.get(fid)
        if not a:
            continue
        if a["kind"] == "DerivedField":
            rows.append(f"| `{fid.split('.')[-1]}` | DerivedField(read-only) | "
                        f"{a.get('derivation','')} | 파생 | SoT: `{a.get('source_of_truth','')}` |")
        else:
            rows.append(f"| `{fid.split('.')[-1]}` | Field | {a.get('data_type','')} | "
                        f"{a.get('required', False)} | validator: `{a.get('validator_ref','—')}` |")
    L += ["## 2. 데이터", "| 필드 | 종류 | 타입/파생 | 필수 | 비고 |", "|---|---|---|---|---|"] + rows + [""]

    # 3. Components (drawers/modals)
    comps = s.by_kind_in_app("Component", app)
    if comps:
        L += ["## 3. 컴포넌트 (Drawer/Modal)", "| Component | 유형 | 모드 | 필드 | 액션 |", "|---|---|---|---|---|"]
        for c in comps:
            L.append(f"| `{c['id'].split('.',2)[2]}` | {c.get('component_type','')} | "
                     f"{c.get('mode','—')} | {', '.join(x.split('.')[-1] for x in c.get('fields',[])) or '—'} | "
                     f"{', '.join(x.split('.')[-1] for x in c.get('actions',[])) or '—'} |")
        L.append("")

    # 4. Validation
    for v in s.by_kind_in_app("Validator", app):
        L += [f"## 4. 검증 — `{v['id'].split('.',2)[2]}`",
              f"- 대상: `{v.get('target','')}` · 공용 헬퍼: `{v.get('shared_helper','—')}`",
              "", "| 규칙 | Normative | 에러 메시지 |", "|---|---|---|"]
        for r in s.many(v.get("rules", [])):
            msg_ref = (r.get("violation") or {}).get("message_ref")
            msg = s.get(msg_ref) if msg_ref else None
            msg_txt = (msg.get("text", {}).get("ko") if msg else "—")
            L.append(f"| {r.get('description','')} | {r.get('normative','')} | {msg_txt} |")
        L.append("")

    # 5. Actions
    acts = s.by_kind_in_app("Action", app)
    if acts:
        L += ["## 5. 액션", "| Action | API | 상태전이 | 확인 | 결과 |", "|---|---|---|---|---|"]
        for a in acts:
            st = a.get("state_transition") or {}
            trans = (f"{', '.join(st.get('from', []))} → {st.get('to','')}" if st else "—")
            conf = (a.get("confirmation") or {}).get("message_ref", "—")
            rf = a.get("result_feedback") or {}
            res = "/".join(x for x in [rf.get("success_message_ref"), rf.get("failure_message_ref")] if x) or "—"
            api = a.get("api_ref") or ("no_api" if a.get("no_api") else "—")
            L.append(f"| `{a['id'].split('.',2)[2]}` | `{api}` | {trans} | `{conf}` | `{res}` |")
        L.append("")

    # 6. 정책 (Rules not owned by a validator)
    owned = {r for v in s.by_kind_in_app("Validator", app) for r in v.get("rules", [])}
    policy = [r for r in s.by_kind_in_app("Rule", app) if r["id"] not in owned]
    if policy:
        L += ["## 6. 정책 규칙", "| Rule | Normative | 근거 |", "|---|---|---|"]
        for r in policy:
            L.append(f"| {r.get('description','')} | {r.get('normative','')} | "
                     f"{', '.join('`'+d+'`' for d in r.get('decision_refs', [])) or '—'} |")
        L.append("")

    # 7. 관계
    rels = s.by_kind_in_app("Relation", app)
    if rels:
        L += ["## 7. 관계", "| From | To | 유형 | 비고 |", "|---|---|---|---|"]
        for r in rels:
            L.append(f"| `{r.get('from')}` | `{r.get('to')}` | {r.get('relation_type')} | {r.get('note','')} |")
        L.append("")

    # 8. 결정 (why)
    decs = s.by_kind_in_app("Decision", app)
    if decs:
        L += ["## 8. 정책 결정 (근거)"]
        for d in decs:
            tag = " (superseded)" if d.get("status") == "superseded" else ""
            L.append(f"- **`{d['id'].split('.',2)[2]}`{tag}**: {d.get('decision','')}")
            for r in d.get("rationale", []):
                L.append(f"  - 근거: {r}")
            if d.get("supersedes"):
                L.append(f"  - 대체: {', '.join('`'+x+'`' for x in d['supersedes'])}")
        L.append("")

    # 9. Open Questions
    oqs = s.by_kind_in_app("OpenQuestion", app)
    if oqs:
        L += ["## 9. 미해결 질문", "| 질문 | 필요 대상 |", "|---|---|"]
        for q in oqs:
            L.append(f"| {q.get('question')} | {q.get('needed_from','')} |")
        L.append("")

    return "\n".join(L)


def _out(screen: dict, screen_id: str) -> Path:
    scope = screen.get("scope") or {}
    app, feature = scope.get("app", "_"), scope.get("feature")
    slug = screen_id.split(".", 2)[2]
    parts = [app] + ([feature] if feature else [])
    return REPO_ROOT.joinpath("compiled/markdown/screen-definitions", *parts, f"{slug}.md")


def main() -> int:
    screen_id = sys.argv[1]
    ir = REPO_ROOT / "ir"
    md = provenance.stamp(render(ir, screen_id), "screen_definition", load_atoms(ir))
    out = _out(AtomStore(ir).get(screen_id), screen_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"wrote {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
