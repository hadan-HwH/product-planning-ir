# PPIR Architecture

> **성격:** 변하지 않아야 하는 설계 원칙. "왜 이렇게 만들었나".
> 상세 파일 구조는 [02-repository-map.md](02-repository-map.md), 사용법은 [05-operating-guide.md](05-operating-guide.md), 현황은 [06-status.md](06-status.md).

---

## 0. 한 문장

기획 지식을 **문서가 아니라 타입 있는 atom 그래프(SSOT)** 로 두고, 사람·AI가 읽는 문서는 그 그래프에서 **컴파일**한다. 문서는 원본이 아니라 그래프의 *투영(projection)* 이다.

---

## 1. 왜 이 시스템이 존재하는가

### 문서 방식의 고질병
전통적 기획은 "화면정의서 md"가 원본이다. 여기서 생기는 문제:

- **중복·표류(drift)** — 같은 규칙(예: 리소스 이름 검증)이 여러 문서에 복붙되고, 하나만 고쳐지면 어긋난다.
- **근거 소실** — "이 필드는 왜 읽기전용인가?"의 근거 체인이 산문에 묻힌다.
- **영향 파악 불가** — 규칙 하나 바꿀 때 어떤 화면·테스트·메시지가 깨지는지 추적할 방법이 없다.
- **AI 협업 비효율** — 맥락을 주려면 리포 전체를 읽혀야 한다.

### PPIR의 해법
지식을 **원자(atom)** 로 쪼개 **타입(kind)** 과 **전역 유일 ID** 를 부여하고, atom끼리 **참조(ref)** 로 엮어 **그래프**를 만든다.

- 규칙은 한 atom에만 산다 → 중복 제거, 표류 불가.
- 결정(Decision)·근거(rationale)·출처(Source)가 별도 atom으로 남고 참조로 연결 → 근거 체인 추적.
- dependency/reverse 인덱스로 변경 영향을 기계적으로 계산.
- AI에는 리포 전체가 아니라 작업에 필요한 부분 그래프(Context Pack)만 준다.

---

## 2. 4개의 절대 권위 규칙

