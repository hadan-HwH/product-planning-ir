# PPIR Verification & Testing

> **성격:** "AI용 원본을 사람이 어떻게 신뢰하는가"의 설계. 검증·테스트 피라미드와 merge 게이트.
> 무엇을 구현했는지(현황)는 [06-status.md](06-status.md), 개선 백로그는 [07-improvements.md](07-improvements.md).
> 이 문서는 **설계(왜/무엇)** 를 담는다. **Level 0·1·6·7 + merge 게이트 + `ppir-verify` 스킬은 구현됨**(2026-07-07); Level 2·3·4·5는 아직 **제안(proposed)** 이다 — 각 절에 상태를 명시한다.

---

## 0. 한 문장

**원본(`ir/` atom 그래프)은 AI용이라 사람이 직관적으로 못 읽는다. 그러니 원본을 사람이 읽어서 검증하지 말고, 원본에서 사람이 검증할 수 있는 산출물(뷰·리포트·질문형 acceptance test)을 계속 생성해서 그걸로 검증한다.**

---

## 1. 왜 이 문서가 필요한가 — PPIR의 본질적 리스크

PPIR의 최대 강점(원본이 타입 atom 그래프)은 그대로 최대 약점이 된다.

- 원본이 AI용 atom graph가 되면, **사람은 더 이상 원본을 직관적으로 읽지 못한다.**
- 그러면 **잘못된 atom 하나가 들어가도 사람이 못 본다.**
- 그 잘못이 compiled 문서 → AI context → 후속 결정으로 **계속 전파된다.**

그래서 "audit이 PASS면 됐다"로는 부족하다. 기계 검증만으로는 *스키마상 올바르지만 의미상 틀린* atom을 못 잡는다. PPIR에는 네 종류의 검증이 함께 있어야 한다.

| 종류 | 무엇을 보장하나 | 누가 읽나 |
|---|---|---|
| **기계 검증** | 스키마·ID·ref·lifecycle이 형식적으로 옳다 | validator (자동) |
| **의미 검증** | 근거 체인이 완전하다 (source→claim→decision→rule→view) | 리포트 (자동 생성, 사람 확인) |
| **사람 검증** | 의도한 문서·정책이 실제로 나온다 | compiled view·acceptance 답변 |
| **회귀 검증** | 예전에 옳던 것이 지금도 옳다 / 틀린 걸 넣으면 잡힌다 | golden·mutation 테스트 |

> 핵심 원칙: **사람은 YAML 48개를 읽지 않는다.** 사람은 근거 리포트와 "질문에 대한 답"을 읽는다. YAML이 맞는지는 판단 못 해도, "Available 수정 가능해?"의 답이 맞는지는 판단할 수 있다.

---

## 2. 검증 피라미드 (Level 0 → 7)

각 레벨의 역할이 다르다. 아래로 갈수록 사람의 판단이 더 개입한다.

