# B2-1 03-3 — 구조·모듈·파일 저장 설계 V1.0

> 실제 소스는 개발 승인 후 training/round-04-agent/04-src/에만 작성. 아래 구조는 미구현 설계안.

## 한 문장
명령 받는 사람(CLI), 규칙 검사하는 사람(Service), 파일 담당(Repository), 거래 양식(Model)을 나누면 변경 범위를 좁힐 수 있다.

~~~text
training/round-04-agent/04-src/
  budget_app/
    __init__.py
    __main__.py
    cli.py             # argparse / input / 출력
    models.py          # Transaction dataclass
    repositories.py    # JSONL 3파일 읽기·쓰기
    services.py        # 거래·예산·분류 비즈니스 규칙
    utils.py           # 제너레이터/공통 데코레이터(또는 역할별 분리)
    errors.py          # 안전한 오류 표현/종료
  tests/               # 테스트 설계(실행은 별도 승인)
  README.md            # 실행·경로·CSV 스키마
~~~

## 역할과 데이터 흐름
~~~mermaid
flowchart LR
 U["사용자 터미널"] --> C["CLI"]
 C --> S["서비스 규칙/검증"]
 S --> M["거래 모델·타입힌트"]
 S --> R["저장소(Repository)"]
 R --> F1["transactions.jsonl"]
 R --> F2["categories.jsonl"]
 R --> F3["budgets.jsonl"]
 C --> O["결과/오류/종료코드"]
~~~

- JSONL(JavaScript Object Notation Lines)은 한 줄당 JSON 객체를 쓰는 텍스트 저장 형식. 파일을 줄씩 읽는 스트리밍에 적합. 다만 임의 위치 변경·역방향 최신순 처리에는 별도 알고리즘 필요.
- CSV(Comma-Separated Values)는 쉼표로 열을 구분하는 파일. 외부 교환은 고정 CSV 스키마를 사용한다.
- 데이터 저장: Transactions, Categories, Budgets를 서로 다른 파일로 저장. 명령 전역 --data-dir(기본 ./data)을 CLI에서 전달. 디렉터리/파일 생성·권한 실패 처리 필요.
- 모델 필드: id, type(income/expense), date, amount(양수), category, memo/tags. 클래스 최소 2개, 모듈 최소 3개 충족 계획. 타입 힌트 예제의 의미는 03-7에서 설명.
- 저장원자성: update/delete는 원본 전체를 읽고 덮어쓰기보다 같은 디렉터리의 안전한 임시 파일을 작성한 뒤 os.replace로 교체하는 방법을 **권장 설계**로 선택한다. 다중 파일 전체의 트랜잭션을 보장하는 것은 아님.

## 2가지 저장 형식 비교(평가 E4)
| 비교 | JSONL(내부 선택안) | CSV |
|---|---|---|
| 장점 | 객체·태그 구조 표현, 행 단위 순차 처리 | 스프레드시트 호환, 표형식 직관 |
| 한계 | 비전문가 직접 편집 불편, 대량 조회 시 비용 | 쉼표·따옴표·태그 구조 파싱 주의 |
| 사용처 | 거래/분류/예산 3개 내부 파일 | 공식 import/export 교환 |

## V0.1 검토→V1.0
V0.1: 단일 파일 가계부 제안. P07 책임 혼재 → 4계층/2클래스 이상; P08 저장 내구성 → 3파일·재시작·임시 교체; P09 보안·환경 → 기본 경로/--data-dir·표준 라이브러리 고정. V1.0 구조안 채택.

## 검증·인계
REQ-02,03,05,06,07,12,19,21,23 확인. 소스/함수의 실제 SHA는 미래 04~06에서 기록. 다음 [03-4](03-4-DATA-CONTROL-FLOW.md).
