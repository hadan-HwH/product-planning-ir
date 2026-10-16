# PPIR Improvements Backlog

> **성격:** 개선 제안과 그 근거. 우선순위별(P0/P1/P2). 개인적 관찰과 설계 제안이 여기 모인다.
> 현재 구현 상태는 [06-status.md](06-status.md).

각 항목: **문제 → 제안 → 근거**. "완료" 표시는 이번 문서 재구성으로 반영된 것.

---

## P0 — 지금 바로

### P0-1. 문서를 수명별로 분리 ✅(완료)
- **문제:** 한 파일에 원칙(저변동)·현황(고변동)·사용법·개인 제안이 섞여 SSOT로 쓰기 과밀.
- **제안:** README + architecture / repository-map / kind-catalog / glossary / operating-guide / status / improvements 로 분리.
- **근거:** 네 종류는 수명이 다르다. 원칙은 거의 안 바뀌고 현황은 매주 바뀐다. 섞이면 "이 문장 아직 유효한가?"를 매번 의심하게 된다.

### P0-2. kind 카탈로그에 implemented/reserved 상태 ✅(완료)
- **문제:** token map의 22 kind 중 4종(PERM·STATE·BINDING·TERM)은 스키마가 없는데 표에선 동등해 보임.
- **제안:** [03-kind-catalog.md](03-kind-catalog.md)에 상태 컬럼. 특히 **DataBinding(BINDING)은 이전 논의의 핵심 kind였으나 현재 reserved**임을 명시.
- **근거:** "BINDING도 바로 쓸 수 있다"는 오해를 막는다. AI가 없는 스키마로 atom을 만들면 audit이 깨진다.

