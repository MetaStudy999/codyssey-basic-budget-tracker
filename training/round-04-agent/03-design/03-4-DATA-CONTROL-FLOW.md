# B2-1 03-4 — 명령별 데이터·상태·정렬 흐름 V1.1

> **설계/교육용, 미실행**. 공식 PDF 4~6쪽: list/search 최신순·generator, 거래 CRUD, 예산, 오류. 실제 새 코드는 없음.

## 처음 30초
**입력·검증·처리·결과** 흐름은 같지만, 모든 명령이 파일에 쓰는 것은 아니다. 명령별로 읽기/쓰기/계산 경로를 나눈다.

~~~mermaid
flowchart TD
 A["CLI 명령·옵션"] --> B{"명령 종류"}
 B -->|add/update/delete/import/category/budget| W["쓰기: 대상·입력 검증"]
 B -->|list/search| R["읽기: 조회 옵션 검증"]
 B -->|summary/export| Q["계산/출력: 조회·기간 검증"]
 W --> C{"입력·대상 정상?"}
 C -->|아니요| E["원인·힌트, 종료 비0"]
 C -->|예| F["안전한 파일 저장/교체"]
 R --> G["정렬된 JSONL 순차 읽기·yield"]
 Q --> H["JSONL 읽기·집계 또는 CSV 생성"]
 F --> I["ID/변경 건수 출력"]
 G --> J["조건 일치 거래 최신순 출력"]
 H --> K["요약/CSV 결과 출력"]
 I --> S["정상 종료 0"]
 J --> S
 K --> S
~~~

## '최신순'의 명시적 정의와 반례
**내부 설계 선택:** 거래의 `date`가 큰 것부터, 같은 날짜는 `id` 오름차순. '입력한 순서가 반대라도 거래 날짜가 최신이면 위로'가 목표. ID와 등록 시점은 거래 날짜와 다른 개념이다.

교육용/NOT_EXECUTED:
| 실제 입력 순서 | date | amount |
|---|---|---:|
| 첫 번째 | 2026-10-30 | 3000 |
| 두 번째 | 2026-10-01 | 2000 |

기대 `list` 출력 날짜: **2026-10-30 → 2026-10-01**. **단순 append+역방향 읽기라면 잘못된 결과**. 따라서 [03-3의 정렬된 JSONL 유지](03-3-ARCHITECTURE.md)로 수정한다.

## 상태 불변식·수정/삭제
- 거래 ID는 유일하고 수정해도 동일해야 한다. 거래 날짜나 금액의 수정은 검증 후 정렬 위치를 다시 계산.
- 날짜는 실제 유효 YYYY-MM-DD; 금액은 양수 정수; 유형은 income/expense; category는 등록된 값.
- add, update, delete와 import의 최종 저장 후에도 `transactions.jsonl` 날짜 내림차순 불변.
- update/delete에서 없는 ID는 **원본 파일 변경 없이** 오류+힌트와 비0 종료.
- 카테고리 사용 중 제거는 거부(공식 허용안 중 선택). 예산은 월별 지출 합계로 사용률 계산. `잔액 = 수입 - 지출`.
- 조건 검색은 지정한 조건 간 AND(모두 만족); 기간은 시작/끝 포함(설계 선택).
- 거래가 없는 달: '데이터 없음'. 예산만 존재하는 달에 잔액·예산 출력 정책은 04 구현 전에 예제와 함께 확정.
- `summary`는 집계 중심 읽기, `export`는 내부 거래 파일을 **바꾸지 않고** 사용자가 지정한 CSV 출력만 생성.

## 흐름의 추적 포인트
~~~mermaid
sequenceDiagram
 participant User as 사용자
 participant CLI
 participant Service as 서비스
 participant Repo as JSONL 저장소
 User->>CLI: add/date/amount
 CLI->>Service: 거래 생성 요청
 Service->>Service: 유효성 및 ID 검사
 Service->>Repo: 정렬된 새 파일로 안전한 교체
 Repo-->>Service: 저장 결과
 Service-->>CLI: 거래 id
 CLI-->>User: 저장 완료 또는 원인+힌트
~~~

## 5분 종이 실습
입력: income 100000, expense 30000, budget 20000(동일 월). 예상 잔액 **70000**, 예산 사용률 **150%**, 초과 경고. 날짜 순서를 거꾸로 입력해도 거래 목록 정렬 규칙은 그대로 적용한다.

## 검토·보완
- V0.1: 단일 add→저장 흐름 및 '파일 역방향 조회'를 임시 계획.
- P10 기존 정렬·generator 설계 결함, P11 안전한 update/delete, P12 사용 중 분류 삭제·예산 경고 검토.
- **P29 [높음]** 읽기/쓰기/계산 명령 동일 처리로 오해 → 3갈래 분리.
- **P30 [높음]** '최신순'이 입력순인지 날짜순인지 미확정 → 날짜 기준 확정, 비순차 입력 테스트 추가.
- V1.1: 흐름·불변식·예상 출력을 수정. 정확성은 04~05 실제 시험 전 NOT_VERIFIED.

[03-3 파일 구조](03-3-ARCHITECTURE.md) · [03-6 시험계획](03-6-TEST-EVIDENCE-PLAN.md).
