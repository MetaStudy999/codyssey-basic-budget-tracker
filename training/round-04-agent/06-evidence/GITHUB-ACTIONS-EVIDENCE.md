# B2-1 Round 04 — 검증 증빙 인덱스 (과거 CI 및 현재 WSL2)

> 아래 GitHub Actions 결과는 당시 커밋의 과거 기록입니다. 수정 코드 CI는 PR #11에서 Python 3.10/3.12 각각 unittest 29/29 PASS 및 CLI smoke PASS로 확인했습니다. 병합 후 main도 사용자 WSL2에서 29/29·61/61 PASS로 다시 검증했습니다. 출력 예시와 학습용 그림은 Evidence로 인정하지 않습니다.

| Evidence ID | 시험 환경 | 출처 / 실제 결과 | 소스 SHA |
|---|---|---|---|
| EV-CI-01 | Ubuntu / Python3.10,3.12 | [1회차 13/13 PASS](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40960764834) | `2145b4447762d851bfa65eaaa57ecd4e9b1fb6b7` |
| EV-CI-02 | Ubuntu / Python3.10,3.12 | [2회차 20/20 PASS](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40960980367) | `bdf42bdabcf0f3196bf242a20374c753f920bc6c` |
| EV-CI-03 | Ubuntu / Python3.10,3.12 | [3회차 21/21 PASS](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40961200893) | `024e59bb719f9b1d0c266399780d2ccee960d716` |
| EV-CI-04 | main 병합 후 Ubuntu Python3.10/3.12 | [21/21 각각 PASS](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40962189408) | `5d62bd97a1c54a642ed0c9dc11455eed761ec718` |
| EV-CI-05 | PR #11 헤드 / Ubuntu Python3.10·3.12 | [각각 29/29 PASS, CLI smoke 성공](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/41037428815) | `0208d59823c01eb1f8c9d478c545cd28962da20a` |

GitHub Job 3회차: `123754104509` (Python3.10), `123754104184` (Python3.12), 각 `Ran 21 tests` / `OK`. [테스트 설명](../05-tests/RUNTIME-TEST-RESULTS.md) 참조.

## 현재 WSL2 실행 증빙

| Evidence ID | 시험 환경 | 출처 / 실제 결과 | 검증 대상 |
|---|---|---|---|
| EV-WSL2-RUNTIME | 사용자 WSL2 / Python 3.12.3 / Agent Codyssey를 통한 Codex agent | [환경·정상/오류/영속성·검증 경계](WSL2-RUNTIME-2026-10-30.md) | 수정 작업 트리, 시작 HEAD `9be11f664b5d32d35364b0e1c0595c2467263d12` |
| EV-WSL2-UNIT | 동일 WSL2 / 임시 가상 데이터 | [29/29 PASS: Ran 29 tests, OK, exit=0](WSL2-UNITTEST-2026-10-30.txt) | 기존 21개 + 회귀 8개 |
| EV-WSL2-CLI | 동일 WSL2 / 매 명령 별도 Python 프로세스 | [61/61 PASS 및 임시 데이터 정리 True](WSL2-CLI-2026-10-30.txt) | 로그의 6개 소스 SHA256과 현재 파일 일치 |

WSL2 agent의 자동 실행은 사용자 키보드 직접 입력·독립 구술 설명을 대신하지 않습니다. 정상/오류 종료 코드, 파일 보존, 재시작 후 JSONL 3종 복원을 확인했으며 `os.replace` 실패는 unittest 주입입니다. [요구사항별 독립 검증](../05-tests/WSL2-INDEPENDENT-VERIFICATION.md)을 함께 참조합니다.

## 미증빙 항목
- 사용자 직접 독립 시연·자기 말 설명·학습 숙달: **NOT_VERIFIED**. WSL2 agent 실행은 위 증빙으로 PASS.
- 현재 수정 코드의 GitHub Actions CI: PR #11 실행 41037428815에서 Python 3.10/3.12 각각 29/29 PASS. main 병합 커밋의 별도 CI 실행은 아직 확인되지 않았습니다.
- 07 공식 동료평가에서의 구술 설명·추가 질문: **NOT_VERIFIED**.
- 08 슬라이드 실물: 현재 ChatGPT 대화에서 PPTX/PDF 4종 파일을 생성했으나 슬라이드 바이너리 GitHub 업로드는 **미완료**, 사용자의 시연 자료 검증은 별도.
- 비용·배포: CLI 과제에 클라우드 배포 요구 없음.

이 문서의 CI 결과는 서버가 보고한 성공 로그에 근거하며, 원래 수행하지 않은 시험을 수행했다고 표현하지 않습니다.

**보존된 main CI 실증:** PR #9 병합 후 main 실행 40962189408, Python3.10 Job 123757580996 및 Python3.12 Job 123757580482, 각각 `Ran 21 tests` / `OK` / success. **현재 WSL2 실증:** 위 29/29·61/61 PASS. 공식 동료평가 및 **CLEAR=NOT_VERIFIED**를 유지합니다.

## PR #11 병합 후 확정된 현재 기준 (2026-10-30)

- 원격 GitHub main: `1759968dbfe436583967b7c1878fbbc4ffa31014`, PR #11 merged.
- GitHub PR 헤드 `0208d59823c01eb1f8c9d478c545cd28962da20a` Actions run `41037428815`: Python 3.10 Job `124001632858` `Ran 29 tests`, success; Python 3.12 Job `124001632470` `Ran 29 tests`, success. 양쪽 CLI smoke success.
- 사용자 WSL2 로컬 main은 ff-only 동기화 후 같은 SHA, Python 3.12.3 unittest 29/29 PASS, 61개의 독립 CLI 프로세스 검증 PASS, 임시 가상 데이터 정리 PASS, 작업 트리 clean.
- 병합 SHA에서 별도로 실행된 GitHub main CI는 현재 확인된 기록이 없으므로 PR 헤드 CI와 구분한다. 사용자 독립 시연·자기 말 설명·대면 동료평가·CLEAR는 계속 NOT_VERIFIED.
