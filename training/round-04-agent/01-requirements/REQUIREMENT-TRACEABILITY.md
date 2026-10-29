# B2-1 공식 요구사항 전수 추적표 V1.0

> 유일한 요구 기준: 사용자가 제공한 2026 제2기 B2-1 미션 PDF, 1~10쪽. 평가 참고: 저장소 루트 b2-1-evaluation.md. 아래 REQ 번호는 **내부 추적 식별자**이며 공식 문항 번호가 아니다. 04 코드는 승인 전 미작성, 시험/증빙은 예상 설계만 기록한다.

## A. 핵심 기능/구조 (CORE)

| ID | 공식 요구 요지 | PDF | 03/04 설계·구현 예정 | 검증 예정 | 평가 연결 |
|---|---|---|---|---|---|
| REQ-01 | Python CLI 명령, 명령별 --help, add 대화형 입력, -- 긴 옵션 | 3,8 | 03-2 / cli | T-CMD | E1 |
| REQ-02 | 거래 id/type/date/amount/category/memo/tags, dataclass 준하는 모델 | 4 | 03-3 / models | T-MODEL | E2 |
| REQ-03 | 최소 클래스 2개, 모듈 3개, 역할 분리 | 4,6 | 03-3 / models·repositories·services·cli | T-ARCH | E2 |
| REQ-04 | 날짜·type·양수 금액·등록 카테고리 검증 | 4 | 03-5 / validation | T-VAL | E1 |
| REQ-05 | JSONL 또는 CSV 중 하나, 3개 이상 파일 영구 저장 | 1~4,8 | 03-3 / transactions·categories·budgets | T-PERSIST | E1,E4 |
| REQ-06 | 기본 ./data 권장, --data-dir 등으로 경로 변경 | 4 | 03-2·03-3 / storage config | T-DATADIR | E1 |
| REQ-07 | 첫 실행 파일 초기화 또는 안내, 빈 카테고리 정책 확정 | 4 | 03-3·03-5 | T-INIT | E1 |
| REQ-08 | add: 입력 대화형, 등록된 카테고리, 저장 id 반환 | 4 | 03-2·03-4 / add | T-ADD | E1 |
| REQ-09 | list: 최신순·--limit, 파일 스트리밍 제너레이터 | 4~5 | 03-4 / list·yield | T-LIST | E1,E3 |
| REQ-10 | update: --id 옵션 또는 대화형 중 한 방식 고정 | 5 | 03-2·03-4 / update | T-UPDATE | E1,E2 |
| REQ-11 | delete --id 및 없는 id 오류 | 5 | 03-4·03-5 / delete | T-DELETE | E1 |
| REQ-12 | update/delete 파일 안전성 고려 | 5 | 03-4·03-5 / rewrite | T-ATOMIC | E2 |
| REQ-13 | search: 기간·카테고리·type·메모 키워드·태그, 최신순 스트리밍 | 5 | 03-2·03-4 / search | T-SEARCH | E1,E3 |
| REQ-14 | summary 월 수입/지출/잔액·카테고리 TOP N·자료없음 | 5 | 03-4 / summary | T-SUMMARY | E1 |
| REQ-15 | budget set 월별 예산, 사용률과 초과 경고, 영구 저장 | 5~6 | 03-4 / budget | T-BUDGET | E1 |
| REQ-16 | category add/list/remove; 사용 중인 분류 삭제 정책 | 6 | 03-4·03-5 / category | T-CATEGORY | E1 |
| REQ-17 | CSV import 전체/부분 유효성 처리, export 월/기간 조건 | 6 | 03-2·03-5 / import·export | T-CSV | E1,E4 |
| REQ-18 | CSV 스키마 date/type/category/amount/memo/tags, UTF-8 헤더 | 6 | 03-3·03-5 / csv | T-CSV-SCHEMA | E1,E4 |
| REQ-19 | 공통 관심사 데코레이터 1개 이상 실제 적용 | 6 | 03-3 / utils | T-DECORATOR | E3 |
| REQ-20 | 오류는 원인+해결 힌트, traceback 미노출, 오류 종료 비0 | 6,8 | 03-5 / errors | T-ERROR | E1 |
| REQ-21 | 타입 힌트 적용 및 계약 설명 | 1,3 | 03-3·03-7 / signatures | T-TYPES | E3 |
| REQ-22 | README 실행·저장 위치/형식·명령 예·CSV 스키마 | 3 | 03-6 / 04-src README | T-README | E1,E2 |
| REQ-23 | Python 3.10+, 표준 라이브러리만, 외부 pip 패키지 금지 | 7~8 | 03-3 / 환경 | T-STD-LIB | E1 |

## B. 선택 기능 (BONUS — CORE 완료 뒤)
| ID | 보너스 | PDF |
|---|---|---|
| BON-01 | 타임스탬프 백업 명령 | 7 |
| BON-02 | 반복 거래 등록·자동 생성 | 7 |
| BON-03 | 표 형태 문자열 정렬 | 7 |
| BON-04 | 임시 파일과 rename 기반 원자성 강화 | 7 |

안전한 임시 파일 교체는 REQ-12의 권장 구현으로 채택 가능하지만, BON-04 자체를 미션 필수 평가항목이라고 주장하지 않는다.

## C. 공식 표기 차이·해석 경계
- PDF 3쪽은 --help / --limit / --from 등 이중 하이픈을 구체적으로 요구하므로 이 표기를 목표로 한다. PDF 8쪽 제약 문장의 단일 '-'-표기와 차이가 있어 **구체적인 3쪽 예시를 채택한 설계 판단**으로 기록한다. 공식 정오표로 선언하지 않는다.
- PDF 6쪽 import/export의 파일 인자 표시가 문자 깨짐으로 보이는 부분은 앞쪽 2쪽 예시와 나머지 문장에서 --from, --out CSV를 확인하여 설계한다. 확신할 수 없는 문구는 의도적으로 재구성하지 않는다.
- 거래 최신순의 동률 처리·ID 발급 알고리즘·부분성공/롤백 등 상세 정책은 PDF에서 일률적으로 지정하지 않는다. 03단계에서 선택하고 문서화한다.
- 기존 평가표의 10만 건 확장성 질문은 기존 E4의 평가 항목이며 공식 필수 구현 성능 요구로 확대하지 않는다.

## D. 요구→구현→시험→증빙→평가 규칙
REQ마다 실제 구현이 완료되면 파일·함수·Git SHA를 채우고, T-* 시험에 예상/실제 출력과 종료코드를 구분해 기록한다. 06-evidence에는 실행한 세션의 시간·명령·환경·SHA·결과만 둔다. 07-evaluation은 사람이 실제 독립적으로 확인한 판정만 PASS.

## E. 검토 범위/미완료
PDF 본문을 기준으로 항목을 전수 분리했으나 아직 **런타임 실증 전**이다. 품질 게이트 QG-01의 문서 매핑과 실제 구현·실습·증빙 연결은 분리 판정한다.
