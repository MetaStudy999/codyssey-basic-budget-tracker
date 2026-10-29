# B2-1 Round 04 — 평가 준비 체크리스트 (독립 수행 전)

> **EVALUATION_PREPARED / USER_DEMONSTRATION_NOT_VERIFIED**. 실제 동료평가 PASS는 본 문서나 자동 시험만으로 확정하지 않습니다. 원본: `b2-1-evaluation.md` (기존 E1~E4).

## 실제 시연 순서 (사용자 WSL2에서 수행 후 Evidence 확보)
1. `python3 --version` 3.10 이상 확인 → `cd training/round-04-agent/04-src`.
2. `python3 -m budget_app --help`와 하위 `--help` 설명.
3. **반드시 시험용 데이터 폴더**에서 category add/list → add 대화형 → list/search → update/delete.
4. summary/budget set과 예산 초과 경고, export/import CSV 정상·불량 행, 종료 코드.
5. 터미널 종료→프로그램 재실행 후 3 JSONL 파일 거래·분류·예산 복구 확인.
6. 파일 읽기(generator/yield), 오류 데코레이터, type hints, 파일 교체 코드 설명 및 새로운 질문 응답.

## 공식 평가 4영역을 코드·시험·설명에 연결
| 평가 | 평가자가 확인하는 것 | 관련 신규 코드 | 자동 검증 | 사용자 독립 시연 |
|---|---|---|---|---|
| E1 기능·예외 | 10기능군, CSV·에러 힌트·비0 종료 | cli.py/service.py | [CI 21 PASS](../05-tests/RUNTIME-TEST-RESULTS.md) | NOT_VERIFIED |
| E2 모듈·클래스 | 2클래스 이상, 3모듈 이상, 안전한 재작성 | models.py/storage.py/service.py | 원자적 파일 테스트 PASS | NOT_VERIFIED |
| E3 generator/decorator/types | list/search 스트리밍, 공통 오류 처리, 타입계약 | storage.py/cli.py/models.py | generator·CLI 에러 시험 PASS | NOT_VERIFIED |
| E4 저장·확장 | JSONL/CSV 비교, 10만 건 시 병목, CSV 일부 오류 대응 | storage.py/service.py/README.md | 부분 성공·재시작 PASS | NOT_VERIFIED |

## 평가 답변 (암기본이 아닌 설명 가이드)
- WHAT(무엇): Python 표준 라이브러리로 파일 기반 개인 가계부를 만들었습니다.
- WHY(왜): 재시작해도 거래 데이터가 남고, 거래·예산·카테고리를 분리해 관리하기 위해서입니다.
- HOW(어떻게): CLI→Service→Store→JSONL 순서로 처리하고, 정렬된 파일을 generator로 읽습니다.
- VERIFY(검증): CI Ubuntu Python3.10·3.12에서 각 21개 테스트 PASS. 사용자 WSL2 시연은 별도 확인이 필요합니다.
- LIMITATION(한계): JSONL 전체 재작성은 거래가 10만 건 이상으로 늘면 느려질 수 있고, 여러 파일을 한 번에 원자적으로 교체하지는 않습니다.

## 10초 / 30초 / 1분 설명 훈련
- 10초: "CLI로 거래를 기록하고 3개 JSONL 파일에 저장해 재시작해도 유지하는 가계부입니다."
- 30초: 위 내용 + 모델·서비스·저장소 분리 이유 + 파일 수정 시 안전한 교체 설명.
- 1분: 실제 add→list→budget→summary 흐름 + 이상 입력·CSV 부분 성공 처리 + 테스트 근거 + 한계.

## 공식 동료평가 주의
평가자·피평가자가 같은 자리에서 피평가자 PC로 평가한다는 별도 동료평가 규칙 준수. AI가 대신 평가를 완료했다고 주장하지 않는다.

**현상태:** 문서 준비는 완료, 실제 동료평가 및 사용자 자기 말 시연은 NOT_VERIFIED.
