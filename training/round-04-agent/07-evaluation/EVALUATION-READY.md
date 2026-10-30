# B2-1 Round 04 — 평가 준비 체크리스트 (독립 수행 전)

> **EVALUATION_PREPARED / USER_DEMONSTRATION_NOT_VERIFIED**. 실제 동료평가 PASS는 본 문서나 자동 시험만으로 확정하지 않습니다. 원본: `b2-1-evaluation.md` (기존 E1~E4).

사용자 WSL2에서 Agent Codyssey를 통한 Codex agent가 Python 3.12.3으로 unittest **29/29**, 별도 프로세스 CLI **61/61 PASS**를 확인했습니다. 임시 가상 데이터로 정상·오류·파일 보존·3종 JSONL 재시작 영속성을 검증했으며, [런타임 증빙](../06-evidence/WSL2-RUNTIME-2026-10-30.md), [unittest 원본](../06-evidence/WSL2-UNITTEST-2026-10-30.txt), [CLI 원본](../06-evidence/WSL2-CLI-2026-10-30.txt)과 연결합니다. 로그의 소스 6개 SHA256은 현재 수정 파일과 일치합니다.

과거 main SHA `5d62bd97a1c54a642ed0c9dc11455eed761ec718`의 GitHub Actions Python3.10/3.12 각각 21/21 PASS는 별도 기록입니다. 현재 수정 코드 CI는 PR 후 재실행 전까지 **NOT_VERIFIED**입니다. 사용자 직접 독립 시연·자기 말 설명·공식 동료평가는 미진행이며 **CLEAR=NOT_VERIFIED**입니다.

## 사용자 직접 독립 시연 순서 (WSL2 agent 실행 완료와 별도)
1. `python3 --version` 3.10 이상 확인 → `cd training/round-04-agent/04-src`.
2. `python3 -m budget_app --help`와 하위 `--help` 설명.
3. **반드시 시험용 데이터 폴더**에서 category add/list → add 대화형 → list/search → update/delete.
4. summary/budget set과 예산 초과 경고, export/import CSV 정상·불량 행, 종료 코드.
5. 터미널 종료→프로그램 재실행 후 3 JSONL 파일 거래·분류·예산 복구 확인.
6. 파일 읽기(generator/yield), 오류 데코레이터, type hints, 파일 교체 코드 설명 및 새로운 질문 응답.

## 공식 평가 4영역을 코드·시험·설명에 연결
| 평가 | 평가자가 확인하는 것 | 관련 신규 코드 | 자동 검증 | 사용자 독립 시연 |
|---|---|---|---|---|
| E1 기능·예외 | 10기능군, CSV·에러 힌트·비0 종료 | cli.py/service.py | [WSL2 unit 29/29·CLI 61/61 PASS](../05-tests/RUNTIME-TEST-RESULTS.md) | NOT_VERIFIED |
| E2 모듈·클래스 | 2클래스 이상, 3모듈 이상, 안전한 재작성 | models.py/storage.py/service.py | 구조 정적 확인·3종 영속성·교체 실패 주입 PASS | NOT_VERIFIED |
| E3 generator/decorator/types | list/search 스트리밍, 공통 오류 처리, 타입계약 | storage.py/cli.py/models.py | generator·CLI 에러 시험 PASS, 타입 힌트 정적 확인 | NOT_VERIFIED |
| E4 저장·확장 | JSONL/CSV 비교, 10만 건 시 병목, CSV 일부 오류 대응 | storage.py/service.py/README.md | 부분 성공·재시작 PASS, 10만 건 성능 미검증 | NOT_VERIFIED |

## 평가 답변 (암기본이 아닌 설명 가이드)
- WHAT(무엇): Python 표준 라이브러리로 파일 기반 개인 가계부를 만들었습니다.
- WHY(왜): 재시작해도 거래 데이터가 남고, 거래·예산·카테고리를 분리해 관리하기 위해서입니다.
- HOW(어떻게): CLI→Service→Store→JSONL 순서로 처리하고, 정렬된 파일을 generator로 읽습니다.
- VERIFY(검증): 과거 main CI Ubuntu Python3.10·3.12 각 21/21 PASS, 현재 WSL2 Python3.12.3 agent 실행 unit 29/29·별도 CLI 61/61 PASS. 수정 코드 CI·사용자 직접 시연·자기 말 설명은 미검증입니다.
- LIMITATION(한계): JSONL 전체 재작성은 거래가 10만 건 이상으로 늘면 느려질 수 있고, 여러 파일을 한 번에 원자적으로 교체하지는 않습니다.

## 10초 / 30초 / 1분 설명 훈련
- 10초: "CLI로 거래를 기록하고 3개 JSONL 파일에 저장해 재시작해도 유지하는 가계부입니다."
- 30초: 위 내용 + 모델·서비스·저장소 분리 이유 + 파일 수정 시 안전한 교체 설명.
- 1분: 실제 add→list→budget→summary 흐름 + 이상 입력·CSV 부분 성공 처리 + 테스트 근거 + 한계.

## 공식 동료평가 주의
평가자·피평가자가 같은 자리에서 피평가자 PC로 평가한다는 별도 동료평가 규칙 준수. AI가 대신 평가를 완료했다고 주장하지 않는다.

**현상태:** WSL2 agent 실행 PASS·평가 준비 완료. 실제 동료평가·사용자 직접 독립 시연·자기 말 설명은 NOT_VERIFIED, 슬라이드 바이너리 GitHub 업로드 미완료, CLEAR=NOT_VERIFIED.