### P0-3. "사람은 YAML 직접 안 씀"의 MVP 예외 명시 ✅(완료)
- **문제:** 개발자가 "근데 지금 YAML 만지잖아?"라고 느끼면 원칙 전체의 신뢰가 흔들림.
- **제안:** [05-operating-guide.md §3](05-operating-guide.md#3-사람이-yaml을-만져야-할-때-mvp-예외) — seed/schema 작업은 허용, accepted IR 직접 수정은 불가.
- **근거:** 예외를 숨기면 규칙이 위선이 된다. 명시하면 규칙과 현실이 공존한다.

### P0-4. lifecycle 설명을 "독립 축이나 조합은 matrix로 제한"으로 ✅(완료)
- **문제:** "세 축은 완전히 독립"이라는 서술은 운영상 위험(모든 조합 허용으로 오해).
- **제안:** [01-architecture.md §3](01-architecture.md#세-축은-독립이지만-조합은-제한된다-중요) — 의미 축은 독립이나 유효 조합은 lifecycle matrix가 강제.
- **근거:** validator가 이미 조합을 제한하고 있다. 문서가 코드와 어긋나면 안 된다.

### P0-5. id 없는 YAML은 proposals wrapper 외엔 audit HARD ✅(완료)
- **문제:** `load_atoms`가 id 없는 파일을 **조용히 건너뛴다.** 실제 누락·오타를 놓칠 수 있다.
- **제안:** 신규 validator `validate_file_envelope` — `ir/**/*.yaml` 중 top-level `id`가 없으면(또는 mapping이 아니면) HARD violation, 단 `ir/proposals/**` wrapper만 예외.
- **근거:** 로더는 건너뛰더라도 **audit는 잡아야** 한다. 조용한 무시는 "커버했다"는 착각을 만든다.
- **상태:** ✅ 구현 완료 — `validators/validate_file_envelope.py`, `runtime/audit.run_all`에 연결(→ audit CLI·pipeline 03·merge 자동 적용). YAML parse error도 함께 HARD로 잡음. 실제 audit PASS 유지, 결함 파일 3종(음성 테스트)에서 검출 확인.

### P0-6. pipeline/01은 파일럿 seed임을 명시 ✅(완료)
- **문제:** `01_adopt_pilot.py`를 범용 adopter로 오해하면 다른 문서에 그대로 쓰려다 실패.
- **제안:** README·operating-guide·repository-map에 "파일럿 전용 seed, 범용 adopter 아님" 명시.
- **근거:** 이 파일은 04 문서를 손으로 atom화한 1회성 부트스트랩이다.

---

## P1 — 곧

### P1-1. kind 정보 단일 registry ✅(완료)
- **문제:** kind 정보가 6곳에 흩어짐 — `ppir.config.yaml kind_token_map` / `patch.py _KIND_FOLDER` / `validate_typed_refs.py _RULES` / `validate_lifecycle.py _MATRIX` / `schemas/` / 컴파일러. 거의 반드시 drift.
- **구현:** `kind-registry.yaml`(27 kind) 단일 원본 + `ppir/registry.py` 로더(`token_map`·`folders`·`lifecycle_matrix`·`typed_ref_rules`·`schema_files`·`reserved_kinds`). `config.py`·`patch.py`·`validate_lifecycle`·`validate_typed_refs`가 전부 registry에서 파생. `ppir.config.yaml`에서 `kind_token_map` 제거.
- **검증:** 파생 구조가 기존 하드코딩과 **정확히 동일**함을 대조(token 27·lifecycle 20·typed_refs 33). `tests/test_kind_registry_consistency.py` 7종으로 schema↔registry 정합성·token 유일성 상시 감시. 전체 88 passed, audit PASS.
- **부수 발견:** Rule lifecycle의 `draft`는 commitment_level이 아니라 status 값이라 envelope 스키마가 이미 거부하는 **죽은 값** → 제거(동작 변화 없음, 사용 atom 0).
- **효과:** 새 kind 추가가 6곳 → **2곳**(registry + schema) 편집으로 축소. [03-kind-catalog.md](03-kind-catalog.md#새-kind를-추가할-때-손대는-곳).

### P1-2. compiled provenance (재현·추적) ✅(완료)
- **문제:** compiled 문서가 어느 atom 상태에서 나왔는지 모름 → 표류(staleness) 판단 불가, 오류 역추적 어려움.
- **구현:** `compilers/provenance.py` — 생성 뷰 최상단에 `<!-- provenance: compiler=NAME@VERSION source_graph_hash=… -->`(md) / `# provenance: …`(yaml) 스탬프. 4개 컴파일러(screen_definition·traceability·decision_projection·context_pack)의 모든 write 지점 + pipeline 05/06에 배선.
- **결정성:** `source_graph_hash`(atom 그래프 sha256 12자)·`compiler_version`은 결정적 → compiled/ **diff-clean, golden 테스트 무영향**(테스트는 `render()`/`build()`를 직접 부르고 write 경로만 스탬프됨). `generated_at`은 비결정적이라 **기본 off**, 빌드/CI가 `provenance.stamp(..., generated_at=…)`로 주입 가능.
- **검증:** `tests/test_provenance.py` 6종(해시 결정성·atom 변경 시 해시 변화·스타일·generated_at 주입). fixture로 실제 스탬프 확인(projection yaml은 `#` → YAML 파싱 유효). 전체 96 passed.
- **효과:** compiled 뷰가 "어느 그래프에서 나왔나"를 스스로 증명 → staleness 판정·오류 역추적의 기반. [05-operating-guide.md §6.1](05-operating-guide.md#61-compiled-문서에-오류가-보일-때).

### P1-3. tests/ 회귀 안전망 ✅(완료 — 사용자 + plan8)
- **문제:** `tests/`가 비어 있었음. 다음 kind 추가 때 조용히 깨질 수 있었다.
- **현재:** 초기 레거시 화면 파일럿은 제거됐고(→ [06-status.md](06-status.md)), 대신 plan8이 pytest suite + `tests/fixtures/decision-evolution-a-to-a2/` 골든 + `06_verify`(regression+mutation)를 깔았다. P1-1/P1-2/P1-4가 여기에 registry·provenance·skills-sync 테스트를 추가(전체 96 passed).
- **근거:** validator·merge·컴파일러는 순수 함수라 테스트하기 좋고, 이 안전망이 있어 P1-1 registry 리팩터를 안전하게 검증할 수 있었다.

### P1-4. 스킬 공용 reference 단일 원본 + packaging ✅(완료)
- **문제:** `ppir-core.md`(10)·`runtime-commands.md`(10)·`review-packet-template.md`(5)가 각 스킬 `references/`에 사본으로 존재 — 헌법 한 줄 고치려면 10곳 편집. (`ppir-skills-v0.1` 이중 트리는 그새 제거됨.)
- **구현:** `skills-shared/`(단일 원본 3파일) + `scripts/build_skills.py` — presence 기반 배포(각 스킬이 이미 가진 공용 파일명을 원본에서 갱신). `--check`로 drift 감지(exit 1).
- **검증:** `tests/test_skills_shared_sync.py` 2종(전 사본 sync·고아 원본 없음). 25개 공용 사본이 원본과 일치. 오염 주입→check FAIL→build 복구 확인. `06_verify`가 pytest suite를 돌리므로 게이트에도 포함.
- **효과:** 공용 reference 편집이 10곳 → **1곳**(`skills-shared/`) + `build_skills.py`.

### P1-5. ownership 규칙 ✅(문서화 완료)
- [05-operating-guide.md §4](05-operating-guide.md#4-ownership-규칙--atom을-어느-scope에-둘까). feature/shared/foundations/reality/governance 판단 기준. 남은 것: 도구화(위반 감지).

### P1-6. current-law 선택 규칙 ✅(문서화 완료)
- [05-operating-guide.md §5](05-operating-guide.md#5-current-law-선택-규칙--문서에-과거현재-결정이-섞여-있을-때). legacy migration의 과거/현재 결정 판별 기준.

---

## P2 — 나중

### P2-1. Refactor Proposal operation
- **문제:** merge가 create/update/deprecate만 지원. atom 재구조화(split/merge/move-scope)를 표현할 1급 operation이 없다.
- **제안:** Proposal에 `refactor` operation 추가 — `split` / `merge_atoms` / `move_scope` / `deprecate_with_replacement`. 참조 자동 업데이트 포함.
- **근거:** [05-operating-guide.md §6.2](05-operating-guide.md#62-atom이-잘못-쪼개졌을-때-refactor)를 지금은 여러 create+deprecate로 우회한다. 잦아지면 1급 operation이 필요.

### P2-2. compiled 오류 수정 워크플로우 ✅(문서화 완료)
- [05-operating-guide.md §6.1](05-operating-guide.md#61-compiled-문서에-오류가-보일-때). 도구화(renderer trace)는 P1-2에 의존.

### P2-3. source 해석 오류 수정 워크플로우 ✅(문서화 완료)
- [05-operating-guide.md §6.3](05-operating-guide.md#63-source가-잘못-해석됐을-때).

### P2-4. Decision.rationale 분화
- **문제:** 근거·트레이드오프·제약·비목표를 지금은 `Decision.rationale` 문자열 배열에 몰아넣음.
- **제안:** 복잡해지면 별도 governance kind로 분리 — `DesignRationale` / `Tradeoff` / `Constraint` / `NonGoal`.
- **근거:** 현재 규모에선 rationale 인라인이 합리적. 결정별 트레이드오프가 많아지면 검색·재사용을 위해 atom화가 유리하다. **지금은 "Decision.rationale에 저장, 커지면 분리"로 남겨둔다.**

---

## 관찰된 설계적 강점 (유지할 것)

- **폴더-독립 ID + rglob 로더** — 리팩터링 내성. 폴더는 사람 편의일 뿐.
- **트랜잭션 merge + 롤백** — ir/가 반쯤 깨진 상태로 남지 않음. Git과 별개의 원자성.
- **DO NOT EDIT 배너** — 생성물이 스스로 "원본 아님"을 선언.
- **track 경계** — "구현됐다 ≠ 정책이다"를 구조가 강제.
