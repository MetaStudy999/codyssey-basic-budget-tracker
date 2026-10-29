# B2-1 Round 04 — 실제 CI 검증 결과 (2026-10-30)

> 자동 시험은 **GitHub Actions의 Ubuntu 러너**에서 실행했으며 사용자 WSL2 환경은 아직 검증하지 못했습니다. 실제 소스 커밋 SHA: `024e59bb719f9b1d0c266399780d2ccee960d716`.

## 3회 반복 실제 실행 기록

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
- **WSL2:** Agent Codyssey `run_command` 요청이 `INVALID_ARGUMENT` 반환, 실제 사용자 WSL2는 `NOT_VERIFIED`. 외부 서버/클라우드 배포 불필요(공식 CLI 미션).
- **데이터:** 테스트는 임시 디렉터리와 가상 거래만 사용. 실제 사용자 가계부/비밀번호/API 키 사용하지 않음.
- **주의:** CI에서의 소스 동작 PASS가 사용자의 학습 숙달 L1~L5나 코디세이 동료평가 CLEAR를 의미하지 않음.

## 다음 확인
- WSL2 재연결 후 동일 커밋으로 사용자 환경 독립 재실행, 실제 CLI 시연, 증빙 기록.
- PR #9 병합 후 main SHA로 CI/문서 연결을 다시 확인.

## 4차 — PR #9 main 병합 이후 재시험
- merge SHA: `5d62bd97a1c54a642ed0c9dc11455eed761ec718`.
- 실제 run: https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40962189408
- Python3.10 Job `123757580996`: Ran 21 tests, OK, success.
- Python3.12 Job `123757580482`: Ran 21 tests, OK, success.
- **결론:** 최종 main에 반영된 코드도 GitHub Ubuntu CI에서 각각 21/21 PASS. WSL2와 공식 동료평가 상태는 별도 NOT_VERIFIED.
