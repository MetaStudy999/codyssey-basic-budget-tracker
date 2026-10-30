> **2026-10-25 신규 미션 작성 경로(B2-1):** [`training/round-04-agent/`](training/round-04-agent/README.md) — 신규 코드는 `training/round-04-agent/04-src/`에만 작성합니다. 기존 Round 01~03 및 루트의 내용은 과거 수행·참고 이력으로 보존합니다. **현재 Round 04는 사용자 요청으로 구현·로컬 검증이 승인되었고 WSL2 런타임 PASS(29개 unittest·61회 CLI)입니다. 사용자 직접 시연·동료평가·CLEAR는 NOT_VERIFIED**입니다. 중앙 기준: [15개 미션 신규 실행 허브](https://github.com/MetaStudy999/codyssey-basic/tree/main/training/round-04-agent).

> **자료 보관:** 기존 Round 01·02는 [`training/archive/`](training/archive/README.md)로 이동했으며 파일 원본을 보존합니다.

# Codyssey Basic B2-1 — 나만의 용돈 기입장 프로그램 만들기

## 현재 훈련 상태

- 구분: **필수 미션 (REQUIRED)**
- Round: **Round 04 Agent — 구현·WSL2 검증 완료, 인계 준비**
- Runtime Mission 상태: **WSL2_RUNTIME_PASS — Python 3.12.3, unittest 29/29, 별도 CLI 61회**
- 사용자 직접 시연·학습 숙달·동료평가·CLEAR: **NOT_VERIFIED**
- 과거 R01/R02 및 Phase A Reference: **REFERENCE_ONLY / CORE READY (과거 기록)**

[실제 WSL2 증빙](training/round-04-agent/06-evidence/WSL2-RUNTIME-2026-10-30.md)과 [독립 검증·요구별 감사](training/round-04-agent/05-tests/WSL2-INDEPENDENT-VERIFICATION.md)를 확인하세요. 실제 가상 데이터로 오류·영속성·CSV·파일 보존을 검증했습니다. 사용자 직접 시연과 동료평가는 미진행이며 CLEAR를 선언하지 않습니다.

## 공식 원본

- `b2-1-mission.pdf`
- `b2-1-mission.md`
- `b2-1-evaluation.md`

공식 원본은 수정하지 않습니다.

## Reference 시작 위치

- `training/archive/round-01-clear/REFERENCE-STATUS.md` — Phase A 자체감사 결과
- `training/archive/round-01-clear/REFERENCE-BUILD.md` — 기준 구현/검증 설계
- `training/archive/round-01-clear/BEGINNER-GUIDE.md` — Phase C 단계별 실습
- `training/archive/round-01-clear/CHECKLIST.md` — Mission/Evaluation/CLEAR Gate
- `training/archive/round-01-clear/reference/README.md` — Reference 앱 사용법

## 기술 스택

- Python 3.10+
- Python standard library only
- argparse CLI
- dataclass / type hints
- JSONL persistence
- CSV import/export
- unittest

## 로컬 실행

Repository 루트에서:

```bash
cd training/round-04-agent/04-src
PYTHONDONTWRITEBYTECODE=1 python3 -m budget_app --help
```

별도 실습 데이터 폴더 권장:

```bash
B2_DATA=$(mktemp -d)
PYTHONDONTWRITEBYTECODE=1 python3 -m budget_app --data-dir "$B2_DATA" category list
```

## 저장 파일 위치와 형식

기본 위치는 `./data`이며 `--data-dir`로 변경할 수 있습니다. Round 04 내부 저장 포맷은 JSONL입니다. 임시 실증의 데이터는 매 실행 새 폴더에 만들고 정리합니다.

```text
data/
├── transactions.jsonl
├── categories.jsonl
└── budgets.jsonl
```

첫 실행에서 category 파일이 비어 있으면 기본 카테고리 `food`, `transport`, `rent`, `salary`, `etc`를 생성합니다.

## 주요 명령

```bash
python3 -m budget_app add
python3 -m budget_app list --limit 10
python3 -m budget_app search --from 2026-08-01 --to 2026-08-31 --category food
python3 -m budget_app summary --month 2026-08 --top 3
python3 -m budget_app budget set --month 2026-08 --amount 500000
python3 -m budget_app category add --name health
python3 -m budget_app category list
python3 -m budget_app category remove --name health
python3 -m budget_app update --id TX-000001 --amount 18000 --memo "저녁"
python3 -m budget_app delete --id TX-000001
python3 -m budget_app export --out export.csv --month 2026-08
python3 -m budget_app import --from import.csv
```

`--data-dir`은 main command 앞에 둡니다.

```bash
python3 -m budget_app --data-dir "$B2_DATA" list --limit 10
```

## update 방식

공식 허용안 중 **옵션 기반 방식**으로 고정했습니다. 지정하지 않은 필드는 기존 값을 유지합니다.

## CSV import/export 스키마

UTF-8, 헤더 포함:

| column | required | 설명 |
|---|---|---|
| date | Y | `YYYY-MM-DD` |
| type | Y | `income` / `expense` |
| category | Y | 등록된 category |
| amount | Y | 양수 정수 |
| memo | N | 문자열 |
| tags | N | 쉼표 구분 문자열 |

Import는 정상 행은 저장하고 깨진 행은 건너뛴 뒤 `imported`, `skipped`, 행별 원인을 출력하는 부분 성공 정책을 사용합니다.

## 과거 Reference 자체감사 기록 (신규 증빙과 구분)

- transactions/categories/budgets **3종 재오픈 persistence 테스트**
- list/search 실제 generator 객체 확인
- 날짜/type/category/0·음수 amount 검증
- missing update/delete ID 오류
- atomic rewrite 뒤 temp 잔존 여부와 재오픈 결과
- import broken-row/row reason, export date range/조건 검사
- verify가 `compileall` 대신 AST parse를 사용하여 Repository에 bytecode cache를 만들지 않음
- root/subcommand help, long option `--`, README/저장 구조를 자동 점검

## 테스트/검증

```bash
PYTHONDONTWRITEBYTECODE=1 python3 training/round-04-agent/05-tests/runtime_cli_verification.py
```

또는 unit test만:

```bash
cd training/round-04-agent/04-src
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## 핵심 설계

- `models.py`: 데이터 구조
- `storage.py`: JSONL 파일 I/O·generator·원자적 교체
- `service.py`: 거래·분류·예산·CSV 비즈니스 규칙
- `cli.py`: 사용자 명령/입출력·공통 오류 데코레이터

list/search는 generator streaming으로 처리하며, update/delete는 임시 파일을 완전히 쓴 뒤 `os.replace()`로 원자적 교체합니다.

## CLEAR 원칙

**Round 04 Runtime: WSL2_RUNTIME_PASS / CLEAR: NOT_VERIFIED**

이번 agent 실행 결과와 사용자 직접 시연·설명·동료평가를 구분합니다. 과거 Reference의 CLEAR를 현재 Round에 전용하지 않습니다. 이번 PR 준비는 지정 feature 브랜치 커밋과 일반 push까지 승인되었으며 클라우드 배포는 범위 밖입니다.
