# PPIR Status

> **성격:** 변동성이 가장 높은 문서 — 현재 구현 상태와 로드맵. 이 파일만 자주 갱신된다.
> 개선 백로그(우선순위별)는 [07-improvements.md](07-improvements.md).

**기준일:** 2026-07-08

---

## 한 줄 현황

**결정 진화 그래프(plan8) 엔진 완성 + 옛 모델 정합화(plan9) 대체로 완료.** Governance(결정 그래프)가 SSOT 중심, Intent는 cite, Reality/Discovery는 신호원(전부 reduce rule 1로 격리). 옛 `Decision`/`Supersession` deprecated. 첫 실데이터 제품 `D2IR`(설계 이력 도그푸딩) 86 atom. 스펙 v3.0.0이 v2.1.0 supersede. verify PASS(121 테스트).

---

## atom 인벤토리 (현재 `ir/`)

**제품 `D2IR` — 86 atom / DecisionTarget 15개** (DecisionEvent 34 · SolutionOption 30 · Source 6 · OpenQuestion 1). 이 시스템을 만든 설계 결정 흐름 자체를 결정 그래프로 기록(도그푸딩). `ir/d2ir/design-history/`. 예: `knowledge_representation`(마크다운→타입IR→결정그래프 3단계 replace), `pilot_data`(cancel_target), `demo_data_source`(propose+reject, 자기참조), `option_authoring`(adopt→reject→adopt 번복), `product_isolation`·`reducer_scope`·`ssot_repo` 등. audit PASS, projection/context-pack 자동 생성. (초기 레거시 화면 파일럿 48 atom은 파이프라인 검증에 쓴 뒤 제거했다 — 그 결정 자체가 `pilot_data` 타깃으로 기록돼 있다.) 합성 예시는 `tests/fixtures/decision-evolution-a-to-a2/`.

---

## 동작하는 것 (검증됨)

- **결정 진화 그래프 (plan8, 2026-07-07):** 신규 5 kind(DecisionTarget·SolutionOption·DecisionEvent·DecisionRelation·CurrentDecisionProjection) + reducer(`compilers/compile_decision_projection.py`, **16 event_type 전부** + rule 3 effective_from·rule 5 authority_level) + guard 4종(`validators/validate_decision_projection.py`) + explain 3모드(`runtime/explain_decision.py`). a→a2 골든 픽스처(`tests/fixtures/decision-evolution-a-to-a2/`)로 **핵심 명제 증명**: 같은 소스에서 naive_latest=a, reducer=a2. step05 compile·step06 verify에 배선. **Context Pack(Phase ④) 완료**: `compilers/compile_context_pack.py` — projection을 AI-facing authority(current)+inactive(`must_not_use_as_current`)+`forbidden_inferences`("Do not present option a as the current decision")+open questions+sources로 컴파일(md+yaml). 청크 RAG와 갈리는 핵심 산물. **Chunk RAG baseline 정량 비교(Phase ⑤) 완료**: `evaluation/`(chunk_baseline·harness) — 같은 소스 코퍼스에 chunk-RAG를 돌려 DecisionGraph와 대조. 결과(`compiled/reports/decision-eval-report.md`): **Timeline Faithfulness** baseline 0.40 vs graph 1.00, **Context Contamination Rate** baseline 0.80 vs graph 0.00, 현재-답 baseline=a(07-15 신호에 오도) vs graph=a2. (reducer `as_of`를 effective_from→decision_time 폴백으로 보정해 타임라인 정답 재현.) **다음: adopt 자동화(plan3) → atomicity(plan7).** (Phase ② 파일럿 승격은 파일럿 데이터 제거로 폐기.)
- **구모델 정합화 (plan9, 2026-07-08):** 옛 `Decision`/`Supersession` **deprecated**(`validate_deprecated_kinds`) + Rule 근거가 `DecisionEvent`/`Projection` 허용 + 제품 격리(`validate_product_isolation`, 고유 DOMAIN + cross-product ref HARD 금지) + **Reality 트랙 첫 구현**(`ImplementationFact` kind + `validate_drift` — "구현≠정책" 기계 체크) + adopt에 `decisions` 모드(대화→결정그래프 추출 방법) + 小 스킬 4종(context/router/audit/legacy) 결정그래프 이관. Discovery는 결정그래프가 흡수(신호원으로 축소). 스펙 v3.0.0.
- `ppir/` 로더, `schemas/` **24 kind** + envelope (결정그래프 5 + Reality 1 + deprecated 2 + reserved 4 포함).
- **validator 12종** (file_envelope·schema·id·ref·typed_ref·lifecycle·evidence·graph_health·decision_projection·product_isolation·deprecated_kinds·drift) → **audit PASS (0 hard)**.
- `runtime/merge.py` 트랜잭션 merge (스냅샷→apply→audit→롤백).
- `runtime/graph_query.py` 3인덱스 빌드.
- `compilers/compile_screen_definition.py` → 화면정의서 재생성.
- pipeline 02→06 전 구간.
- 스킬 팩 v0.1 (10종) **설계** 완료.

---

## 미완 (설계됐으나 미구현)

| 항목 | 현재 상태 |
|---|---|
| `/adopt` 자동화 | 범용 adopter 미구현 — 현재는 스킬이 Proposal을 만들고 사람이 승인 |
| runtime 스크립트 다수 | `adopt.py`·`reflect.py`·`publish.py`·`context.py`·`explain.py`·`observe_impl.py` 미구현 (스킬이 "pending"으로 표시) |
| role별 publish | FE/BE/QA/PM 각각의 뷰 미구현 (현재 화면정의서 1종만) |
| Context Pack 생성 | 자동화 미구현 |
| 앱 로드맵/인덱스 뷰 | 미구현 |
| Discovery 트랙 스킬 | phase 3 예정 (고객/영업/마케팅 신호) |
| reserved kind 4종 | TERM·PERM·STATE·BINDING — 스키마 없음 ([03-kind-catalog.md](03-kind-catalog.md)) |

---

## 다음 단계 (요약)

우선순위와 근거는 [07-improvements.md](07-improvements.md)에 P0/P1/P2로 정리. 요약:

- **P0** — 문서 분리(완료), kind 상태 표기(완료), MVP 예외 명시(완료), lifecycle 조합 제약 서술(완료), **id-없는 YAML audit(`validate_file_envelope`) 구현(완료)**, pipeline/01 성격 명시(완료). → **P0 전부 완료.**
- **P1** — kind-registry 단일화 ✅, compiled provenance(hash/version) ✅, 스킬 공용 reference 단일 원본 ✅, tests/ 회귀 안전망 ✅(사용자+plan8), ownership·current-law 규칙 ✅(문서). → **P1 전부 완료.**
- **P2** — Refactor Proposal operation(미착수), compiled/source 오류 수정 워크플로우(문서화 완료), Decision.rationale 분화(plan8 결정 진화 그래프가 상위 대체).
