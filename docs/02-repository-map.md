# PPIR Repository Map

> **성격:** repo의 상세 구조와 폴더/파일별 역할. "무엇이 어디에 있나".
> 설계 원리는 [01-architecture.md](01-architecture.md), kind 정의는 [03-kind-catalog.md](03-kind-catalog.md).

리포는 3층으로 나뉜다(데이터 / 기계 / 절차 — [01-architecture.md §5](01-architecture.md#5-3층-구조--아키텍처의-중심축)). 아래는 층별 상세.

```
product-planning-ir/
├─ ppir.config.yaml    # 공통 식별자: id규칙·domains·tracks·statuses·commitment_levels·schema_mode
├─ kind-registry.yaml  # ★ kind 단일 원본: token·folder·lifecycle·typed_refs (P1-1)
├─ README.md           # 절대 규칙 + 첫 실행
├─ ir/  sources/  schemas/  compiled/  graph/          ── ① 데이터 층
├─ ppir/  validators/  runtime/  compilers/            ── ② 기계 층
├─ pipeline/  .claude/skills/  skills-shared/  scripts/  ── ③ 절차 층
├─ docs/              # 문서 (이 파일 포함)
└─ tests/             # pytest suite + fixtures (registry·provenance·skills-sync·plan8 골든)
```

> `ppir-skills-v0.1/`(구 배포 이중 트리)는 제거됐다 — 스킬 트리는 `.claude/skills/` 하나, 공용 reference 원본은 `skills-shared/`(P1-4).

---

## ① 데이터 층

### `ir/` — 진짜 SSOT

feature가 1급 단위. **한 기능의 모든 atom이 한 폴더 밑에** 모인다(검색·로드맵 단위).

**이 저장소에 실제로 들어 있는 것**은 `ir/d2ir/design-history/` 하나다 — 이 시스템을 만들면서 내린 설계 결정들을 이 시스템 자신의 결정 그래프로 기록한 데이터(도그푸딩, 86 atom). 제품 기획 데이터는 별도로 관리하며 이 저장소에 포함하지 않는다.

```
ir/
└─ d2ir/design-history/               # D2IR = 이 시스템 자신의 설계 이력
   ├─ sources/          SRC.*          설계 세션·스펙 버전 (근거)
   ├─ target/           TARGET.*       결정 대상 ("SSOT를 어느 레포에 둘까" 등)
   ├─ options/          OPTION.*       후보안
   ├─ events/           DEVENT.*       adopt / replace / cancel / reject … (시간순 결정 이벤트)
   └─ open-questions/   OQ.*           아직 못 정한 것
```

앱 feature 데이터가 들어오면 아래 레이아웃이 생긴다(`patch.py`의 `_path_for`가 scope로 경로를 정한다 — 아래 [폴더 축의 원리](#폴더-축의-원리-patchpy의-_path_for)). 예시는 가상의 쇼핑몰 어드민(`SHOP`)의 창고 관리 화면이다.

```
ir/
├─ product/                            # PROD.* 상품 방향·패키지
├─ foundations/                        # 전 앱 공통 UI/TERM/TONE/MSG
├─ apps/
│  └─ shop-admin/                      # 앱 = 1급 단위 (모노레포 packages/ 처럼)
│     ├─ shared/                       #  ── 앱 내 여러 feature 공용 ──
│     │  ├─ rules/     RULE.resource_name.{required,min_length,max_length,format,unique}.yaml
│     │  └─ messages/  MSG.resource_name.{required,min_length,max_length,format,duplicate}.yaml
│     └─ features/
│        ├─ warehouses/
│        │  │   # (근거 / governance)
│        │  ├─ sources-atoms/    SRC.legacy.warehouse_04_v2_0_0.yaml
│        │  ├─ claim-sets/       CLAIMSET.legacy.warehouse_04.yaml   (문서에서 뽑은 주장들)
│        │  ├─ legacy-maps/      LEGACYMAP.warehouse_04.yaml         (문서조각→atom 매핑)
│        │  ├─ decisions/        DEC.*  (v1 toggle / v2 redefined / delete_block …)
│        │  ├─ supersessions/    SUPERSESSION.available_v1_to_v2.yaml
│        │  │   # (제품 정책 / intent)
│        │  ├─ entities/         ENTITY.warehouse.yaml
│        │  ├─ fields/           FIELD.warehouse.name.yaml
│        │  ├─ derived-fields/   DERIVED.warehouse.available.yaml
│        │  ├─ validators/       VALIDATOR.warehouse.name.yaml
│        │  ├─ rules/            RULE.*  (available_readonly / delete_blocked / edit_name)
│        │  ├─ components/       COMPONENT.*  (create_drawer / edit_drawer / delete_modal)
│        │  ├─ actions/          ACTION.*  (create / edit / delete)
│        │  ├─ messages/         MSG.warehouse.*  (create/edit/delete×성공·실패 + tooltip/confirm)
│        │  ├─ relations/        RELATION.warehouse.storage_group.yaml
│        │  ├─ screens/          SCREEN.warehouses.yaml
│        │  ├─ open-questions/   OQ.derived_available_be_provisioning.yaml
│        │  └─ test-cases/       TEST.{delete_blocked,name_required}.yaml
│        └─ storage-groups/             #  ── 관계로만 등장하는 이웃 feature ──
│           ├─ entities/  ENTITY.storage_group.yaml
│           └─ fields/    FIELD.storage_group.name.yaml
└─ proposals/
   ├─ approved/                        # 승인됐으나 미반영 (merge 대상)
   └─ merged/                          # 반영 완료 제안 (atom을 만든 diff의 이력)
```

**설계 의도로 읽어야 할 것:**
- `shared/`의 `resource_name` 규칙이 `VALIDATOR.warehouse.name`에 참조로 물린다 → **검증 규칙을 한 번만 쓰고 여러 feature가 공유**(중복 제거). 어디에 둘지는 [05-operating-guide.md의 ownership 규칙](05-operating-guide.md#ownership) 참조.
- 근거(governance) → 정책(intent)이 폴더로도 분리돼 "무엇이 법이고 무엇이 근거인지" 한눈에.
- `storage-groups`가 필드 2개짜리 껍데기인 이유: `RELATION`이 가리킬 대상이 있어야 typed_ref 검증을 통과. **참조 무결성이 폴더 구성을 이끈다.**

> **id 없는 YAML:** `ir/` 아래에서 top-level `id`가 없는 파일은 로더가 건너뛴다. 이는 **`ir/proposals/` 아래 Proposal wrapper에만 허용**되는 예외다. 그 외 위치의 id 없는(또는 mapping이 아닌) YAML은 `validate_file_envelope`가 audit HARD violation으로 잡는다. ✅(P0-5 구현됨)

### `sources/` `schemas/` `compiled/` `graph/`

```
sources/legacy/                       # legacy 원문(마크다운). SRC atom의 captured_ref가 가리킨다.
sources/openapi/                      # (예약 — observe-impl용)
   # 이 저장소에는 원문을 포함하지 않는다.

schemas/                              # _envelope + 18개 kind 스키마
├─ _envelope.schema.yaml             # 공통 필드 (required: kind/id/track/status/commitment_level/scope)
├─ proposal · claimset · source · legacy-extraction-map            (근거/제안)
├─ decision · supersession                                         (governance)
├─ entity · field · derived-field · validator · rule               (데이터/정책)
├─ screen · component · action · message · relation                (UI)
└─ open-question · test-case
   # 각 파일은 x-kind: + required: + properties: 만 담고, 로드 시 envelope와 병합됨(ppir/schemas.py)

compiled/
├─ context-packs/                     # 05_compile: DecisionTarget별 AI-facing Context Pack (md + yaml)
├─ reports/decision-projections/      # 05_compile: 현재 권위 결정 projection
├─ reports/traceability-report.md     # 06_verify: 근거 추적 리포트
├─ reports/decision-eval-report.md    # evaluation/harness.py: chunk-RAG 대비 결정그래프 평가
└─ markdown/screen-definitions/…      # 05_compile: Screen atom이 있으면 화면정의서. 맨 위 "DO NOT EDIT" 배너

graph/                                # 04_graph_build 산출물 3종
├─ atom-index.json                    # {id: {kind, track, status, path}}
├─ dependency-graph.json              # {id: [내가 참조하는 id...]}
└─ reverse-index.json                 # {id: [나를 참조하는 id...]}  ← 영향분석 엔진
```

---

## ② 기계 층 — 파이썬 4패키지 (파일별 역할)

모든 파일이 `ppir` 공용 로더 위에 서고 서로 import한다. 순수 함수 위주라 테스트하기 쉽다.

### `ppir/` — 공용 로더 (다른 모든 층이 의존)
| 파일 | 역할 |
|---|---|
| `registry.py` | **kind-registry.yaml 로더** — `token_map`·`folders`·`lifecycle_matrix`·`typed_ref_rules`·`schema_files`·`reserved_kinds`. config·patch·validator가 여기서 파생(P1-1). ppir 내 어떤 것도 import 안 함(순환 방지) |
| `config.py` | `ppir.config.yaml` 로드 → `ID_RE·DOMAINS·TRACKS·COMMITMENT_LEVELS·schema_mode`. `KIND_TOKEN_MAP`은 `registry`에서 파생 |
| `atoms.py` | `load_atoms()`: ir/ 전체 rglob → `{id:{path,data}}` · `iter_id_refs()`: 값 속 ID 재귀 수집 |
| `schemas.py` | envelope + kind 스키마 로드/병합 · `allowed_props`(오타 탐지) |
| `patch.py` | Proposal changes를 ir/에 적용 · `_path_for`(scope→폴더, folder는 registry) · create/update/deprecate |

### `validators/` — 6종 검증
| 파일 | 줄 | 검사 |
|---|---|---|
| `validate_file_envelope.py` | `ir/**` YAML은 mapping + top-level `id` 필수 (`ir/proposals/` wrapper만 예외) |
| `validate_schema.py` | 병합 스키마 준수 + unknown property 경고(schema_mode) |
| `validate_ids.py` | ID 정규식·domain·kind토큰 일치·파일 중복 |
| `validate_refs.py` | 모든 ID 참조가 실재 + deprecated/rejected 아님 |
| `validate_typed_refs.py` | kind 제약 참조 (registry `typed_refs`, 예: `Screen.components`→`Component`) |
| `validate_lifecycle.py` | kind별 (허용 track, 허용 commitment_level) matrix (registry) |
| `validate_evidence.py` | (plan8) accepted atom의 근거 체인(source/decision)·normative rule의 test 커버리지 |
| `validate_graph_health.py` | (plan8) accepted 정책 atom의 orphan(역참조 0) 경고 |
| `validate_decision_projection.py` | (plan8) 결정 진화 그래프 guard 4종 |

> 위 9종 중 `validate_file_envelope`만 **파일 자체**를 훑어 로더가 조용히 건너뛴 id-없는 파일을 잡는다. 나머지는 `load_atoms`가 걸러낸 atom dict 위에서 돈다. (표는 파일 단위 — 라인 수는 변동이 잦아 생략.)

### `runtime/` — 실행 도구 (CLI 진입점)
| 파일 | 역할 |
|---|---|
| `audit.py` | 9 validator 전부 실행 · `_hard()`로 HARD/advisory 구분 · exit code |
| `graph_query.py` | `build()` 3인덱스 생성 · `write()` · `deps`/`reverse` 조회 CLI |
| `merge.py` | ★트랜잭션 merge: 스냅샷→patch→graph→audit→HARD면 롤백→Proposal을 merged/로 |
| `explain_decision.py` | (plan8) 결정 진화 그래프 explain 3모드 |

### `compilers/` — 뷰 생성
| 파일 | 역할 |
|---|---|
| `loaders.py` | `AtomStore`: get/many/by_kind/by_kind_in_app 헬퍼 |
| `provenance.py` | **compiled 뷰 provenance 스탬프** (`source_graph_hash`·`compiler_version`, md/yaml) (P1-2) |
| `compile_screen_definition.py` | SCREEN atom 1개 → 관련 atom 수집 → 9섹션 화면정의서 md 렌더 |
| `compile_traceability.py` | (plan8) 근거 추적 리포트 (atom→source/decision, 역참조, broken-chain) |
| `compile_decision_projection.py` | (plan8) DecisionEvent 스트림 → CurrentDecisionProjection reducer |
| `compile_context_pack.py` | (plan8) projection → AI-facing Context Pack (authority/inactive/forbidden_inferences) |

---

## ③ 절차 층

### `pipeline/` — 실행 순서 O (번호)
legacy 문서 → 검증된 IR → 재생성 화면정의서 한 바퀴.

| 파일 | 역할 |
|---|---|
| `02_merge.py` | `approved/`의 모든 Proposal을 `runtime.merge`로 반영 |
| `03_audit.py` | 전 validator 실행 |
| `04_graph_build.py` | 그래프 3인덱스 생성 |
| `05_compile.py` | Screen 화면정의서 + (plan8) DecisionProjection·Context Pack. 전부 provenance 스탬프 |
| `06_verify.py` | (plan8) merge 게이트: audit + traceability 리포트 + pytest(regression·mutation) |

> 초기 파일럿 전용 seed(`01_adopt_pilot.py`)는 파일럿 데이터와 함께 제거됐다. 새 문서 수용은 Claude의 `ppir-adopt`/`ppir-legacy-migration` 스킬이 담당한다.

### `.claude/skills/` — 실행 순서 X (AI가 골라 씀)
스킬 11종(`ppir-*` 10 + `ppir-verify`). 상세 사용법은 [05-operating-guide.md](05-operating-guide.md).

```
.claude/skills/ppir-{router, legacy-migration, adopt, review-merge, audit,
                     publish, context, explain, reflect, observe-impl, verify}/
   ├─ SKILL.md            # frontmatter(name/description) + 절차·경계·산출물 형식
   └─ references/         # 공용 파일은 skills-shared/에서 생성됨(직접 편집 금지):
       ├─ ppir-core.md            # 모든 스킬 공통 헌법 (권위규칙·4트랙·write boundary)
       ├─ runtime-commands.md     # runtime 스크립트 호출 패턴 + "성공을 지어내지 말 것"
       ├─ review-packet-template.md  # (쓰기 스킬만) 사람 리뷰용 패킷 양식
       └─ router-matrix.md        # (router만) 요청→스킬 라우팅 표 (단일 사용, 비공유)
```

### `skills-shared/` + `scripts/build_skills.py` — 공용 reference 단일 원본 (P1-4)
`ppir-core.md`·`runtime-commands.md`·`review-packet-template.md`의 **정본**은 `skills-shared/`에 하나씩만 산다. `python scripts/build_skills.py`가 각 스킬 `references/`로 배포하고, `--check`가 drift를 감지한다(`tests/test_skills_shared_sync.py`가 상시 감시, `06_verify` 게이트 포함). 헌법 수정은 `skills-shared/` 한 곳만.

---

## 폴더 축의 원리 (`patch.py`의 `_path_for`)

atom 저장 폴더는 **id·kind가 아니라 scope로 결정**된다:

| 조건 | 저장 위치 |
|---|---|
| `domain == PROD` | `ir/product/{folder}/` |
| app 없음 | `ir/foundations/{folder}/` |
| app + feature 있음 | `ir/apps/{app}/features/{feature}/{folder}/` |
| app만 있음 | `ir/apps/{app}/shared/{folder}/` |

`{folder}`는 kind별 매핑(`Rule`→`rules` 등). **track/kind는 경로가 아니라 atom 메타데이터**다. 로더가 `rglob("*.yaml")`로 전체를 훑고 ID로만 인덱싱하므로, 폴더는 사람이 찾기 좋은 정리일 뿐 — 옮겨도 ID·그래프·참조는 안 깨진다.
