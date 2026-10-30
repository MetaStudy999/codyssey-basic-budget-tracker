# B2-1 — 01단계 공식 요구사항·평가 매핑

> 공식 PDF 기반 기준 작성. **요구별 감사 완료 / WSL2_RUNTIME_PASS**. [현재 REQ별 근거](../05-tests/WSL2-INDEPENDENT-VERIFICATION.md).

## 3분 Quick Start
1. [공식 요구사항 추적표](REQUIREMENT-TRACEABILITY.md)에서 REQ-01~23의 근거 PDF 쪽과 필수 범위를 확인한다.
2. [수용 기준·평가 연결표](ACCEPTANCE-CRITERIA.md)에서 각 요구가 어떻게 검증되는지 읽는다.
3. [학습 목표 연결](LEARNING-OBJECTIVES.md)을 읽고 자신의 말로 WHAT/WHY를 설명한다. 정상/오류의 **구체적 기대값**은 [수용 기준](ACCEPTANCE-CRITERIA.md)의 추가 표를 본다.
4. 다음 [02 기존 자료 분석](../02-analysis/README.md)으로 이동한다.

## 공식 출처
- 최우선: 제2기 현재 B2-1 공식 미션 PDF (사용자 제공, 10쪽)
- 다음: 제2기 오리엔테이션 PDF
- 기존 미션·평가: 저장소 루트 b2-1-mission.md, b2-1-evaluation.md
- 참고만: training/archive/round-01-clear/ 및 round-02-clear/

## 핵심 주의
CORE(필수) 23개 추적 ID와 BONUS(선택) 4개를 구분한다. REQ 번호는 문서 작업용이다. 모든 명령은 --help를 제공해야 하며 3종 파일 영속성·yield·데코레이터·타입 힌트·오류 종료 코드가 필수 범위이다. 공식 PDF에서 표기가 상충하거나 깨진 부분은 추적표 C절에서 명시한다.

**다음 단계:** 02 분석. 04-src 로컬 구현·WSL2 실행·커밋과 지정 feature 브랜치 일반 push는 사용자 요청으로 승인되었습니다. 배포는 범위 밖이며 사용자 직접 평가·CLEAR는 미검증입니다.
