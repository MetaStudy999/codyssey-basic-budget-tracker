# Round 04 WSL2 실제 런타임 증빙 — 2026-10-30

실행 주체는 이 작업의 Codex agent이다. **WSL2_RUNTIME_PASS**, 사용자 직접 시연·학습 숙달·공식 동료평가는 **NOT_VERIFIED**, CLEAR는 **NOT_VERIFIED**다. 아래 결과는 실제 실행이며 예상 출력이 아니다.

- 시작: `main`, HEAD `9be11f664b5d32d35364b0e1c0595c2467263d12`, `git status --short` 출력 없음(clean).
- 브랜치: 존재 여부 확인 후 `feature/b2-1-round04-runtime-evidence-20261030` 신규 생성. main 직접 커밋·병합·push 없음.
- 환경 실측: Ubuntu 24.04.4 LTS, `Linux 6.18.33.2-microsoft-standard-WSL2`, Python 3.12.3.
- CLI 시작 시각: `2026-10-30T09:21:22.939890+00:00` (KST 18:21:22). 최종 unittest 시각은 원본 로그 첫 줄에 기록.
- 검증 대상: 위 HEAD 기반의 수정된 작업 트리. CLI 원본 로그 첫 부분에 `budget_app/*.py` 6개 SHA256 기록. 시작 HEAD가 수정 후 소스 SHA라고 주장하지 않는다. 결과를 담은 로컬 커밋은 `git log -1`로 확인한다.
- 데이터: `tempfile.mkdtemp`/`TemporaryDirectory` 아래 가상 거래만 사용. 실제 사용자 데이터·비밀·외부 서비스 미사용. CLI 임시 폴더 삭제 결과 `True`. 테스트는 전부 `PYTHONDONTWRITEBYTECODE=1`로 실행.

## 원본 출력과 재현

- [CLI 실제 출력](WSL2-CLI-2026-10-30.txt): 명령, 가상 stdin, stdout/stderr, 종료 코드, 파일 보존 assertion. 도움말은 첫 줄만 보관했다고 명시하며 다른 결과 출력은 그대로 기록.
- [최종 unittest 실제 출력](WSL2-UNITTEST-2026-10-30.txt): 29개 이름·결과, `Ran 29 tests`, `OK`, `exit=0`.
- [독립 검증 절차·정적 감사](../05-tests/WSL2-INDEPENDENT-VERIFICATION.md).

저장소 루트에서 재현한다. 실행마다 새로운 임시 폴더와 UUID를 생성하므로 경로·ID·시각은 달라진다.

```bash
PYTHONDONTWRITEBYTECODE=1 python3 training/round-04-agent/05-tests/runtime_cli_verification.py
cd training/round-04-agent/04-src
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## 실측 결과

| 범위 | 실제 확인 | 판정 |
|---|---|---|
| 시작·종료 | root/10개 명령/중첩 4개 명령 help, 정상 exit=0, 오류 exit=2, traceback 없음 | PASS |
| add/list/search | 대화형 가상 입력·생성 ID, --limit, 역순 날짜 입력 후 최신순, 전체 검색 필터 동시 적용·검색 결과 순서 | PASS |
| update/delete | ID 유지·날짜 변경 후 재정렬, 삭제 후 재시작 목록에서 제외, 없는 ID 두 명령 exit=2 | PASS |
| category | 대화형 추가·목록·미사용 삭제, 사용 중 삭제 거부, 거래 삭제 후 분류 삭제 성공 | PASS |
| budget/summary | 예산 영속성, 총수입 12000/총지출 3500/잔액 8500, TOP study→food, 사용률 116.67%·초과 경고, 빈 달 안내 | PASS |
| 3종 영속성 | 모든 명령을 별도 Python 프로세스로 시작, 사용자 정의 study 분류·거래 ID·월 예산 복원, JSONL 3개 확인 | PASS |
| export | UTF-8 한글·고정 6열·쉼표 태그 인용, 월 3건/기간 2건, 기존 출력 보호와 명시적 overwrite, 내부 3종 파일 보호 | PASS |
| import | 정상 CSV 1/0 exit=0, 혼합 CSV 2/1 exit=2·3행 사유/힌트·정확히 2건 반영, 잘못된 헤더·없는 파일 무반영 | PASS |
| 잘못된 입력 | 불가능한 날짜, 0/음수/소수, 잘못된 type/미등록 category, 역전 기간, EOF, 필수 옵션 누락 | PASS |
| 파일 보존 | 실패한 CLI의 3종 JSONL byte 비교, 기존 export byte 비교, 손상 거래 파일을 덮어쓰지 않음 | PASS |
| 쓰기 실패 | unittest의 os.replace 실패 주입: update 원본 유지, export 기존 보고서 유지, import 전체 저장 실패 시 원본 유지·임시 파일 정리 | PASS (실패 주입) |

실제 CLI 출력 발췌:

```text
총 수입: 12000원
총 지출: 3500원
잔액: 8500원
예산: 3000원 (사용률 116.67%)
[경고] 월 예산 초과
1) study: 2000원
2) food: 1500원
exit= 0

