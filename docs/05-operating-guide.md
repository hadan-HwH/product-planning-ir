# PPIR Operating Guide

> **성격:** 실제로 일할 때 보는 문서. 어떤 스킬을 언제 쓰나, pipeline 순서, 판단 규칙, 에러 수정 절차.
> 원칙은 [01-architecture.md](01-architecture.md), 구조는 [02-repository-map.md](02-repository-map.md), 현황은 [06-status.md](06-status.md).

---

## 1. 스킬 시스템 개요

`.claude/skills/`에 11개 스킬이 있다. 파이프라인이 "기계가 도는 방식"이라면, 스킬은 <b>"Claude가 사람 대신 판단하며 도는 방식"</b>이다.

**절대 경계 (write boundary):**
- accepted `ir/`을 바꾸는 것은 **오직 `ppir-review-merge`** 뿐.
- 나머지 스킬은 Source·ClaimSet·Proposal·Report·ContextPack·compiled view만 만든다.
- `compiled/`는 어떤 스킬도 직접 수정하지 않는다.
- 구현된 것은 정책이 아니다 → 백엔드 MVP는 `ppir-observe-impl`로 Reality Track에.

> runtime 스크립트가 아직 없는 경우, 스킬은 설계된 artifact를 텍스트/YAML로 생성하되 해당 실행을 **"pending implementation"으로 표시**해야 한다. 성공한 실행을 지어내지 않는다.

### 스킬 11종
| 스킬 | 하는 일 |
|---|---|
| `ppir-router` | 요청을 보고 알맞은 스킬 선택 (애매하면 여기부터) |
| `ppir-legacy-migration` | 기존 정책서/화면정의서 md → Source·ClaimSet·LegacyMap·Proposal |
| `ppir-adopt` | 회의/Slack/구두 결정 → Source·ClaimSet·Proposal·OpenQuestion |
| `ppir-review-merge` | 승인된 Proposal만 staging·audit 후 반영. **유일하게 ir/를 씀** |
| `ppir-audit` | schema·id·ref·typed_ref·lifecycle·atomicity·중복·표류 검증 |
| `ppir-verify` | docs/08 검증 피라미드 실행 — audit + traceability report + 회귀(골든) 테스트 → Quality Dashboard·merge 게이트 |
| `ppir-publish` | ir/ → 화면정의서·핸드오프·QA·PM 브리핑 컴파일 |
| `ppir-context` | AI 작업용 Context Pack 생성 (리포 전체 대신 부분 그래프) |
| `ppir-explain` | 규칙/화면/필드/결정의 근거 체인 설명 |
| `ppir-reflect` | 변경의 downstream 영향 추적 + Proposal 생성 |
| `ppir-observe-impl` | 백엔드 MVP/OpenAPI/코드/DB를 Reality Track으로 관찰·비교 |

### 라우팅 표
| 상황 | 스킬 |
|---|---|
| 기존 md 정책서/화면정의서 이관 | `ppir-legacy-migration` |
| 회의/Slack/구두 결정 반영 | `ppir-adopt` |
| Proposal 승인 후 반영 | `ppir-review-merge` |
| 변경 영향 범위 확인 | `ppir-reflect` |
| 구조/일관성 검증 | `ppir-audit` |
| feature 신뢰성 검증 ("맞나/빠진 것 없나") · merge 전 게이트 | `ppir-verify` |
| 화면정의서/전달본/QA 문서 생성 | `ppir-publish` |
| AI 작업 context 생성 | `ppir-context` |
| "왜 이렇게 됐는지" | `ppir-explain` |
| 백엔드 MVP/OpenAPI와 정책 비교 | `ppir-observe-impl` |
| 애매함 | `ppir-router` |

> 고객/영업/마케팅 요구(Discovery 트랙)는 이 팩 범위 밖 — phase 3 스킬 예정.

---

## 2. Pipeline — 실행 순서 <a id="pipeline"></a>

```bash
python pipeline/02_merge.py            # merge: ir/proposals/approved/의 Proposal 반영 (트랜잭션, 실패 시 롤백)
python pipeline/03_audit.py            # audit (전 validator)
python pipeline/04_graph_build.py      # graph 인덱스
python pipeline/05_compile.py          # compile → 화면정의서 · DecisionProjection · Context Pack
python pipeline/06_verify.py           # verify: audit + traceability + pytest (merge 게이트)
```

- **새 문서를 받아들이는 첫 단계(adopt)는 스크립트가 아니라 스킬이다.** Claude의 `ppir-adopt`/`ppir-legacy-migration` 스킬이 legacy 문서를 Source·ClaimSet·Proposal로 만들고, 그 Proposal을 `ir/proposals/approved/`에 놓은 뒤 `02_merge` 이후를 돈다. (초기 파일럿용 seed 스크립트 `01_adopt_pilot.py`는 파일럿 데이터와 함께 제거됐다.)
- **`02_merge`만 `ir/`를 바꾼다.** 나머지(audit·graph·compile·verify)는 검증·색인·생성이라 안전하게 반복 가능.
- 생성물만 다시: `rm -rf graph compiled` 후 `04_graph_build`부터. (`ir/`는 SSOT라 지우지 않는다.)

