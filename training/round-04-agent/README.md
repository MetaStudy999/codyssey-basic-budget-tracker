# B2-1 — 나만의 용돈 기입장 프로그램 만들기 | Round 04 Agent

> 신규 작업 경로 승인: 2026-10-25. **00~03 문서 검토 완료, 04 신규 코드 작성, CI 3회 검증 완료**. 사용자 요청에 따라 개발 진행 중. CI 21/21(Python3.10/3.12) PASS, 사용자 WSL2·독립 학습·CLEAR=NOT_VERIFIED.

- 공식 기준: 제2기 Mission PDF 및 평가 요구사항
- Canonical Repository: `MetaStudy999/codyssey-basic-budget-tracker`
- 신규 작업 경로: `training/round-04-agent/`
- 유일한 신규 코드 작성 경로: `training/round-04-agent/04-src/`
- ChatGPT 기획·개발 주도, Agent Codyssey MCP + WSL2 Ubuntu Codex 실행·검증
- 이전 Round 자료는 `training/archive/round-01-clear/`, `round-02-clear/`에 보관·REFERENCE_ONLY; 신규 코드는 `04-src/budget_app/`
- [00~03 설계 내용 QA](05-tests/DESIGN-CONTENT-REVIEW.md): 문서만 검토; 기능 실행·학습자 결과는 NOT_VERIFIED

| 작업 폴더 | 목적 |
|---|---|
| `00-plan/` | [마스터 실행계획](00-plan/EXECUTION-MASTER-PLAN.md)·승인·목차 |
| `01-requirements/` | [공식 REQ-01~23](01-requirements/README.md)·수용 기준 |
| `02-analysis/` | [기존 자료·갭 분석](02-analysis/README.md) |
| `03-design/` | [03-1~03-8 독립 설계](03-design/README.md) |
| `04-src/` | 신규 미션 소스 전용 |
| `05-tests/` | 테스트·회귀 검증 |
| `06-evidence/` | 실제 실행 증빙·SHA |
| `07-evaluation/` | 공식 평가 항목별 판정 |
| `08-presentation/` | PPTX/PDF 및 발표 자료 |
| `09-handoff/` | 완료 보고·후속 인계 |

**제약:** 사용자 미션 개발 승인 전에는 소스 구현·명령 실행·배포·PR 병합을 하지 않습니다. 이전 PASS는 새 Round에 자동 적용하지 않고 근거로만 참조합니다. AWS·Discord·iMac은 보류하며 공식 필수 항목과 충돌할 경우 별도 협의합니다. `round-04-agent`는 신규 에이전트 실행 작업 경로이지 기존 학습 단계 R04 HARDEN 완료 선언이 아닙니다.

## 이번 04~09 진행 (2026-10-30)
- [신규 가계부 소스와 실행 안내](04-src/README.md)
- [실제 GitHub Actions 3회 CI 21/21 PASS](05-tests/RUNTIME-TEST-RESULTS.md)
- [검증 증빙](06-evidence/GITHUB-ACTIONS-EVIDENCE.md)
- [평가 준비](07-evaluation/EVALUATION-READY.md)
- [4종 슬라이드 제작 내역](08-presentation/DELIVERABLES-INDEX.md)
- [현재 인계 및 미확인 사항](09-handoff/FINAL-HANDOFF.md)

**현재 CLEAR가 아닌 이유:** 사용자 WSL2 CLI 독립 시연과 공식 동료평가는 아직 수행되지 않았습니다.
