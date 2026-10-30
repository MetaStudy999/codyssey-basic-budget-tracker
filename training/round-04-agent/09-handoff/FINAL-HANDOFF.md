# B2-1 Round 04 — 최종 인계 및 미완료 구분 (2026-10-30)

## 현재 한 문장
**상태 구분: WSL2_AGENT_PASS / USER_DEMO_PENDING / peer_evaluation=NOT_VERIFIED / clear=NOT_VERIFIED.**

**현재 수정 코드는 사용자 WSL2에서 agent 실행으로 Python3.12.3 unit 29/29·별도 CLI 61/61 PASS. 과거 main CI 21/21과 구분하며, 수정 코드 CI·사용자 직접 독립 시연·자기 말 설명·공식 동료평가는 NOT_VERIFIED, 슬라이드 바이너리 GitHub 업로드는 미완료, CLEAR=NOT_VERIFIED다.**

## 00~09 단계별 상태
| 단계 | 완료한 근거 | 현재 판정 |
|---|---|---|
| 00 계획 | EXECUTION-MASTER-PLAN, 학습·슬라이드 계획 | DOC_PASS |
| 01 요구 | REQ-01~23, BON 4, 평가 E1~E4 연결 | DOC_PASS |
| 02 분석 | archive R01/R02 정적 읽기, 사전/사후 8문항 | DOC_PASS / 사용자 사전평가 미실시 |
| 03 설계 | 03-1~03-8, V0.1/V1.1, QA 3회 이상 | DOC_CONTENT_REVIEW_PASS |
| 04 구현 | 04-src/budget_app + tests, 표준 라이브러리, 회귀 8개 추가 | WSL2_RUNTIME_PASS / 수정 코드 CI NOT_VERIFIED |
| 05 시험 | 현재 WSL2 Python3.12.3 unit 29/29·별도 CLI 61/61 PASS, 과거 main CI Python3.10/3.12 각각 21/21 PASS | WSL2_RUNTIME_PASS / 사용자 직접 시연 NOT_VERIFIED |
| 06 증빙 | WSL2 실행·unit·CLI 원본 및 소스 SHA256, 과거 CI URL·Job ID·Git SHA | WSL2_EVIDENCE_READY / 과거 CI 구분 보존 |
| 07 평가 | E1~E4 설명·시연 순서·10/30/60초 답변 | PREPARED / 동료평가 NOT_VERIFIED |
| 08 발표 | 4종 PPTX/PDF(16+45+18+2), ZIP/manifest 생성 | LOCAL_ARTIFACT_CREATED / GitHub 원본 업로드 미완료 |
| 09 인계 | 본 문서, 근거·남은 검증 요약 | HANDOFF_PREPARED / CLEAR NOT_VERIFIED |

## 소스·증빙
- 정식 저장소: https://github.com/MetaStudy999/codyssey-basic-budget-tracker
- 신규 코드: `training/round-04-agent/04-src/`
- PR: https://github.com/MetaStudy999/codyssey-basic-budget-tracker/pull/9 (병합 완료)
- 과거 3차 CI 실행: https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40961200893
- 과거 3차 CI 검증 SHA: `024e59bb719f9b1d0c266399780d2ccee960d716` (현재 수정 소스 SHA가 아님).
- 현재 브랜치: `feature/b2-1-round04-runtime-evidence-20261030`, 시작 HEAD `9be11f664b5d32d35364b0e1c0595c2467263d12` 기반 수정 작업 트리.
- [WSL2 런타임 증빙](../06-evidence/WSL2-RUNTIME-2026-10-30.md), [unittest 원본 29/29 PASS](../06-evidence/WSL2-UNITTEST-2026-10-30.txt), [별도 CLI 원본 61/61 PASS](../06-evidence/WSL2-CLI-2026-10-30.txt), [독립 검증·요구사항 감사](../05-tests/WSL2-INDEPENDENT-VERIFICATION.md). CLI 로그의 소스 6개 SHA256과 현재 파일이 일치한다.
- [실제 시험 설명](../05-tests/RUNTIME-TEST-RESULTS.md), [Evidence](../06-evidence/GITHUB-ACTIONS-EVIDENCE.md), [평가 준비](../07-evaluation/EVALUATION-READY.md), [발표 자료 목록](../08-presentation/DELIVERABLES-INDEX.md).