### 개별 도구 직접 호출
```bash
python runtime/audit.py --scope all
python runtime/graph_query.py deps    D2IR.DEVENT.ssot_repo.002_replace_with_ppir   # 이 atom이 참조하는 것
python runtime/graph_query.py reverse D2IR.SRC.session_2026_07_06                   # 이 근거가 정당화한 것들
python runtime/explain_decision.py --mode timeline    D2IR.TARGET.knowledge_representation
python runtime/explain_decision.py --mode why-current D2IR.TARGET.knowledge_representation
python runtime/merge.py <PROPOSAL_ID>                                               # approved Proposal 1건 반영
python compilers/compile_screen_definition.py <SCREEN_ID>                           # Screen atom이 있을 때
```

---

## 3. 사람이 YAML을 만져야 할 때 (MVP 예외)

원칙: **사람은 accepted atom을 직접 편집하지 않는다.** 그러나 MVP 동안 다음은 허용된다.

| 하려는 일 | 허용? | 방식 |
|---|---|---|
| legacy migration seed 작성 | ✅ | Proposal(또는 seed 스크립트)로. accepted IR 직접 수정 ✗ |
| schema/validator/runtime 코드 보강 | ✅ | 코드 개발. atom이 아님 |
| accepted `ir/**` atom 파일 직접 편집 | ❌ | 언제나 금지. Proposal → merge |
| `compiled/`·`graph/` 편집 | ❌ | 생성물. atom 고치고 재생성 |

즉 예외는 **"제안을 만드는 것"과 "기계를 고치는 것"** 에 한정되며, **write boundary(규칙 3)는 그대로** 유효하다.

---

## 4. Ownership 규칙 — atom을 어느 scope에 둘까 <a id="ownership"></a>

같은 규칙이 여러 곳에서 쓰일 때 "누구 소유인가"가 애매하다(예: `resource_name` validator를 Warehouse·Storage Group·Product가 공유). 판단 기준:

1. **하나의 feature에서만 쓰면** → `features/{feature}/` (feature-owned)
2. **같은 app의 2개 이상 feature에서 쓰면** → `apps/{app}/shared/`
3. **여러 app에서 쓰면** → `foundations/`
4. **외부 구현/API 사실이면** → track `reality`
5. **근거/결정/변경 이유면** → track `governance`

> 처음 한 feature 마이그레이션 중 생긴 공용 규칙이라도, 두 번째 소비자가 생기는 순간 `shared/`로 승격(move-scope Refactor)한다.

---

## 5. Current-law 선택 규칙 — 문서에 과거·현재 결정이 섞여 있을 때

legacy migration의 가장 어려운 문제: 한 문서 안에 옛 결정과 새 결정이 같이 있을 때 무엇을 `accepted`로 볼 것인가.
(초기 레거시 화면 파일럿에서는 v1을 `superseded`, v2를 `accepted`로 처리했다.) 일반 규칙:

1. **명시적 버전/날짜가 최신인 것**을 current law로. 옛 것은 삭제하지 말고 `superseded`로 보존 + `Supersession` atom 생성.
2. **변경 이유(QA·결정)가 붙은 쪽**이 이긴다. 근거 있는 새 결정 > 근거 없는 옛 서술.
3. **충돌하는데 우열을 못 정하면** accepted로 승격하지 말고 `OpenQuestion`으로 남긴다.
4. **예시(example) 행은 정책이 아니다** — accepted로 올리지 않는다.
5. MUST/MUST_NOT 규칙에 **source나 decision 근거가 없으면** 승격 보류.

---

## 6. 에러 수정 워크플로우

### 6.1 compiled 문서에 오류가 보일 때
compiled는 생성물이라 **직접 고치면 안 된다**(다음 컴파일에 덮인다).

1. 오류 문장이 **어느 atom에서 렌더됐는지** 추적 (`graph_query reverse`, 또는 향후 renderer trace).
2. 해당 atom 수정 **Proposal** 생성.
3. `ppir-review-merge`.
4. 다시 `publish`(05_compile).

### 6.2 atom이 잘못 쪼개졌을 때 (Refactor)
예: Rule 하나에 정책 2개가 들어감 / Field로 둘 것을 DerivedField로 둠 / feature에 둔 것을 shared로 올려야 함.

현재 merge는 create/update/deprecate 중심이라 **Refactor operation 정의가 필요**하다(→ [07-improvements.md P2](07-improvements.md)). 임시로는 Proposal에서:
- split: 새 atom들 create + 원 atom deprecate + 참조 업데이트(update)
- move-scope: 새 위치로 create + 원자 deprecate (ID가 바뀌면 참조 전부 update)
- merge-atoms: 통합 atom create + 원자들 deprecate

**절대 삭제하지 않는다** — deprecate로만.

### 6.3 source가 잘못 해석됐을 때
legacy migration에서 claim 추출이 틀렸을 수 있다.

1. **ClaimSet 수정 Proposal** (틀린 claim을 정정/추가).
2. 그 claim에서 파생된 atom의 해석 수정 Proposal.
3. 필요 시 `Decision` 추가로 "왜 재해석했는지" governance에 남김.
4. `review-merge` → 재검증.

---

## 7. legacy 문서 수용 권장 흐름 (예: 창고 관리 화면)

```
1. ppir-legacy-migration   04-warehouses + 03 관련 섹션
      → Source, ClaimSet, LegacyExtractionMap, Proposal, ReviewPacket
2. ppir-audit              Proposal scope → 검증 리포트
3. ppir-review-merge       approved Proposal → accepted IR + graph + AuditReport
4. ppir-publish            SCREEN.warehouses, role fe/be/qa/pm → compiled views
5. ppir-context            task screen_update → AI ContextPack
6. ppir-explain            "why is available read-only?" → rule→decision→source 체인
```
