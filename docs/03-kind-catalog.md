# PPIR Kind Catalog

> **성격:** atom 타입(kind) 카탈로그. 각 kind가 무엇이고, **지금 구현됐는지 예약(reserved)인지**.
> 용어(track/status 등)는 [04-glossary.md](04-glossary.md), 저장 위치는 [02-repository-map.md](02-repository-map.md).

ID는 `{DOMAIN}.{KINDTOKEN}.{slug}`. token은 `ppir.config.yaml`의 `kind_token_map`에 정의된 27종.

## 상태 범례

- **implemented** — 스키마 존재 + 파일럿에서 실제 atom 생성/검증됨.
- **reserved** — token map에는 있으나 **아직 스키마·사례 없음**. 지금 쓰면 안 된다.

> ⚠️ **`DataBinding`(BINDING)은 이전 논의에서 핵심 kind였지만, 현재 MVP에서는 reserved다.**
> 지금은 화면 필드↔API 연결을 `Component.fields` + `Action.api_ref`로 표현한다. BINDING을 정식 도입할지는 [07-improvements.md](07-improvements.md) 참조. "BINDING도 바로 쓸 수 있다"고 오해하지 말 것.

---

## implemented (23종 — 스키마 있음)

### 근거 / Governance
| 토큰 | kind | track | 역할 |
|---|---|---|---|
| `SRC` | Source | governance | 근거 원문(legacy md·회의록·OpenAPI)을 atom으로 등록 |
| `CLAIMSET` | ClaimSet | governance | Source에서 뽑은 주장 묶음 (`#001` 형태로 개별 참조) |
| `LEGACYMAP` | LegacyExtractionMap | governance | legacy 문서 조각 → 어느 atom이 됐는지 추적 |
| `PROP` | Proposal | governance | ir/ 변경 제안(diff). create/update/deprecate operation 목록 |
| `DEC` | Decision | governance | **하나의 실제 선택** + rationale + supersedes |
| `SUPERSESSION` | Supersession | governance | 결정 A→B 대체를 명시 (1-hop; 다단계는 아래 DecisionEvent) |

### 결정 진화 그래프 / Decision Evolution Graph (plan8)
> 결정을 **정적 상태**가 아니라 **target에 스코프된 이벤트 스트림**으로 본다. "현재 유효한 권위 결정"은 `max(timestamp)`가 아니라 이벤트를 reduce해 계산한 `CurrentDecisionProjection`이다. 파일럿 픽스처: `tests/fixtures/decision-evolution-a-to-a2/`.

| 토큰 | kind | track | 역할 |
|---|---|---|---|
| `TARGET` | DecisionTarget | governance | **무엇에 대한 결정인가**의 앵커 (`current_resolution_policy: single`) |
| `OPTION` | SolutionOption | governance | 한 target을 두고 **경쟁하는 해결책 후보** (a vs a2) |
| `DEVENT` | DecisionEvent | governance | adopt/defer/reopen/replace… **결정 이벤트 1건** (decision_time·selects·replaces·supersedes) |
| `DECREL` | DecisionRelation | governance | Supersession 일반화 (replaces/amends/reopens/…) |
| `PROJECTION` | CurrentDecisionProjection | governance | **compile 산물** — reduce로 계산한 현재 권위 결정 (수기 금지, `compiled/`) |

### 제품 정책 / Intent
| 토큰 | kind | track | 역할 |
|---|---|---|---|
| `ENTITY` | Entity | intent | 도메인 개체 (예: warehouse) |
| `FIELD` | Field | intent | 개체의 필드 (validator_ref로 검증 연결) |
| `DERIVED` | DerivedField | intent | **파생 읽기전용** 필드 (source_of_truth + derivation) |
| `VALIDATOR` | Validator | intent | 한 필드에 적용되는 규칙 묶음 (shared_helper 지정 가능) |
| `RULE` | Rule | intent | **하나의 규범 주장** (MUST/MUST_NOT/MAY) + violation 동작 |
| `SCREEN` | Screen | intent | 화면 (route·columns·components·rules) |
| `COMPONENT` | Component | intent | drawer/modal 등 (fields·actions·messages) |
| `ACTION` | Action | intent | 사용자 액션 (trigger·api_ref·result_feedback) |
| `MSG` | Message | intent | 사용자 대상 메시지 1개 (error/toast/tooltip/confirm) |
| `RELATION` | Relation | intent | 개체 간 관계 (one_to_many 등) |
| `OQ` | OpenQuestion | intent | 미해결 질문 (needed_from·blocks) |
| `TEST` | TestCase | intent | given/when/then 테스트 케이스 |

