# B2-1 03-6 — 시험 ID·입력·예상 결과·증빙 계획 V1.0

> 아래 T-ID는 내부 검증계획이지 실제 수행 PASS가 아님. 05에서 검사와 동시에 06 Evidence를 작성하며 예상과 실제를 분리 기록한다.

## 시험 목록
| 테스트 ID | 요구 ID | 입력/상황 | 예상 결과 | 실제 증거(미실행) |
|---|---|---|---|---|
| T-CMD | 01 | 루트/각 하위 --help | 도움말·0 종료 | NOT_VERIFIED |
| T-MODEL | 02 | 거래 필드·날짜·금액 | dataclass/정확한 타입 | NOT_VERIFIED |
| T-ARCH | 03,21,23 | 코드/의존성 정적 검사 | 2클래스·3모듈·type hint·stdlib | NOT_VERIFIED |
| T-VAL | 04 | 잘못된 날짜/0·음수/type/category | 사유+힌트·비0 | NOT_VERIFIED |
| T-PERSIST | 05 | add/category/budget 후 종료·재시작 | 3파일 저장·동일 데이터 재조회 | NOT_VERIFIED |
| T-DATADIR | 06 | --data-dir 임시폴더 | 그 위치의 3파일만 생성 | NOT_VERIFIED |
| T-INIT | 07 | 파일 없는 새 경로 | 자동 초기화 또는 안내 | NOT_VERIFIED |
| T-ADD | 08 | 정상 수입·지출 입력 | id 출력·거래 재조회 | NOT_VERIFIED |
| T-LIST | 09 | 다른 날짜 거래·--limit 2 | 최신순 2개, generator | NOT_VERIFIED |
| T-UPDATE | 10,12 | --id 수정, 재시작 | 선택 필드 변경·나머지 보존 | NOT_VERIFIED |
| T-DELETE | 11,12 | 존재/없는 ID 삭제 | 삭제/정상 오류 분리 | NOT_VERIFIED |
| T-ATOMIC | 12 | 안전 재작성+임시파일 확인 | 최종 파일 유효·데이터 보전 | NOT_VERIFIED |
| T-SEARCH | 13 | 기간/카테고리/type/q/tag 조합 | 최신순 AND 필터·generator | NOT_VERIFIED |
| T-SUMMARY | 14 | 수입·지출·빈 월 | 정확한 총액/잔액/TOP·자료없음 | NOT_VERIFIED |
| T-BUDGET | 15 | 예산 초과→summary | 비율·경고·재실행 보존 | NOT_VERIFIED |
| T-CATEGORY | 16 | add/list/remove + 사용중 제거 | 카테고리 목록·안전한 삭제 거절 | NOT_VERIFIED |
| T-CSV | 17 | 정상+불량 행 import, 조건 export | 처리/건너뜀 건수·사유 | NOT_VERIFIED |
| T-CSV-SCHEMA | 18 | UTF-8 헤더/컬럼 검사 | 공식 6열 스키마 | NOT_VERIFIED |
| T-DECORATOR | 19 | 데코레이터 감싼 명령 | 실제 공통 동작 확인 | NOT_VERIFIED |
| T-ERROR | 20 | 오류 유발 | traceback 대신 힌트, 비0 | NOT_VERIFIED |
| T-TYPES | 21 | 함수 시그니처 검사 | 타입 힌트+설명 | NOT_VERIFIED |
| T-README | 22 | README 문서 검토 | 실행·저장·명령·CSV 명시 | NOT_VERIFIED |
| T-STD-LIB | 23 | import 목록/버전 | Python3.10+ stdlib only | NOT_VERIFIED |

## 05/06 시험 기록 형식
T-ID / REQ-ID / 기준 PDF쪽 / Git SHA / OS·Python버전 / 실행시간(서울) / 사용 명령 / 입력(가상 데이터) / 기대값 / 실제 stdout·stderr·exit code / 비교 PASS·FAIL / Evidence 파일경로·SHA / 수행자 / 수정·재검증.

## 검증 실행 순서(개발 승인 후)
Preflight: 현재 브랜치/경로·Python 3.10+·데이터 폴더와 권한 확인 → 정적 파싱·도움말 → 단위 시험 → CLI 정상 흐름 → 오류/경계 → 프로세스 종료·재시작·3파일 복원 → CSV·개별 재검증 → 평가 설명. 원본 데이터와 충돌하지 않도록 테스트 전용 임시 디렉터리 사용.

## 입력·출력의 엄격한 구분
~~~text
EDUCATIONAL_EXAMPLE / NOT_EXECUTED
입력: 2026-10-01 expense food 5000
예상: 생성된 거래 id가 나오고 파일에 저장
실제: (현재 없음)
~~~
기술 보조 그림을 실제 실행 캡처로 제출하지 않는다.

## V0.1→위험 검토→V1.0
V0.1: 정상 add/list만 테스트. P16 재시작 영속성 누락 → T-PERSIST, P17 기능·평가 연결 약함 → REQ 23개 전수, P18 오류 종료·실제 SHA 누락 → T-ERROR/기록 형식, P19 비밀정보 노출 → 가상 데이터. V1.0: 기능·구조·오류·증거 전수 매핑.

## 상태/인계
시험 설계(DOC), 실제 실행(RUNTIME), 증빙(EVIDENCE)의 상태를 개별 보존. 05 시험을 시작하는 사용자 승인 미획득. 다음 [03-7](LEARNING-DESIGN.md).
