# B2-1 Round 04 — WSL2 실제 실행 및 과거 CI 검증 결과 (2026-10-30)

> **WSL2_RUNTIME_PASS**: 사용자 WSL2에서 Agent Codyssey를 통한 Codex agent 실행으로 Python 3.12.3, unittest **29/29**, 별도 프로세스 CLI **61/61 PASS**. 사용자 직접 독립 시연·자기 말 설명·공식 동료평가 및 **CLEAR=NOT_VERIFIED**. 아래의 이전 CI 기록 외에 PR #11 수정 코드 CI(Python 3.10/3.12 각각 29/29 PASS)와 병합 후 WSL2 검증을 최신 근거로 확인했다.

## 현재 WSL2 실제 실행 근거

- 환경: Ubuntu 24.04.4 LTS, `Linux 6.18.33.2-microsoft-standard-WSL2`, Python 3.12.3.
- 대상: `feature/b2-1-round04-runtime-evidence-20261030`의 수정 작업 트리. 시작 HEAD `9be11f664b5d32d35364b0e1c0595c2467263d12`와 수정 후 소스를 구분한다. CLI 로그의 소스 6개 SHA256을 현재 파일과 교차 확인했다.
- [런타임 증빙·범위](../06-evidence/WSL2-RUNTIME-2026-10-30.md), [unittest 원본: Ran 29 tests / OK / exit=0](../06-evidence/WSL2-UNITTEST-2026-10-30.txt), [CLI 원본: 61 fresh CLI processes / all assertions passed](../06-evidence/WSL2-CLI-2026-10-30.txt), [독립 검증·요구사항 감사](WSL2-INDEPENDENT-VERIFICATION.md).
- 임시 디렉터리의 가상 데이터만 사용. 정상 기능, 오류 exit=2·힌트·traceback 없음, 실패 후 파일 보존, 별도 프로세스 재시작 후 거래·분류·예산 JSONL 3종 영속성을 검증했다. CLI 임시 데이터 정리 결과는 `True`다.
- 기존 21개에 EOF/중단·손상 분류/예산·인자 오류·부분 import·저장 실패 회귀 8개를 추가해 29개가 통과했다. `os.replace` 실패는 unittest에서 주입했으며 실제 디스크 장애 시험은 아니다.

## 과거 CI — 3회 반복 실제 실행 기록

| 회차 | 소스 커밋 | Python | 수행 | 결과 | GitHub Actions |
|---|---|---|---|---|---|
| 1 | `2145b4447762d851bfa65eaaa57ecd4e9b1fb6b7` | 3.10 / 3.12 | unittest 13개/버전 및 CLI smoke | 13/13 각각 PASS | https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40960764834 |
| 2 | `bdf42bdabcf0f3196bf242a20374c753f920bc6c` | 3.10 / 3.12 | unittest 20개/버전 및 CLI smoke | 20/20 각각 PASS | https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40960980367 |
| 3 | `024e59bb719f9b1d0c266399780d2ccee960d716` | 3.10 / 3.12 | unittest 21개/버전 및 CLI smoke | **21/21 각각 PASS** | https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40961200893 |

### 3회차 실제 GitHub job 로그 근거
- Python 3.10: Job ID `123754104509`; `Ran 21 tests`, `OK`, job conclusion success.
- Python 3.12: Job ID `123754104184`; `Ran 21 tests`, `OK`, job conclusion success.
- 추가 실행: `python -m budget_app --help`, `category --help`, 임시 데이터 폴더 `category list`, 빈 월 `summary` smoke 모두 성공.