## reserved (4종 — 스키마 없음, 사용 금지)

| 토큰 | kind | 예정 역할 | 대체 표현(현재) |
|---|---|---|---|
| `TERM` | Term | foundations 용어 정의 | 없음 |
| `PERM` | Permission | 권한 | 없음 |
| `STATE` | StateMachine | 상태 기계 | 없음 |
| `BINDING` | DataBinding | 화면 필드 ↔ API/필드 바인딩 | `Component.fields` + `Action.api_ref` |

---

## atom 실물 예시 (DerivedField)

```yaml
kind: DerivedField
id: SHOP.DERIVED.warehouse.available
track: intent
status: accepted
commitment_level: accepted
scope: { platform: commerce, app: shop-admin, feature: warehouses }
entity: SHOP.ENTITY.warehouse
read_only: true
display_only: true
source_of_truth: wms.warehouse.status.available
derivation: 빈 창고(출고 구역 0)=No; 출고 구역 일부 가동=Yes; 전부 중지=No
decision_refs: [SHOP.DEC.warehouse.available_redefined_v2]   # ← 근거 체인
source_refs:   [SHOP.SRC.legacy.warehouse_04_v2_0_0]                        # ← 출처
```

이 한 atom이 "available은 왜 읽기전용인가"의 **완전한 근거 체인**을 담는다: `DerivedField → Decision → (rationale) → Source`.

---

## kind별 허용 lifecycle (matrix 발췌)

`validate_lifecycle.py`가 강제하는 (track, commitment_level) 제약. 전체 축 개념은 [01-architecture.md §3](01-architecture.md#세-축은-독립이지만-조합은-제한된다-중요).

| kind | 필수 track | 허용 commitment_level |
|---|---|---|
| Source / ClaimSet / LegacyExtractionMap | governance | observed |
| Decision | governance | accepted, superseded |
| Supersession | governance | accepted |
| Rule | intent | accepted, deprecated, superseded, draft |
| Screen / Component / Action / Message | intent | accepted, planned, deprecated, superseded |
| Field / DerivedField | intent | accepted, deprecated, superseded |
| Validator / Entity / Relation | intent | accepted, deprecated |

> matrix에 없는 kind는 lifecycle 미제약(schema·id·ref 검증만 받음).

---

## 새 kind를 추가할 때 손대는 곳

**P1-1 완료 이후** kind 메타데이터는 `kind-registry.yaml` **단일 원본**에 모여 있다(token·folder·lifecycle·typed_refs). 그래서 손대는 곳이 6곳 → **2곳**으로 줄었다:

1. **`kind-registry.yaml`** — 해당 kind 항목 추가:
   ```yaml
   MyKind:
     token: MYKIND
     folder: my-kinds
     schema: my-kind.schema.yaml
     lifecycle: { track: intent, commitment_levels: [accepted, deprecated] }
     typed_refs: { some_ref: [TargetKind] }   # 참조가 있으면
   ```
   (스키마 없는 예약 kind면 `{ token: …, folder: …, reserved: true }`)
2. **`schemas/<kind>.schema.yaml`** (`x-kind:` 필수)
3. (사람이 보면) 컴파일러 렌더러 — 선택

`ppir/config.py`(token_map)·`ppir/patch.py`(folder)·`validate_lifecycle.py`(matrix)·`validate_typed_refs.py`(rules)는 전부 `ppir/registry.py`를 통해 이 파일에서 파생된다. drift는 `tests/test_kind_registry_consistency.py`가 잡는다(schema↔registry 정합성, token 유일성, lifecycle track/level 유효성).
