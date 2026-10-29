# B2-1 03-6 — 재현 가능한 시험·증빙 계획 V1.1

> **모든 결과는 기대값(미실행)**. 공식 B2-1 PDF 4~8쪽, 내부 REQ-01~23 / 평가 E1~E4 기준. T-ID는 내부 식별자. 04 구현 승인 전 명령을 실행하지 않는다.

## 요구사항 시험 추적(예상)
| T-ID | REQ | 입력/시나리오 | 기대 결과(설계) |
|---|---|---|---|
| T-CMD | 01 | `python -m budget_app --help`, 각 하위 `--help` | 사용 예시 출력·exit 0 |
| T-MODEL | 02 | 필수 거래 필드 생성 | id/type/date/amount/category/memo/tags 확인 |
| T-ARCH | 03,21,23 | 파일 구조·시그니처·import 검사 | 2클래스·3모듈·타입힌트·Python3.10+·표준 라이브러리 |
| T-VAL | 04 | `2026-02-30`, `0`, `-10`, 알 수 없는 type/category | 사유+힌트, 오류 exit 비0 |
| T-PERSIST | 05 | 거래·분류·예산 저장→종료→재실행 | 3종 JSONL 파일·값 재조회 |
| T-DATADIR | 06 | `--data-dir` 임시 폴더 | 지정 폴더에만 3종 내부 파일 |
| T-INIT | 07 | 빈 데이터 폴더 첫 실행 | 초기화 또는 선행 분류 안내 |
| T-ADD | 08 | 유효 거래 추가 1건 | 생성된 고유 ID 출력, 저장 |
| T-LIST | 09 | 날짜 10/30 먼저·10/01 나중 입력, limit=2 | **10/30 → 10/01**, 실제 generator |
| T-UPDATE | 10,12 | 거래 날짜/금액 수정, 재조회 | ID 유지·필드 변경·정렬 위치 갱신·재시작 보존 |
| T-DELETE | 11,12 | 존재 ID 삭제→없는 ID 삭제 | 첫 삭제 성공, 없는 ID는 원본 불변·비0 |
| T-ATOMIC | 12 | 정상 교체·실패 주입·임시 파일 검사 | 정상 파일 유지, 중단 시 원본 보존/정리 |
| T-SEARCH | 13 | 날짜 역순 삽입+기간/type/category/q/tag 조건 | AND 조건 일치, **날짜 최신순**, generator |
| T-SUMMARY | 14 | 수입 100000, 지출 30000 동일 월 | 잔액 **70000**, 카테고리별 합계·TOP |
| T-BUDGET | 15 | 예산 20000, 지출 30000 | 사용률 **150%**, 초과 경고, 재실행 유지 |
| T-CATEGORY | 16 | category add/list/remove, 사용중 분류 제거 | 사용중 삭제 거부, 원본 유지 |
| T-CSV | 17 | 정상2+잘못된 날짜1행 import | imported=2, skipped=1, 원인·행번호, **exit=2 설계** |
| T-CSV-SCHEMA | 18 | `date,type,category,amount,memo,tags` + UTF-8 | 정확한 헤더, 인용부호/쉼표 정상 왕복 |
| T-DECORATOR | 19 | 실제 사용된 데코레이터 동작 | 공통 처리·오류 처리와 원함수의 연결 |
| T-ERROR | 20 | 없는 ID/잘못된 CSV/쓰기 권한 거부 | traceback 미노출·힌트·비0 |
| T-TYPES | 21 | 모델/함수 반환형 설명 | 타입 힌트와 실제 입력·출력 계약 일치 |
| T-README | 22 | README 원문 검토 | 실행/경로/저장형식/명령/CSV 스키마 |
| T-STD-LIB | 23 | 외부 패키지 import·Python 버전 확인 | 3.10+, 표준 라이브러리만 |

## 추가 경계·회귀(설계 제안)
- T-ORDER-EDGE: 날짜가 뒤섞인 입력, 같은 날짜의 서로 다른 ID, 수정으로 날짜를 변경, import 후 목록/검색 순서 확인.
- T-CSV-PARTIAL: 불량행 일부 반영의 비0 종료, 헤더 불량 때 0건 반영, 재시도 중복·중단 시 처리 범위 확인.
- T-DATA-SAFETY: `--out`이 내부 JSONL과 충돌할 때 거부, 지정된 외부 CSV 출력은 허용, 원본 데이터 유지.
- T-EXPORT-OVERWRITE: CSV 대상 파일이 이미 존재하면 기본 거부, 명시적 `--overwrite`에서만 저장; 기존 내부 파일은 변경하지 않음.
- T-ID-EDGE: 거래 ID 중복 확인, 거래 삭제 후 신규 거래 생성, 날짜 수정 후 ID 불변 확인.
- T-EMPTY: 빈 월 '데이터 없음', 예산은 존재하지만 거래가 없는 월.
- T-SCALE-DESIGN: 10만 건 처리의 재작성 비용/대안 **설명 평가**; 공식 성능 숫자 PASS로 사용하지 않는다.

## 05 테스트 수행 순간 06 증빙 기록
~~~text
TEST_ID:
REQ_ID / E_ID:
source Git SHA / 실행 위치 / Python 버전 / KST 시간:
입력 데이터(가상):
실행 명령:
EXPECTED (사전 기록):
ACTUAL stdout / stderr / exit code:
PASS|FAIL|NOT_VERIFIED / 불일치 원인:
Evidence 파일 위치 및 SHA:
재시험 기록 및 최종 결론:
~~~
테스트용 `--data-dir`와 `--out`은 분리하고 사용자의 실제 가계부 파일을 절대 사용하지 않는다.

## 3회 검토 이력 및 결론
- V0.1: 정상 add/list 위주 시험.
- P16 3파일 재실행, P17 요구별 연결, P18 종료 코드, P19 가상 증빙을 반영.
- **P34 [높음]** 정렬 반례 누락 → T-ORDER-EDGE.
- **P35 [높음]** CSV 부분 성공·종료코드와 덮어쓰기 경계 누락 → T-CSV-PARTIAL / T-DATA-SAFETY.
- **P36 [중간]** 정적 PASS와 실제 결과 혼동 → EXPECTED/ACTUAL 분리.
- **P37 [높음]** 최대 ID 삭제 후 재생성·덮어쓰기 위험 → T-ID-EDGE/T-EXPORT-OVERWRITE 추가.
- V1.1: 요구 ID 23개 모두 T-ID와 연결, 경계시험 추가. **실제 RUNTIME, EVIDENCE는 NOT_VERIFIED**.

[01 요구 추적](../01-requirements/REQUIREMENT-TRACEABILITY.md) · [03-8 통합 QA](03-8-INTEGRATED-REVIEW.md).
