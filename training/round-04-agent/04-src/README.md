# B2-1 Round 04 — 개인 용돈 기입장 (CLI)

> 제2기 공식 미션: 나만의 용돈 기입장 프로그램 만들기. Python 3.10+ **표준 라이브러리만** 사용합니다. 기존 Archive 코드를 복제하지 않은 신규 Round 04 구현입니다.

## 처음 3분: 실행

저장소 루트에서 다음을 실행합니다.

```bash
cd training/round-04-agent/04-src
python3 --version
python3 -m budget_app --help
python3 -m budget_app --data-dir ./data category list
python3 -m budget_app --data-dir ./data add
python3 -m budget_app --data-dir ./data list --limit 5
```

- `--data-dir`: 내부 거래·분류·예산 3개 파일을 보관하는 폴더; 하위 명령 **앞에** 입력합니다.
- `add`: 날짜, income/expense, 분류, 양의 정수 금액, 메모, 태그를 순서대로 입력합니다.
- `--help`: 각 하위 명령 뒤에서도 사용 가능합니다.

## 명령 예시

```bash
python3 -m budget_app --data-dir ./data category add --name health
python3 -m budget_app --data-dir ./data category list
python3 -m budget_app --data-dir ./data list --limit 10
python3 -m budget_app --data-dir ./data search --from 2026-10-01 --to 2026-10-31 --category food --type expense --q lunch --tag meal
python3 -m budget_app --data-dir ./data summary --month 2026-10 --top 3
python3 -m budget_app --data-dir ./data budget set --month 2026-10 --amount 20000
python3 -m budget_app --data-dir ./data update --id <TRANSACTION_ID> --amount 3000
python3 -m budget_app --data-dir ./data delete --id <TRANSACTION_ID>
python3 -m budget_app --data-dir ./data category remove --name health
python3 -m budget_app --data-dir ./data export --out report.csv --month 2026-10
python3 -m budget_app --data-dir ./data export --out report.csv --month 2026-10 --overwrite
python3 -m budget_app --data-dir ./data import --from example.csv
```

## 영구 저장 방식과 순서

저장 형식: **JSONL(JSON Lines)** — 한 줄에 JSON 객체 하나씩 씁니다.

```text
data/
├── transactions.jsonl  # 거래 id/type/date/amount/category/memo/tags
├── categories.jsonl    # 등록된 카테고리
└── budgets.jsonl       # 월별 예산
```

- 거래는 **날짜 내림차순, 같은 날짜는 거래 ID 오름차순**으로 파일을 유지합니다. 입력한 순서가 아닌 거래 날짜로 정렬합니다. `list/search`는 이 파일을 하나씩 `yield`하는 제너레이터로 읽습니다.
- 거래 쓰기·수정·삭제는 파일 재작성과 같은 폴더의 임시 파일 → `os.replace`를 사용합니다. 대량 데이터의 쓰기 성능은 제한적이며 다중 파일 원자성까지 보장하지 않습니다.
- 거래 ID는 무작위 UUID 기반으로 발급하며 날짜 정렬에 의존하지 않습니다. 등록된 카테고리만 거래에 사용할 수 있습니다.
- 기본 카테고리: food, transport, rent, salary, etc.
- 월별 요약: 수입, 지출, 잔액(수입-지출), 카테고리 TOP, 예산 사용률과 초과 경고.

## CSV 가져오기·내보내기 스키마

UTF-8 인코딩, 반드시 헤더 포함.

```csv
date,type,category,amount,memo,tags
2026-10-30,expense,food,5000,점심,"lunch,meal"
```

| 이름 | 필수 | 설명 |
|---|---|---|
| date | 예 | YYYY-MM-DD의 실제 날짜 |
| type | 예 | income 또는 expense |
| category | 예 | 사전에 등록된 분류 |
| amount | 예 | 1 이상의 정수 |
| memo | 아니요 | 문자열 |
| tags | 아니요 | 쉼표 구분 태그, CSV 따옴표 인코딩 필요 |

- export는 `--month YYYY-MM` 또는 `--from YYYY-MM-DD --to YYYY-MM-DD`를 요구합니다. 기존 대상 파일은 기본적으로 보호하며 `--overwrite`를 지정할 때만 교체합니다. `--out`은 내부 data 디렉터리 밖도 허용합니다.
- import에 유효한 행과 불량 행이 섞이면 유효 행만 저장하고 `imported=N, skipped=M`과 행별 이유를 출력합니다. 일부 건너뛰었다면 종료 코드 2이며 완전 성공은 0입니다. CSV 헤더가 잘못되면 0건 반영합니다.
- 같은 CSV를 다시 import하면 동일 거래가 **새 거래로 중복 등록될 수 있습니다**. 중복 판단을 날짜/금액만으로 강제하지 않습니다.

## 정상·오류·검증

- 대화형 입력 EOF/중단, 손상된 카테고리·예산 필드, 필수 옵션 누락도 힌트를 출력하고 오류 코드로 종료합니다. 불량 import 행마다 사유와 해결 힌트를 출력합니다.
- 날짜가 잘못되거나 거래 ID가 없으면 사용자가 이해할 수 있는 `[오류]`, `[힌트]`를 표시합니다. 정상 종료 코드는 0, 오류는 2(비0)입니다.
- 실제 데이터나 API Key를 GitHub에 올리지 마세요. 테스트에는 가상 거래만 사용합니다.
- 외부 pip 패키지 설치 불필요. 내장 unittest 실행:

```bash
cd training/round-04-agent/04-src
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## 구조와 책임

- `models.py`: Transaction dataclass, 입력 형식 검사
- `storage.py`: JSONL 입출력과 안전한 파일 교체
- `service.py`: 거래·예산·카테고리·CSV 규칙
- `cli.py`: argparse 명령 및 공통 오류 데코레이터
- `tests/`: 정상·오류·경계·재시작 회귀 검증

현재 [WSL2 실제 독립 검증](../05-tests/WSL2-INDEPENDENT-VERIFICATION.md): Python 3.12.3에서 unittest 29/29·별도 CLI 61회 PASS. 사용자 직접 시연·동료평가·CLEAR는 미검증입니다.

## 공식 학습·평가와 증빙

[01 요구 추적](../01-requirements/REQUIREMENT-TRACEABILITY.md) → [03 설계](../03-design/README.md) → [05 검증](../05-tests/README.md) → [06 증빙](../06-evidence/README.md) → [07 평가](../07-evaluation/README.md). 운영체제·Python 버전·소스 커밋 SHA·시험 결과·증빙을 확인하기 전에는 미션 CLEAR로 기록하지 않습니다.