## 완료한 WSL2 agent 실행과 재현

사용자 WSL2의 Agent Codyssey를 통한 Codex agent 실행이다. 환경은 Ubuntu 24.04.4 LTS, `Linux 6.18.33.2-microsoft-standard-WSL2`, Python 3.12.3이다. 임시 디렉터리의 가상 데이터로 정상 기능·오류 exit=2와 힌트·실패 후 원본 보존·별도 프로세스 재시작 후 거래/분류/예산 JSONL 3종 복원을 확인했다. CLI 임시 데이터 정리 결과는 `True`이며 기존 데이터·archive를 삭제하거나 초기화하지 않았다. `os.replace` 실패는 unittest 주입이며, 실제 디스크 고갈·전원 차단·동시 쓰기·10만 건 성능은 미검증이다.

아래는 재현 명령이다. 사용자 직접 입력·자기 말 설명은 별도 시연이 필요하다.

```bash
# 이번에 확인한 기존 작업 경로와 브랜치 상태를 유지합니다.
cd /home/ubuntu/codyssey/codyssey-basic-budget-tracker
pwd
git status --short
git branch --show-current
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 training/round-04-agent/05-tests/runtime_cli_verification.py

# 04 코드 실행 위치 (다른 작업 디렉터리에서는 모듈이 검색되지 않습니다)
cd training/round-04-agent/04-src
python3 -m budget_app --help
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

사용자 직접 시연도 개인 데이터 폴더가 아닌 별도 임시 폴더에서 수행한다. 위 unit/CLI 스크립트는 자체 임시 데이터를 사용한다.

## 최종 CLEAR 이전 반드시 필요한 것
1. 사용자 직접 독립 CLI 시연·자기 말 설명 증빙 확보. WSL2 agent의 정상·오류·영속성·CSV 자동 실행 증빙은 위와 같이 확보했다.
2. 실제 동료평가에서 함수·모듈·정렬·제너레이터·데코레이터·JSONL/CSV·10만 건 병목을 자기 말로 설명 및 시연.
3. 슬라이드 ZIP을 GitHub 08 경로에 원본 보관하거나 별도 영구 저장소에 업로드하고 링크·SHA 확인.
4. 현재 수정 코드의 PR 후 GitHub Actions Python3.10/3.12를 재실행하고 해당 SHA·로그를 연결. 재실행 전까지 수정 코드 CI는 NOT_VERIFIED.
5. 사용자 직접 시연·학습자 설명·Evidence·공식 평가 검증이 충족될 때만 `clear` 상태를 변경.

## 과거 환경 장애와 현재 상태
과거 Agent Codyssey `run_command`가 `INVALID_ARGUMENT`를 반환한 시점에는 런타임 증빙이 없었다. 이후 현재 사용자 WSL2에서 위 실제 로그를 확보했으므로 현재 WSL2 런타임은 PASS다. 이 실행은 사용자 직접 독립 시연·학습 숙달·동료평가를 대신하지 않는다.

## 범위·보안
기존 archive R01/R02는 변경하지 않으며, 파일 기반 CLI에 클라우드 배포를 공식 필수로 추가하지 않습니다. 실제 비밀번호/API 키·사용자 거래 데이터를 채팅/Repository/Evidence에 기록하지 않습니다.

## main 병합 후 CI 재검증 추가
- main 머지 SHA: `5d62bd97a1c54a642ed0c9dc11455eed761ec718`.
- 과거 main CI 실행: https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40962189408 — 위 SHA의 Python3.10/3.12 각각 21/21 PASS. 현재 수정 코드 CI 결과로 전용하지 않는다.
- 기존 후속 PR의 `.gitignore` 보완 기록: 04-src/data와 거래 JSONL, 출력 CSV 기본 이름 제외. 이번 상태 문서 갱신에서 `.gitignore`를 추가 변경하지 않았다.
