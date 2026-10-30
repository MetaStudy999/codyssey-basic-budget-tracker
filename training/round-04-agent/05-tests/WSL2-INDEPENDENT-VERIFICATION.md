# Round 04 독립 검증 — 2026-10-30

**판정: WSL2_RUNTIME_PASS / unittest 29/29 PASS / CLI 61회 PASS.** 실행 주체는 Codex agent이며 사용자 직접 시연·동료평가·CLEAR는 NOT_VERIFIED다. 시작 clean main HEAD는 `9be11f664b5d32d35364b0e1c0595c2467263d12`, 작업 브랜치는 `feature/b2-1-round04-runtime-evidence-20261030`이다.

[환경·수정 내역·실제 출력·검증 경계](../06-evidence/WSL2-RUNTIME-2026-10-30.md), [CLI 원본](../06-evidence/WSL2-CLI-2026-10-30.txt), [unittest 원본](../06-evidence/WSL2-UNITTEST-2026-10-30.txt)을 함께 확인한다. 로그의 source SHA256은 테스트한 수정 작업 트리와 연결되며 시작 HEAD와 구분한다.

## 정적 감사

실제 읽은 기준: 루트 `b2-1-mission.md`, `b2-1-evaluation.md`, `01-requirements/REQUIREMENT-TRACEABILITY.md`. 실제 읽은 구현: `04-src/budget_app` 전체 6개 Python 파일, README, 기존 두 테스트 파일과 새 회귀 테스트. 이전 archive 구현이나 PASS를 신규 증빙으로 사용하지 않았다. 원본 공식 문서는 수정하지 않았다.

아래 경로·함수는 모두 `04-src/budget_app/` 기준이다. 시험 이름은 `04-src/tests/` 기준이며 CLI는 [독립 실행 스크립트](runtime_cli_verification.py)의 실제 subprocess assertion으로 확인했다.

| REQ | 구현·계약 | 이번 검증 근거 | 결과 |
|---|---|---|---|
| 01 | cli.build_parser/main, add=input, 긴 옵션·명령별 help | CLI root/하위/중첩 help 및 stdin add | PASS |
| 02 | models.Transaction frozen dataclass, 7필드·UUID | 생성 ID·수정 ID 유지, 모델 검증 시험 | PASS |
| 03 | Transaction/BudgetService/Store, cli/models/storage/service 분리 | 소스 정적 확인, 6모듈 AST | PASS (정적) |
| 04 | validate_date/type/amount, require_category | CLI 날짜·type·금액 0/음수/소수·category 오류 | PASS |
| 05 | Store: transactions/categories/budgets.jsonl | CLI 별도 프로세스 영속성, test_three_files_and_persistence | PASS |
| 06 | --data-dir, 기본 ./data | 모든 CLI 임시 --data-dir 사용, 기본값 정적 확인 | PASS |
| 07 | Store.__init__, 빈 category 기본 분류 초기화 | 신규 임시 폴더 첫 category list, 파일 3개 확인 | PASS |
| 08 | main add, BudgetService.add | 가상 대화형 add 3건·생성 ID | PASS |
| 09 | list → transaction_stream → stream yield | CLI --limit/최신순; test_out_of_order_input_still_lists_latest_date_first | PASS |
| 10 | update 옵션 방식, make_transaction 재검증 | 실제 --date/--amount/--memo/--tags 수정·동일 ID | PASS |
| 11 | delete, 없는 ID BudgetError | 실제 삭제·재시작 목록 및 없는 ID 두 명령 | PASS |
| 12 | Store.save 임시 파일·flush/fsync·os.replace·finally 정리 | test_atomic_replace_failure_keeps_old_transactions, import/export 실패 회귀 | PASS |
| 13 | search 조건별 필터, 정렬된 JSONL yield | CLI 6조건 동시 검색·최신순, generator 객체 시험 | PASS |
| 14 | summary 월별 합계·TOP·빈 달 | CLI 12000/3500/8500·study→food, 빈 달 | PASS |
| 15 | set_budget, summary 사용률·over | 실제 3000 예산·116.67% 경고·프로세스 재시작 | PASS |
| 16 | category add/list/remove, 사용 중 검사 | 추가·삭제 성공/차단·거래 삭제 뒤 분류 삭제 | PASS |
| 17 | import_csv 부분 성공, export_csv 월/기간 필수 | 정상 1/0, 혼합 2/1, 월3/기간2, 조건 누락 오류 | PASS |
| 18 | CSV_FIELDS 6개·UTF-8·csv.DictReader/Writer | 실제 한글/쉼표 태그 export 및 헤더 byte/read 확인 | PASS |
| 19 | @safe_cli 공통 오류 데코레이터 실제 적용 | 파일/입력 오류·EOF traceback 없음·exit=2 | PASS |
| 20 | BudgetError 원인/힌트, HelpfulParser, 오류 비0 | 정상0/오류2·필수 옵션·부분 성공·파일 오류 | PASS |
| 21 | 함수 시그니처·Iterator/Transaction 등 타입 힌트 | 소스 정적 확인; 런타임 정적 타입 검사기는 사용 안 함 | PASS (정적) |
| 22 | 04-src/README 실행·저장·update·CSV 정책 | 실제 문서와 CLI 명령 대조 | PASS (정적) |
| 23 | Python 3.10+ 문법·표준 라이브러리 | 3.12.3 실실행, ast.parse(feature_version=(3,10)), import 집합 확인 | PASS (범위 명시) |

이 표는 공식 기능의 구현·실행 근거이며, 평가 문항의 “사용자 자신의 말로 설명할 수 있는가”까지 PASS 처리하지 않는다. 선택 백업·반복 거래는 미구현이며 필수 범위를 확대하지 않았다.

## 시험 실행과 실패 경로

```bash
# 저장소 루트 — 현재 구현을 import하지 않고 실제 모듈 CLI를 별도 프로세스로 호출
PYTHONDONTWRITEBYTECODE=1 python3 training/round-04-agent/05-tests/runtime_cli_verification.py
cd training/round-04-agent/04-src
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

수정 전 전체 21/21 PASS → 독립 재현으로 EOF·category/budget 손상 traceback 및 argparse 힌트 누락 발견 → 최소 수정·회귀 8개 추가 → 전체 29/29 PASS, CLI 61회 PASS. 최종 unittest 로그는 전체 테스트를 다시 실행한 실제 출력이다.

새 `test_runtime_regressions.py`는 EOF/KeyboardInterrupt, 손상된 분류·예산, 인자 오류, 부분 import 힌트, export 교체 실패, import 저장 실패를 검증한다. 모든 거래는 임시 폴더의 가상 데이터다. 실패 후 JSONL 3개 byte 비교, 기존 CSV byte 비교, 임시 파일 청소를 검사한다. os.replace 실패는 mock 주입으로 실제 저장 실패 처리 분기를 실행하며 실제 디스크 고갈 실험이라고 표현하지 않는다.

list/search는 정렬된 JSONL을 순차 yield하므로 조회 메모리는 제한적이다. 반면 add/update/delete/import는 전체 거래를 메모리에 읽고 정렬·재작성하므로 쓰기 O(n log n), 메모리 O(n)이 병목이다. 10만 건 성능 측정·동시 쓰기 보장은 이번 검증에 포함하지 않았다. JSONL은 타입/태그 보존에 유리하고 CSV는 외부 교환에 유리해 내부 JSONL·외부 CSV를 선택했다.

사용자 직접 입력·독립 구술 설명, 학습 숙달, 공식 동료평가, 발표 파일 보관 확인은 미진행이다. **CLEAR 자동 선언 없음.**
