# PPIR Glossary

> kind/track/status/commitment_level 등 핵심 용어의 짧은 정의. kind 목록은 [03-kind-catalog.md](03-kind-catalog.md).

## 기본 단위

- **atom** — 타입(kind)과 전역 유일 ID를 가진 최소 지식 단위. `ir/` 아래 YAML 파일 하나.
- **SSOT (Single Source of Truth)** — 유일한 원본. PPIR에서는 `ir/`의 atom 그래프.
- **ref (참조)** — 한 atom이 다른 atom의 ID를 값으로 갖는 것. 그래프의 간선(edge).
- **projection (투영)** — atom에서 생성된 뷰(compiled 문서, graph 인덱스). 원본 아님.

## ID

`{DOMAIN}.{KINDTOKEN}.{slug}` — 예: `SHOP.DERIVED.warehouse.available`.
- **DOMAIN** — 화이트리스트: `PROD, UI, TERM, TONE, MSG, SHOP` (SHOP=예시 쇼핑몰 어드민).
- **KINDTOKEN** — kind 약어 ([03-kind-catalog.md](03-kind-catalog.md)).
- **slug** — 소문자/숫자/`_`/`.`. 전역 유일, 재사용 금지.

## 4개의 메타데이터 축

축은 의미상 독립이지만 **모든 조합이 허용되지는 않는다** — lifecycle matrix가 kind별로 유효 조합을 제한한다([01-architecture.md §3](01-architecture.md#세-축은-독립이지만-조합은-제한된다-중요)).

### track — 지식의 성격
| 값 | 뜻 |
|---|---|
| `discovery` | 영업·고객·마케팅 신호, 아이디어, 요구 후보 |
| `intent` | 확정된 제품 정책 (화면·규칙·필드·액션·메시지·테스트) |
| `reality` | 구현 사실 (백엔드 MVP·OpenAPI·코드·DB·런타임) |
| `governance` | 결정·근거·변경요청·트레이드오프·보류·기각 |

### commitment_level — 지식의 확정도
`observed`(직접 관찰) → `interpreted`(분석했으나 미승인) → `candidate`(후보) → `accepted`(제품 승인·SSOT) → `planned`(로드맵) → `implemented`(구현) → `shipped`(출시).
그 외: `deferred`(보류) · `rejected`(기각) · `superseded`(대체됨) · `deprecated`(폐기).

### status — 워크플로우 상태
`draft → extracted → proposed → pending_review → approved → merged` (승인 경로) · `accepted` · `rejected` · `deprecated` · `superseded`.

### scope — 소속
`{ product?, platform?, app?, feature? }`. atom이 어느 앱·기능에 속하는지. **저장 폴더를 결정**한다([02-repository-map.md](02-repository-map.md#폴더-축의-원리-patchpy의-_path_for)).

## normative (Rule 전용)
규범 강도: `MUST` / `MUST_NOT` / `SHOULD` / `MAY`.

## 주요 산출물

- **Proposal** — ir/ 변경 제안(diff). create/update/deprecate operation 묶음.
- **ReviewPacket** — 사람 리뷰용으로 스킬이 만드는 요약(추출된 claim·제안 변경·open question·검증 결과).
- **Context Pack** — AI 작업용으로 잘라낸 부분 그래프 + 프롬프트 조각.
- **compiled view** — 화면정의서 등 사람이 읽는 생성 문서 (`DO NOT EDIT`).