## 공식 요구 연결 — 자동 시험 범위
| 평가 영역 | 실행으로 확인한 테스트 | 제한 |
|---|---|---|
| E1 기능·예외 | add/list/search/update/delete, category, budget, import/export, 비정상 입력, 종료 코드 | 모든 CLI 조합을 수동 시연한 것은 아님 |
| E2 구조·영속성 | 파일 3개·재시작, ID 안정성, 원자적 저장 실패 시 원본 유지 | 대량 10만 건 성능은 실행 안 함 |
| E3 Python 기술 | 실제 generator 객체, 적용된 decorator, 타입 힌트가 있는 코드 | 사용자의 독립 설명은 미검증 |
| E4 저장 형식·확장 | JSONL, CSV UTF-8 헤더, 일부 행 실패, 데이터 내구성 | 대용량 병목·실패 시나리오 설명은 평가 준비 단계 |

## 이번 환경과 보안
- **CI 환경:** GitHub-hosted Ubuntu, Python 3.10 및 Python 3.12. 외부 pip 설치 없음; 표준 라이브러리 unittest 사용.
- **WSL2:** 과거 `run_command`의 `INVALID_ARGUMENT` 장애 기록 이후 현재 사용자 WSL2에서 agent 실실행을 완료했다. 현재 판정은 위 증빙의 **WSL2_RUNTIME_PASS**이며 사용자 직접 시연·자기 말 설명은 **NOT_VERIFIED**다. 외부 서버/클라우드 배포 불필요(공식 CLI 미션).
- **데이터:** 테스트는 임시 디렉터리와 가상 거래만 사용. 실제 사용자 가계부/비밀번호/API 키 사용하지 않음.
- **주의:** CI에서의 소스 동작 PASS가 사용자의 학습 숙달 L1~L5나 코디세이 동료평가 CLEAR를 의미하지 않음.

## 남은 확인
- 사용자 직접 입력·독립 CLI 시연과 자기 말 설명, 공식 동료평가.
- 수정 코드 PR #11 GitHub Actions Python 3.10/3.12 실행에서 각각 29/29 PASS를 확인했고 SHA와 로그를 아래에 추가했다. 별도 main 병합 커밋의 GitHub Actions 재실행 기록은 확인되지 않았다.
- 실제 디스크 고갈·전원 차단·동시 쓰기·10만 건 성능은 이번 검증 범위 밖이다.

## 4차 — PR #9 main 병합 이후 재시험
- merge SHA: `5d62bd97a1c54a642ed0c9dc11455eed761ec718`.
- 실제 run: https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40962189408
- Python3.10 Job `123757580996`: Ran 21 tests, OK, success.
- Python3.12 Job `123757580482`: Ran 21 tests, OK, success.
- **당시 결론:** 위 main SHA는 GitHub Ubuntu CI에서 각각 21/21 PASS. 현재 수정 작업 트리의 WSL2 29/29·CLI 61/61 PASS와 구분하며, 수정 코드 CI·사용자 직접 시연·공식 동료평가는 NOT_VERIFIED다.

## 5차 — PR #11 신규 수정 코드 CI 및 main 병합 뒤 WSL2 실증

- 검증 대상 PR 커밋 `0208d59823c01eb1f8c9d478c545cd28962da20a`.
- 실제 GitHub Actions [run 41037428815](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/41037428815): Python 3.10 `unit-and-cli` Job `124001632858` `Ran 29 tests in 1.363s`, success. Python 3.12 Job `124001632470` `Ran 29 tests in 1.067s`, success. 두 Job의 CLI 기본 시연 단계도 success.
- [PR #11](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/pull/11)을 `main`에 병합한 SHA `1759968dbfe436583967b7c1878fbbc4ffa31014`.
- 사용자 WSL2 `main`과 `origin/main` 동일 SHA 확인 후 재시험: Python3.12.3 `Ran 29 tests in 0.949s`, `OK`, exit=0. CLI 검사 `PASS: 61 fresh CLI processes; all assertions passed`, exit=0. `CLEANUP ... True`, Git 작업 트리 clean.
- 제한: 위 GitHub CI는 PR 헤드에서 수행한 시험이며, main 병합 커밋의 별도 CI 실행은 확인되지 않았다. 사용자 본인 직접 키보드 시연·구술·공식 동료평가·CLEAR는 미검증이다.
