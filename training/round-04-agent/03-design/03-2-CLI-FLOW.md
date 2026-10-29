# B2-1 03-2 — CLI·사용자·명령 흐름 설계 V1.0

> CLI(Command-Line Interface, 명령줄 인터페이스)는 터미널에 글자로 명령을 입력하는 방식. 설계/예상 명령이며 현재 신규 앱은 실행되지 않았다.

## 사용자가 보는 흐름 (Mermaid, 교육용)
~~~mermaid
flowchart TD
 A["터미널 명령 입력"] --> B{"명령과 옵션 올바른가?"}
 B -->|아니요| E["원인+해결 힌트 / 비0 종료"]
 B -->|예| C["입력 자료 검증"]
 C --> D{"유효성 PASS?"}
 D -->|아니요| E
 D -->|예| F["서비스→파일저장/조회"]
 F --> G["명령 결과/ID/요약 표시"]
~~~

## 명령 계약 제안 (공식 PDF 명령 범위 준수)
| 명령 | 핵심 입력 | 결과/예외 |
|---|---|---|
| --help, 각 하위 --help | 도움말 | 구문·옵션·예시 |
| add | 날짜/type/category/amount 대화형, memo/tags 선택 | 생성된 id / 오류 이유·힌트 |
| list | --limit N | 최신순 N건 |
| search | --from/--to/--category/--type/--q/--tag | 최신순 조건 일치 |
| update | --id 및 일부 변경 옵션(선택한 방식 A) | 변경/없는 id |
| delete | --id | 삭제/없는 id |
| category add/list/remove | 이름 | 등록/목록/사용중 삭제 보호 |
| budget set | --month YYYY-MM --amount 양수 | 저장/사용률 요약에 반영 |
| summary | --month YYYY-MM --top N | 수입/지출/잔액/카테고리 TOP N/초과 |
| import | --from CSV | 등록 수·건너뛴 수·이유 |
| export | --out CSV + --month 또는 --from/--to | UTF-8 header 포함 CSV |

**제안 선택:** update는 PDF의 허용안 A(옵션 기반)로 고정; 초기 카테고리는 허용안 A(기본값 자동 생성); 저장 형식은 JSONL 선택(03-3에서 이유). 명령/옵션은 -- 표기 채택. 모든 명령의 --help 출력 필요.

## 입문자 연습(실행 전 예상)
예시 입력(교육용/NOT_EXECUTED):
~~~text
python3 -m budget_app summary --month 2026-10 --top 3
~~~
예상: 해당 월 총 수입, 지출, 잔액, 지출 TOP 3(예산 있으면 사용률/경고). 현재 앱 출력이 아님. 존재하지 않는 월에는 "데이터 없음"으로 안내.

## 프롬프트 V0.1 → 보완 V1.0
V0.1: add/list 중심 CLI. P04 누락 명령 → 10 기능군 완비, P05 형식 상충 → -- 통일, P06 입력 오류/도움말 누락 → 하위 도움말+종료 코드 정책 추가. V1.0: 명령 계약과 정상·오류 흐름 확정(설계안).

## 검증·인계
REQ-01,08~18,20과 CLI 계약 비교. 입력값 보호(공백/경로 등)는 03-5에서 세부 처리. 다음 [03-3](03-3-ARCHITECTURE.md).

## 구현 전 CLI 계약 상세화(설계 선택)
- `python -m budget_app --data-dir ./data <command>`와 같이 전역 데이터 경로 옵션은 **하위 명령 앞에** 둔다. 모든 명령의 `--help`가 동작해야 한다.
- update는 `update --id <id> [--date ...] [--amount ...]` 형식의 옵션 기반을 선택하며, 바꾸지 않은 필드는 유지한다.
- `export --out report.csv --month 2026-10`처럼 사용자 지정 파일로 출력할 수 있다. 기본적으로 기존 파일 덮어쓰기 거부, `--overwrite` 지정 시 허용(내부 편의 옵션·공식 필수 아님).
- import는 `import --from import.csv`. 정상 행만 저장되고 불량 행이 있으면 imported/skipped/행별 원인 및 exit=2(설계 정책). 가져올 때 중복을 자동 제거한다고 주장하지 않는다.
- 명령별 입력·출력의 구분: list/search/summary는 내부 파일 읽기, export는 외부 CSV 쓰기, add/update/delete 등은 내부 파일 변경.
- 재사용 가능한 프롬프트·위험 검토는 [설계 프롬프트 기록](DESIGN-PROMPTS-AND-REVIEWS.md) 참조.