| Level | 이름 | 종류 | 산출물 | 상태 |
|---|---|---|---|---|
| **0** | Hard Validator | 기계 | audit PASS/FAIL | ✅ 구현 (`validate_evidence`·`validate_graph_health` 추가) |
| **1** | Traceability Test | 의미 | `compiled/reports/traceability-report.md` | ✅ 구현 (`compilers/compile_traceability.py`) |
| **2** | Source Coverage Test | 의미 | `compiled/reports/source-coverage/{feature}.md` | 제안 |
| **3** | Compiled View Review | 사람 | 근거 컬럼 포함 화면정의서 | 부분(화면정의서만) |
| **4** | Question Acceptance Test | 사람 | `AcceptanceQuestionSet` + 생성 답변 | 제안 (신규 kind 필요) |
| **5** | Cross-view Consistency Test | 의미 | view 간 atom ID 일치 리포트 | 제안 |
| **6** | Regression / Golden Test | 회귀 | `tests/test_regression.py` | ✅ 구현 ([P1-3](07-improvements.md#p1-3-tests에-az-파일럿-회귀-테스트)) |
| **7** | Mutation / Negative Test | 회귀 | `tests/test_mutation.py` | ✅ 구현 |

> 실행: `python pipeline/06_verify.py` (audit + traceability + pytest 한 번에) 또는 `ppir-verify` 스킬.

---

## 3. Level 0 — Hard Validator (기계 검증)

**현재 구현됨** (`validators/`, `03_audit.py`가 실행): `file_envelope · schema · id · ref · typed_ref · lifecycle`.

**제안 — 추가할 규칙:**

| 규칙 | 무엇을 강제 | 종류 |
|---|---|---|
| `source_required` | accepted atom은 `source_refs` 또는 `decision_refs`를 가져야 한다 | HARD |
| `decision_required` | 모든 MUST/MUST_NOT Rule은 `decision_refs`를 가져야 한다 | HARD |
| `test_required` | 모든 Rule은 TestCase 참조 또는 명시적 `no_test_reason`을 가져야 한다 | HARD |
| `no_orphan_atom` | 어떤 참조도 받지 못하는(그래프에서 고립된) accepted atom 금지 | WARN→HARD |
| `no_direct_compiled_edit` | `compiled/`·`graph/` 수기 편집 감지 (해시 대조) | HARD |
| `generated_staleness` | compiled 뷰의 `source_graph_hash`가 현재 그래프와 다르면 stale | WARN |
| `atomicity` | 한 atom = 한 의미 (예: 한 Rule에 MUST와 MUST_NOT 혼재 금지) | WARN |

> `test_required`의 `no_test_reason`이 중요하다. "테스트 없음"을 **명시적으로** 남기면 "빠뜨린 것"과 "일부러 안 만든 것"이 구분된다. `OpenQuestion`과 같은 철학이다(규칙 4).

**최소 규칙 (P0에서 먼저):**
- 모든 accepted atom은 `source_refs` 또는 `decision_refs`를 가진다.
- 모든 MUST/MUST_NOT Rule은 `decision_refs`를 가진다.
- 모든 Rule은 TestCase 또는 `no_test_reason`을 가진다.
- 모든 DerivedField는 `source_of_truth` + `decision_refs`를 가진다.

사람이 atom을 다 읽지 않아도, **근거 체인이 완전한지**는 기계가 답할 수 있어야 한다.

---

## 4. Level 1 — Traceability Test (의미 검증)

**목표:** 각 accepted atom에 대해 다음이 자동으로 답변된다.

- 이 atom은 **어디서** 왔는가? (어떤 Source 문서/라인)
- 어떤 **claim**에서 나왔는가?
- 어떤 **decision**이 이 atom을 정당화하는가?
- 이 atom은 **어디에** 반영됐는가? (화면/메시지/테스트/compiled view)

**산출물:** `compiled/reports/traceability-report.md` — 그래프의 dependency/reverse 인덱스에서 컴파일.

```markdown
# Traceability Report — Warehouses

## SHOP.RULE.warehouse.available_readonly
- Kind: Rule
- Track: intent
- Commitment: accepted
- Source:    SHOP.SRC.legacy.warehouse_04_v2_0_0
- Claim:     SHOP.CLAIMSET.legacy.warehouse_04#004
- Decision:  SHOP.DEC.warehouse.available_redefined_v2
- Affects (reverse-index):
  - SHOP.DERIVED.warehouse.available
  - SHOP.COMPONENT.warehouse.create_drawer
  - SHOP.COMPONENT.warehouse.edit_drawer
  - SHOP.TEST.warehouse.available_readonly
- Rendered in: 화면정의서 §5, QA test plan
```

**Hard fail 조건 (근거 체인이 끊긴 곳):**

- **orphan atom** — accepted인데 참조 체인이 없음.
- **dangling source** — Source는 있는데 어떤 compiled view에도 한 번도 안 나타남.
- **idle decision** — Decision은 있는데 어떤 Rule/Field/Action도 정당화하지 않음.
- **idle test** — TestCase가 어떤 Rule도 검증하지 않음.

---

## 5. Level 2 — Source Coverage Test (의미 검증)

legacy migration에서 **가장 중요한** 테스트. 문서를 atom으로 변환할 때 사람이 알고 싶은 것:

- 기존 문서의 중요한 내용이 **빠지지 않았나?**
- 어떤 문장이 **법(current law)** 으로 채택됐고, 어떤 문장이 예시/설명/과거 이력으로 분류됐나?
- 어떤 문장이 **OpenQuestion** 으로 남았나?

**산출물:** `compiled/reports/source-coverage/04-warehouses.md`

```markdown
# Source Coverage Report — 04 Warehouses

| Source Section | Classification | Extracted As | Status |
|---|---|---|---|
| §1 개요 | background_only | Source summary | covered |
| §2 Create Drawer Name 검증 | current_law | SHOP.VALIDATOR.warehouse.name | covered |
| §2 Available 입력 없음 | current_law | SHOP.RULE.warehouse.available_readonly | covered |
| §5 Available 파생 정의 | current_law | SHOP.DERIVED.warehouse.available | covered |
| §3 예시 표 | example | (승격 안 함) | ignored_with_reason |
```

**모든 source segment는 아래 중 하나로 분류되어야 한다:**

`current_law` · `superseded_law` · `decision_rationale` · `example` · `message` · `validation` · `api_gap` · `open_question` · `background_only` · `ignored_with_reason`

> `ignored_with_reason`이 핵심이다. AI가 뭔가를 **안 옮겼다면 왜 안 옮겼는지** 남겨야 한다.
> 예: *"이 표는 예시 데이터이므로 example로 분류하고 current Rule로 승격하지 않음."*

**Hard fail 조건:**

- source segment가 **unclassified**.
- `current_law` segment인데 대응 atom 없음.
- superseded 내용인데 accepted Rule로 들어감.
- 예시 데이터가 Rule/Enum으로 승격됨.
- `ignored`인데 reason 없음.

이 테스트가 있어야 "내가 넣은 기존 문서가 제대로 해석됐나"를 사람이 볼 수 있다.

---

## 6. Level 3 — Compiled View Review (사람 검증)

사람은 YAML이 아니라 **생성된 사람용 문서**를 본다. 다만 일반 화면정의서만으로는 부족하다 — **검토용 compiled view**는 각 항목에 **근거 컬럼**을 붙여, "왜 이게 들어갔는지"를 바로 역추적하게 한다.

```markdown
| Rule | 내용 | Decision | Source |
|---|---|---|---|
| SHOP.RULE.warehouse.available_readonly | Available은 Create/Edit에서 입력받지 않는다 | SHOP.DEC.warehouse.available_redefined_v2 | 04 창고 §5 |
```

**현황:** 화면정의서 컴파일(`compile_screen_definition`)은 있으나, **근거 컬럼이 붙은 검토용 뷰는 제안 상태**. compiled provenance(`source_graph_hash`/`generated_at`) 부착은 [P1-2](07-improvements.md#p1-2-compiled-provenance-재현추적) 참조.

---

## 7. Level 4 — Question-based Acceptance Test (사람 검증) ★

**AI용 시스템에서 가장 중요한 테스트.** 사람은 atom graph를 못 읽지만, **질문에 대한 답이 맞는지는 판단할 수 있다.**

feature마다 `AcceptanceQuestionSet`을 만든다.

```yaml
kind: AcceptanceQuestionSet          # ← 신규 kind (아래 "kind 영향" 참조)
id: SHOP.ACCEPTANCE.warehouses.v1
target: SHOP.FEATURE.warehouses
questions:
  - id: Q1
    question: "Warehouse의 Available은 사용자가 수정할 수 있는가?"
    expected_answer_contains:
      - "수정할 수 없다"
      - "WMS warehouse.status.available 파생값"
      - "SHOP.DEC.warehouse.available_redefined_v2"
  - id: Q2
    question: "창고 삭제가 막히는 조건은 무엇인가?"
    expected_answer_contains:
      - "재고가 남아 있을 때"
      - "delete_blocked_when_stock_exists"
      - "failure message"
  - id: Q3
    question: "창고 이름 검증 규칙은 무엇인가?"
    expected_answer_contains: ["필수", "길이", "형식", "중복", "resource_name validator"]
  - id: Q4
    question: "아직 백엔드 확인이 필요한 것은 무엇인가?"
    expected_answer_contains: ["OpenQuestion", "derived available", "BE provisioning"]
```

**동작:** `ppir-explain` / `ppir-context`로 답변을 생성 → `expected_answer_contains`와 대조.

**왜 필요한가:** 사람 입장에선 YAML 48개보다 이게 훨씬 낫다.
> Q. Available 수정 가능해?  A. 불가능합니다. 이유는… (근거 decision/source 인용)

여기서 답이 틀리면 **atom graph가 잘못된 것**이다.

**Hard fail 조건:**
- 정답에 필수 decision/source가 빠짐.
- OpenQuestion이 있는데 "확정됐다"고 답함 (모르는 걸 지어냄 — 규칙 4 위반).

**kind 영향:** `AcceptanceQuestionSet`은 **신규 kind**다. 지금은 [03-kind-catalog.md](03-kind-catalog.md)의 22 kind에 없다 → 정식 도입하려면 token map 등록 + 스키마 + lifecycle matrix 추가가 필요하다. 그 전까지는 fixture(테스트 데이터)로만 둔다.

---

## 8. Level 5 — Cross-view Consistency Test (의미 검증)

한 feature는 여러 compiled view로 투영된다 (Screen Definition / QA Test Plan / FE Handoff / AI Context Pack). 이들이 **같은 Rule ID를 참조**하는지 검사한다.

예 — 창고 삭제 차단 규칙이라면 네 뷰가 모두 `SHOP.RULE.warehouse.delete_blocked_when_stock_exists`를 참조해야 한다:

| view | 반영 |
|---|---|
| Screen Definition | 재고가 남은 창고는 Delete disabled/실패 |
| QA Test Plan | 재고 > 0일 때 delete 시도 → block/failure |
| FE Handoff | delete modal / error toast |
| AI Context Pack | `delete_blocked_when_stock_exists` Rule 포함 |

**검사 방식:** 각 뷰에서 사용된 atom ID를 추출 → 같은 feature의 required atom coverage와 비교.

**Hard fail 조건:**
- Screen Definition엔 Rule 있는데 QA Test Plan엔 TestCase 없음.
- QA엔 테스트 있는데 Screen/Action에 연결된 Rule 없음.
- Context Pack이 **superseded atom을 active rule로** 포함.
- BE Gap Report가 OpenQuestion을 누락.

---

## 9. Level 6 — Regression / Golden Test (회귀 검증)

파일럿이 통과했으면 그 결과를 **golden으로 고정**한다. ([P1-3](07-improvements.md#p1-3-tests에-az-파일럿-회귀-테스트)의 구체화.)

```
tests/fixtures/warehouses/
├─ sources/
├─ expected-source-coverage.yaml
├─ expected-traceability.yaml
├─ expected-acceptance-questions.yaml
└─ expected-compiled-structure.yaml
```

**golden을 두 층으로 나눈다** (markdown 전체 byte 비교는 너무 취약 — 줄바꿈으로 깨지면 안 된다):

1. **구조적 golden** — section 수 · 포함 atom ID · required rule ID · open question ID.
2. **문서 snapshot** — 주요 문단/표만 비교.

원칙: **Markdown 줄바꿈으로 테스트가 깨지면 안 된다. 하지만 중요한 Rule/Decision/Message가 빠지면 깨져야 한다.**

---

## 10. Level 7 — Mutation / Negative Test (회귀 검증)

"잘못된 것이 들어갔을 때 잡는지"를 보는 테스트. PPIR엔 필수다.

| # | Mutation | 기대 |
|---|---|---|
| 1 | `available_readonly`에서 `source_refs` 제거 | audit fail (`source_required`) |
| 2 | superseded decision(`available_operator_toggle_v1`)을 `commitment_level: accepted`로 | lifecycle 또는 semantic conflict fail |
| 3 | `available`을 DerivedField → editable Field로 변경 | cross-view consistency 또는 acceptance Q1 fail |
| 4 | 예시 표를 Rule로 승격 | source coverage fail (example→current_law 승격 금지) |
| 5 | Rule에서 모든 TestCase·`no_test_reason` 제거 | audit fail (`test_required`) |

---

## 11. Proposal Review Packet — 사람이 보는 것

Proposal이 생기면 사람에게 **YAML 전체를 보여주지 않는다.** 다음 패킷을 보여준다.

```markdown
# Proposal Review Packet
## 1. 요약        — 무엇을 바꾸는가? current/superseded/open 수
## 2. Source Coverage    | 원문 섹션 | 분류 | 생성 atom | 판단 |
## 3. New / Updated Atoms | Atom | Kind | Meaning | Source | Decision |
## 4. 위험한 판단  — AI 해석인가? current law 승격 근거? 기존 정책과 충돌?
## 5. Open Questions      | Question | Blocks | Needed From |
## 6. Generated Preview   — 화면정의서 / QA test / explain answer 미리보기
## 7. Acceptance Questions| Question | Expected | Generated Answer | Pass |
## 8. 승인 체크박스
- [ ] 원문 누락 없음
- [ ] 과거 정책이 현재 정책으로 잘못 승격되지 않음
- [ ] 모르는 것은 OpenQuestion으로 남았음
```

---

## 12. Merge Gates — audit PASS만으로 merge 금지

| Gate | 조건 |
|---|---|
| 1 | Hard Validator (Level 0) PASS |
| 2 | Merge transaction (snapshot→apply→audit→실패 시 rollback) OK |
| 3 | Traceability (Level 1) PASS |
| 4 | Acceptance Questions (Level 4) PASS 또는 human override |
| 5 | Compiled Preview 확인 |
| 6 | Human Approval |

**현실적 단계 정책:**

```
P0/P1 단계:  Gate 1 + Gate 2 + Human Approval
운영 단계:   Gate 1 ~ 6 전부
```

---

## 13. "잘못이 오래 남는 것"을 막는 운영 장치

테스트만으로 부족하다. 운영 장치가 함께 필요하다.

### 13.1 Confidence·Review Depth
Proposal에 위험도를 넣는다.

```yaml
risk_level:   low | medium | high
confidence:   high | medium | low
review_depth: normal | strict
```

- legacy 표를 단순 Field로 옮김 → `low`
- 과거 정책과 현재 정책이 충돌 → `high`
- 백엔드 구현을 정책으로 채택 → `high`
- OpenQuestion을 닫음 → `medium`/`high`

`high` risk는 stricter gate를 요구한다.

### 13.2 Quarantine
애매한 atom은 accepted로 바로 넣지 않는다.

```yaml
commitment_level: candidate
status: pending_review
quarantine: true
reason: "source conflict — v1 토글 정의와 v2 파생 정의 충돌"
```

### 13.3 OpenQuestion aging
OpenQuestion은 오래 방치되면 위험하다.
- age > 30일 → warning
- active screen/action을 block → hard warning

### 13.4 Explain Smoke Test
중요 feature마다 5~10개 질문을 던진다. 답이 틀리면 사람이 즉시 감지한다.
> 왜 Available은 read-only인가? / 이름 validation은 어디서? / 삭제가 막히는 조건? / 남은 API gap? / 이전 정책에서 바뀐 것?

---

## 14. 테스트 스위트 (제안 — `tests/`는 현재 비어 있음)

```
tests/
├─ fixtures/warehouses/{sources, expected-*.yaml}
├─ test_audit.py
├─ test_merge_transaction.py
├─ test_traceability.py
├─ test_source_coverage.py
└─ test_acceptance_questions.py
```

**바로 넣을 골든 10개:**

1. 48 atom audit PASS
2. 잘못된 typed_ref → audit fail
3. pending Proposal → merge fail
4. HARD violation → merge rollback (ir/ 원상 복구)
5. compiled 화면정의서 생성됨
6. source coverage 100% (모든 segment 분류됨)
7. traceability 체인 완전 (orphan/dangling 0)
8. accepted Rule은 Decision·Source·Test를 가짐
9. acceptance Q: "Available read-only" 답변 pass
10. superseded v1 decision이 current law로 취급되지 않음

---

## 15. Quality Dashboard (feature별)

YAML을 몰라도 상태를 파악하는 최종 뷰.

```markdown
# PPIR Quality Dashboard — Warehouses
## Summary
- Atoms: 48 | Current Rules: 9 | Superseded Decisions: 1 | Open Questions: 1 | Test Cases: 2
- Source Coverage: 100% | Traceability: 100% | Acceptance: 5/5 pass
- Audit: PASS | Compiled Views: fresh
## Risk
- High-risk judgments: 1 — Available semantics: operator toggle → WMS 파생값
## Open Questions
- SHOP.OQ.derived_available_be_provisioning — BE confirmation 필요
## Last Generated
- source_graph_hash: … | generated_at: … | compiler_version: …
```

---

## 16. 운영 원칙 — merge 전 답할 수 있어야 하는 10문

1. 기존 source의 중요한 내용이 **모두 분류**됐는가?
2. 어떤 문장이 **current law**가 됐는가?
3. 어떤 문장이 **superseded/deprecated**로 남았는가?
4. 어떤 문장이 **OpenQuestion**으로 남았는가?
5. accepted Rule은 **Decision·Source·Test**를 갖는가?
6. compiled view를 보면 **의도한 문서**가 나오는가?
7. explain 질문에 **사람이 기대한 답**이 나오는가?
8. 같은 atom이 **FE/BE/QA/AI view에서 일관되게** 쓰이는가?
9. 잘못된 **mutation을 넣으면 테스트가 잡는가?**
10. 이 변경이 나중에 **어디에 영향을 주는지 reverse-index로** 보이는가?

이 10문에 답할 수 있으면, 사람이 YAML을 직접 읽지 않아도 품질을 판단할 수 있다.

---

## 17. 핵심 판단

> **PPIR의 검증은 "YAML을 사람이 읽는 것"이 아니라, "AI용 원본에서 사람용 검증 뷰와 질문형 acceptance test를 생성해서 그걸로 확인하는 것"이다.**

사람은 Source Coverage · Traceability · Acceptance Questions · Compiled Preview · Regression Diff를 검토한다. YAML은 끝까지 기계 산물로 둔다.
