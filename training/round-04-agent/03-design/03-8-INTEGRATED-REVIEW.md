# B2-1 03-8 — 종합 설계 검증 및 04 개발 인계 V1.0

> **문서 종합 점검용**. 자체 선언만으로 설계 PASS가 되지 않으며, 별도 GitHub 재조회·링크·요구 매핑 검증 후 문서 QA 기록이 있어야 한다. 개발 승인 PENDING, RUNTIME/LEARNER/CLEAR NOT_VERIFIED.

## 03-1~03-8 독립 문서 링크
1. [03-1 요구/평가 범위](03-1-REQUIREMENTS-SCOPE.md)
2. [03-2 CLI·명령 흐름](03-2-CLI-FLOW.md)
3. [03-3 모델·모듈·저장 구조](03-3-ARCHITECTURE.md)
4. [03-4 데이터/제어 흐름](03-4-DATA-CONTROL-FLOW.md)
5. [03-5 입력·오류·보안](03-5-ERROR-SECURITY.md)
6. [03-6 시험·증빙 계획](03-6-TEST-EVIDENCE-PLAN.md)
7. [03-7 학습 설계](LEARNING-DESIGN.md)
8. [03-8 이 종합 검증 문서](03-8-INTEGRATED-REVIEW.md)

## 확인 체크리스트
- [x] 제2기 공식 PDF B2-1 제목, 필수/선택, Python 표준 라이브러리 요구가 문서와 일치
- [x] REQ-01~23 모두 시험 T-ID와 연결, E1~E4의 판단 근거 확보
- [x] 03 하위 8 문서 각각 V0.1→위험 ID→V1.0 및 입문자 사례·학습 설명이 적절히 연결
- [x] 모든 상대 링크·Mermaid/code fence 파싱·원본 SHA·승인 상태 재검증
- [x] 파일 영구 저장·제너레이터·데코레이터·타입힌트·오류코드 설계 누락 없음
- [x] 과거 archive 레퍼런스는 원문 보존, 신규 코드 경로에 복제하지 않음
- [x] 실제 프로그램·학생 학습·Evidence는 모두 NOT_VERIFIED로 유지

**3회 검토+보완 재검증**: [05-tests/DOCUMENT-QA-ROUND04.md](../05-tests/DOCUMENT-QA-ROUND04.md)에 요구 23개·선택4개, 링크 검사, 잘못된 상위 README 복구, 숨은 문자 제거 및 원격 링크 재검증 기록. 문서 정적 점검만 PASS이며 실제 기능/증빙/독립 학습은 NOT_VERIFIED.

## 04 단계 구현 입구
- 소스 유일 경로: training/round-04-agent/04-src/
- 개발 시작 전 명시적 승인값과 작업 지시 재확인
- 환경/브랜치/권한/비밀정보 Preflight, 공식 REQ-01~23 재확인
- 작은 구현 단위: A 모델·파일, B 카테고리/add/list, C 검색/update/delete, D 요약/budget, E CSV, F generator/decorator/type hint/오류 통합
- 개발 후 05 테스트와 06 증빙을 같은 실행에서 기록. 07 독립 평가, 08 실물 자료, 09 인계.

## V0.1→위험 검토→V1.0
V0.1: 하위 문서 목록만 기록. P23 링크/요구 누락 위험 → 정적 검사 기준 추가; P24 문서 PASS를 runtime PASS로 오인 → 상태 분리; P25 개발 승인 우회 위험 → 별도 승인 게이트 추가. V1.0: 종합 체크·인계 설계 확정.

## 최종 한 문장
현재 문서·계획이 완성되더라도 공식 요구 전체의 실제 실행·재현 증거와 학습자 설명이 있기 전에는 B2-1 CLEAR가 아니다.