(전문은 [README](../README.md#절대-규칙). 여기서는 설계적 의미를 덧붙인다.)

1. **`ir/`의 atom만 원본** — 나머지는 근거이거나 생성물.
2. **`compiled/`·`graph/`는 생성물** — 손대면 다음 컴파일에 덮인다.
3. **모든 쓰기는 Proposal → staging 검증 → merge** — 그 외 도구는 읽기·검증·색인·생성만.
4. **모르는 것은 OpenQuestion** — AI가 추론으로 빈칸을 메우는 것을 구조적으로 차단.

이 규칙들은 취향이 아니라 **시스템 무결성의 전제**다. 하나라도 깨지면 "SSOT가 하나"라는 보장이 사라진다.

---

## 3. 핵심 개념 4축

모든 atom에 붙는 메타데이터. **폴더가 아니라 atom 안의 필드**로 관리된다(그래서 폴더를 옮겨도 그래프가 안 깨진다). 용어 정의는 [04-glossary.md](04-glossary.md).

- **kind** — 원자의 타입 (22종, [03-kind-catalog.md](03-kind-catalog.md)).
- **track** — 지식의 성격: Discovery / Intent / Reality / Governance (§4).
- **commitment_level** — 지식의 확정도: observed→interpreted→candidate→accepted→…→shipped.
- **status** — 워크플로우 상태: draft→proposed→approved→merged→…

### 세 축은 독립이지만 조합은 제한된다 (중요)

`track / commitment_level / status`는 **의미 축은 서로 독립적**이다. 그러나 **모든 조합이 허용되는 것은 아니다.**
kind마다 허용되는 (track, commitment_level) 조합이 정해져 있고, 이를 **lifecycle validator의 matrix가 강제**한다.

예:
- `Decision` → track은 반드시 `governance`, commitment_level은 `{accepted, superseded}`만.
- `Source` → `governance` + `{observed}`만.
- `Rule` → `intent` + `{accepted, deprecated, superseded, draft}`만.

> 즉 "독립 축"은 개념 설명이고, 운영에서는 **matrix로 좁혀진 유효 조합만 통과**한다. matrix 밖 조합은 audit HARD violation.

---

## 4. 4 Track — 지식의 경계선

모든 atom은 정확히 하나의 track에 속한다. 이 경계가 "구현됐다 ≠ 정책이다"를 강제한다.

| Track | 담는 것 | 혼동하면 안 되는 것 |
|---|---|---|
| **Discovery** | 영업·고객·마케팅 신호, 아이디어, 요구 후보 | 확정된 제품 정책 |
| **Intent** | 확정된 제품 정책 — 화면·규칙·필드·액션·메시지·테스트 | 구현 사실 |
| **Reality** | 백엔드 MVP, OpenAPI, 코드 동작, DB 사실, 런타임 관찰 | 확정된 제품 정책 |
| **Governance** | 결정·변경요청·근거·트레이드오프·보류·기각 | 화면 스펙 그 자체 |

**왜 나누나:** 백엔드가 만든 것을 정책으로 착각하면 꼬리가 몸통을 흔든다. 영업 신호를 요구사항으로, 요구 후보를 확정 규칙으로 승격시키면 근거 없는 정책이 쌓인다. track이 이 경계를 물리적으로 막는다.

---

## 5. 3층 구조 — 아키텍처의 중심축

리포는 **수명과 성격이 다른 3개 층**으로 나뉜다. 각 층은 바로 아래 층에만 의존한다 → 위층을 갈아엎어도 아래가 안 흔들린다.

| 층 | 폴더 | 성격 |
|---|---|---|
| **① 데이터 층** | `ir/` `sources/` `schemas/` `compiled/` `graph/` | 지식 그 자체 + 규격 + 생성물 |
| **② 기계 층** | `ppir/` `validators/` `runtime/` `compilers/` | 데이터를 읽고·검증·변경·렌더하는 순수 파이썬. 순서 없음, 서로 import |
| **③ 절차 층** | `pipeline/` `.claude/skills/` | 기계를 정해진 순서/판단으로 오케스트레이션. pipeline=기계용, skills=AI용 |

### 구축 순서 = 의존 방향 (아래에서 위로)

```
① 규격:  ppir.config.yaml + schemas/*.yaml   "무엇이 유효한 atom인가"를 설정으로 못박음
   ▼
② 로더:  ppir/ (config·atoms·schemas·patch)  "atom을 어떻게 읽고·찾고·쓰나"
   ▼
③ 검증:  validators/                          순수 함수 (atoms)->[위반]. 규격 집행
   ▼
④ 실행:  runtime/ (audit·graph_query·merge)   ③을 묶어 안전하게 바꾸고 색인
   ▼
⑤ 렌더:  compilers/                           결과를 사람용 뷰로 투영
   ▼
⑥ 절차:  pipeline/ (기계용) + skills/ (AI용)   ①~⑤를 오케스트레이션
```

---

## 6. 데이터 흐름 — 한 사이클

```
legacy .md (sources/)                                          ← 원문, 법 아님
   │  ppir-legacy-migration / ppir-adopt 스킬
   ▼
Source · ClaimSet · LegacyMap  +  APPROVED Proposal            ← 근거 + 제안(diff)
   │  runtime/merge.py — 스냅샷 → patch.apply → graph → audit
   │                        └─(HARD 위반)→ 롤백, ir/ 그대로 둠
   ▼ (통과 시)
ir/ accepted atoms  (SSOT)                                     ← 여기만 진짜 원본
   │  graph_query.build → graph/*.json      compile → compiled/*.md
   ▼                                            ▼
dependency/reverse 인덱스                    화면정의서 (DO NOT EDIT)
   │  explain / reflect / context가 소비           사람·AI가 읽음
   ▼
"왜?" 근거체인 · "뭐가 깨지나?" 영향분석 · AI Context Pack
```

---

## 7. Write boundary — 운영 안정성의 핵심

> **쓰기가 일어나는 지점은 단 하나 — `runtime/merge.py`.**
> 모든 변경은 Proposal을 통해 **staging 사본에서 검증된 뒤에만** accepted `ir/`에 반영된다. 그 외 모든 도구·스킬은 **읽기·검증·색인·생성**만 수행한다.

merge는 트랜잭션이다:

1. `ir/`를 임시 폴더에 스냅샷.
2. Proposal operations를 적용(`patch.apply`).
3. 그래프 재빌드 + 전 validator audit.
4. **HARD violation이 하나라도 있으면 롤백** — 스냅샷 복원, Proposal은 `approved/`에 그대로.
5. 통과 시에만 그래프 기록 + Proposal을 `merged/`로 이동.
6. `approved`가 아닌 Proposal은 merge 거부. deprecated/superseded atom은 **삭제하지 않고** status만 전이.

이 설계 덕에 `ir/`는 절대 반쯤 깨진 상태로 남지 않는다. Git과 별개의 자체 원자성이다.

---

## 8. graph와 compiled view의 역할

둘 다 생성물이지만 소비자가 다르다.

- **`graph/`** (기계·AI가 소비) — 3종 인덱스.
  - `atom-index.json` : `{id → kind/track/status/path}`
  - `dependency-graph.json` : `{id → 내가 참조하는 것들}`
  - `reverse-index.json` : `{id → 나를 참조하는 것들}` ← **영향분석·근거추적의 엔진**
- **`compiled/`** (사람이 소비) — 화면정의서 등. 맨 위 `DO NOT EDIT` 배너로 "원본 아님"을 파일이 스스로 선언.

핵심: **사람이 읽는 문서와 기계가 읽는 그래프가 같은 atom에서 함께 파생**된다. 그래서 둘이 어긋날 수 없다.
