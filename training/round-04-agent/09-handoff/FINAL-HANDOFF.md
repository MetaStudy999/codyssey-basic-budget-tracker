# B2-1 Round 04 — 최종 인계 및 미완료 구분 (2026-10-30)

## 현재 한 문장
**신규 Python CLI 코드 + GitHub CI 테스트 + 평가 준비 문서 + 4종 슬라이드 파일 생성까지 진행했으나, 사용자 WSL2 독립 시연과 공식 동료평가가 없어 B2-1 CLEAR는 아니다.**

## 00~09 단계별 상태
| 단계 | 완료한 근거 | 현재 판정 |
|---|---|---|
| 00 계획 | EXECUTION-MASTER-PLAN, 학습·슬라이드 계획 | DOC_PASS |
| 01 요구 | REQ-01~23, BON 4, 평가 E1~E4 연결 | DOC_PASS |
| 02 분석 | archive R01/R02 정적 읽기, 사전/사후 8문항 | DOC_PASS / 사용자 사전평가 미실시 |
| 03 설계 | 03-1~03-8, V0.1/V1.1, QA 3회 이상 | DOC_CONTENT_REVIEW_PASS |
| 04 구현 | 04-src/budget_app + tests, 표준 라이브러리 | 구현 파일 존재 / CI 시험 PASS |
| 05 시험 | GitHub Actions Python 3.10/3.12 각각 21/21 PASS | CI_PASS / WSL2 NOT_VERIFIED |
| 06 증빙 | 실제 CI URL·Job ID·Git SHA | CI_EVIDENCE_READY / WSL2 Evidence 없음 |
| 07 평가 | E1~E4 설명·시연 순서·10/30/60초 답변 | PREPARED / 동료평가 NOT_VERIFIED |
| 08 발표 | 4종 PPTX/PDF(16+45+18+2), ZIP/manifest 생성 | LOCAL_ARTIFACT_CREATED / GitHub 원본 업로드 미완료 |
| 09 인계 | 본 문서, 근거·남은 검증 요약 | HANDOFF_PREPARED / CLEAR NOT_VERIFIED |

## 소스·증빙
- 정식 저장소: https://github.com/MetaStudy999/codyssey-basic-budget-tracker
- 신규 코드: `training/round-04-agent/04-src/`
- PR: https://github.com/MetaStudy999/codyssey-basic-budget-tracker/pull/9 (병합 완료)
- 최종 3차 CI 실행: https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40961200893
- 검증된 소스 HEAD(추가 문서 변경 전): `024e59bb719f9b1d0c266399780d2ccee960d716`
- [실제 시험 설명](../05-tests/RUNTIME-TEST-RESULTS.md), [Evidence](../06-evidence/GITHUB-ACTIONS-EVIDENCE.md), [평가 준비](../07-evaluation/EVALUATION-READY.md), [발표 자료 목록](../08-presentation/DELIVERABLES-INDEX.md).

## WSL2 재접속 후 1회 통합 실증(사용자 또는 연결된 도구에서)
```bash
# 이미 작업 중인 저장소가 있다면 원본 Git 상태와 새 브랜치를 먼저 확인합니다.
cd ~/codyssey-basic-budget-tracker
pwd
git status --short
git branch --show-current
python3 --version

# 04 코드 실행 위치 (다른 작업 디렉터리에서는 모듈이 검색되지 않습니다)
cd training/round-04-agent/04-src
python3 -m budget_app --help
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

**주의:** 위의 `cd` 경로는 로컬 저장소가 해당 홈 경로에 이미 설치된 경우의 예시이며 확인 전 단정할 수 없습니다. 실제 위치가 다르면 `git clone` 전에 기존 저장소와 Git 상태부터 확인합니다. 사용자의 개인 데이터 폴더가 아닌 임시 폴더에서 시연합니다.

## 최종 CLEAR 이전 반드시 필요한 것
1. 사용자 WSL2에서 실제 코드 SHA 기준 독립 CLI 재실행, 오류·재시작 영속성·CSV 증빙 확보.
2. 실제 동료평가에서 함수·모듈·정렬·제너레이터·데코레이터·JSONL/CSV·10만 건 병목을 자기 말로 설명 및 시연.
3. 슬라이드 ZIP을 GitHub 08 경로에 원본 보관하거나 별도 영구 저장소에 업로드하고 링크·SHA 확인.
4. WSL2/학습자/Evidence/평가 검증이 충족될 때만 `clear` 상태를 변경.

## 환경 장애
Agent Codyssey `run_command`는 짧은 `pwd` 호출까지 `INVALID_ARGUMENT`로 거부되었습니다. 실제 명령이 제출되지 않아 성공·실패의 런타임 출력이 없습니다. 원인과 접근 권한을 확인하기 전 반복 원격 실행은 하지 않습니다.

## 범위·보안
기존 archive R01/R02는 변경하지 않으며, 파일 기반 CLI에 클라우드 배포를 공식 필수로 추가하지 않습니다. 실제 비밀번호/API 키·사용자 거래 데이터를 채팅/Repository/Evidence에 기록하지 않습니다.

## main 병합 후 CI 재검증 추가
- main 머지 SHA: `5d62bd97a1c54a642ed0c9dc11455eed761ec718`.
- main CI 실행: https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40962189408 — Python3.10/3.12 각각 21/21 PASS.
- 원본 `.gitignore`에는 개인 가계부 데이터 패턴이 없었으므로 이번 후속 PR에서 04-src/data와 거래 JSONL, 출력 CSV 기본 이름을 제외하도록 보완했습니다.