[완료] imported=2, skipped=1
[건너뜀] 3행: 날짜가 올바르지 않습니다. [힌트] YYYY-MM-DD 형식으로 입력하세요.
exit= 2

PASS: 61 fresh CLI processes; all assertions passed
CLEANUP: temporary synthetic data removed: True
```

## 재현한 결함과 보완

기존 21개 unittest는 실제 PASS였지만, 독립 subprocess 재현에서 다음을 확인했다.

| 수정 전 실제 관찰 | 최소 수정 | 수정 후 근거 |
|---|---|---|
| add 입력 EOF: exit=1, traceback=True | 공통 데코레이터에서 EOF/KeyboardInterrupt 처리 | EOF CLI exit=2·힌트, 중단 전후 3파일 동일; Ctrl-C는 unittest 예외 주입 |
| categories의 `{}`·budgets의 문자열 amount: exit=1, traceback=True | JSONL 읽기 시 category/budget 필드 검증 | 손상값별 사용자 오류, 읽기·수정 시 원본 보존 회귀 테스트 |
| delete 필수 옵션 누락: exit=2, hint=False | argparse 오류에 --help 해결 힌트 추가 | 누락·잘못된 숫자·알 수 없는 옵션 회귀 테스트 |
| import 불량 행의 사유만 출력 | 각 불량 행에 해당 검증 힌트도 출력 | 2/1 부분 성공 실제 CLI 및 회귀 테스트 |

회귀 테스트 8개 추가, 최종 전체 29/29 PASS. 표준 라이브러리·기존 기능 범위를 유지했다.

## 검증 경계

Python 3.10 문법 AST 파싱은 6모듈 PASS이며 외부 패키지 import 없음도 정적으로 확인했다. **이번 수정 버전은 Python 3.12.3에서 실행했다.** 기존 CI의 3.10/3.12 21개 PASS는 과거 기록이고 이번 수정 버전의 새 CI 실행으로 간주하지 않는다. 네트워크 접근·push·클라우드 배포는 수행하지 않았다.

실제 디스크 고갈·전원 차단·다중 프로세스 동시 쓰기·10만 건 성능은 미검증이다. os.replace 실패는 실제 디스크 장애 대신 명시적 실패 주입으로 확인했다. 입력은 subprocess stdin으로 제공했으며 사용자의 키보드 직접 시연이나 구술 설명을 대신하지 않는다. 동일 CSV 재import 중복 등록 허용은 문서화된 정책이고, 이번 중복 보호 PASS는 기존 export 대상 보호를 뜻한다. 사용자 직접 시연·동료평가·발표 바이너리 보관 확인은 별도로 남는다.
