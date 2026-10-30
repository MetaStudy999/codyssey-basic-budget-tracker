# B2-1 — 03단계: 상세 설계 8개 문서 안내

> 03-1~03-8은 **입문자에게 설명 가능한 설계 자료**이며 현재 신규 프로그램은 구현·로컬 검증 승인 후 WSL2_RUNTIME_PASS. [요구별 실제 검증](../05-tests/WSL2-INDEPENDENT-VERIFICATION.md) 참조. LEARNER/동료평가/CLEAR=NOT_VERIFIED.
> 공통 필수 표준: https://github.com/MetaStudy999/codyssey-basic/blob/main/standards/ROUND-04-AGENT-MISSION-PROCESS-STANDARD.md

## 30초 요약
Python 가계부가 **명령 입력 → 유효성 검사 → 비즈니스 규칙 → 3종 파일 저장·조회 → 결과 또는 오류 출력**으로 동작하도록 설계한다. 공식 요구와 평가를 충족하는지 8개 문서를 하나씩 검사한다.

## 3~5분 Quick Start
1. [01 공식 요구 표](../01-requirements/REQUIREMENT-TRACEABILITY.md)에서 필수 REQ-01~23을 확인한다.
2. [02 과거 자료 분석](../02-analysis/LEGACY-GAP-ANALYSIS.md)에서 기존 참조와 미실행 검증 범위를 구별한다.
3. 아래 **03-1**부터 순서대로 문서를 열어 Mermaid 도식과 예상 결과를 읽고, "왜 이 방법인가?"를 한 문장으로 설명한다.
4. [03-8 종합 점검](03-8-INTEGRATED-REVIEW.md)에서 설계·링크·승인 경계를 확인한다. 04 신규 소스와 실제 WSL2 결과를 대조한다.

## 03-1~03-8 독립 문서·인계
| 세부 단계 | 직접 열기 | 평가 연결 | 문서 작성 상태 |
|---|---|---|---|
| 03-1 | [공식 요구·CORE/BONUS·수용 기준](03-1-REQUIREMENTS-SCOPE.md) | E1~E4 | DOC_STATIC_PASS · 내용 재검토 V1.1 |
| 03-2 | [CLI 입력·출력·명령·도움말](03-2-CLI-FLOW.md) | E1 | DOC_STATIC_PASS (설계 문서) |
| 03-3 | [모델·클래스·저장구조](03-3-ARCHITECTURE.md) | E2/E4 | DOC_STATIC_PASS (설계 문서) |
| 03-4 | [이벤트·데이터·상태 흐름](03-4-DATA-CONTROL-FLOW.md) | E1/E3 | DOC_STATIC_PASS (설계 문서) |
| 03-5 | [입력·오류·비밀·안전성](03-5-ERROR-SECURITY.md) | E1/E4 | DOC_STATIC_PASS (설계 문서) |
| 03-6 | [시험 ID·예상·증빙 계획](03-6-TEST-EVIDENCE-PLAN.md) | E1~E4 | DOC_STATIC_PASS (설계 문서) |
| 03-7 | [학습 설계(기존 파일 재사용)](LEARNING-DESIGN.md) | L1~L5/QG | DOC_STATIC_PASS (설계 문서) |
| 03-8 | [종합 독립 검토·04 인계](03-8-INTEGRATED-REVIEW.md) | 문서 QA | DOC_STATIC_PASS (설계 문서) |

기존 문서 정적 3회 점검은 [기존 QA 보고서](../05-tests/DOCUMENT-QA-ROUND04.md)를 참조한다. 이번 기술 설계 보완 결과는 [추가 설계 내용 QA](../05-tests/DESIGN-CONTENT-REVIEW.md)에서 별도로 검증한다. 문서 적합성 판정과 실행 PASS를 구분한다.

- [03-1~03-8 실제 재사용 프롬프트 V0.1→위험 검토→V1.1](DESIGN-PROMPTS-AND-REVIEWS.md)

## 모든 세부 단계의 7단계 공통 절차
공식 근거/실제 HEAD 확인 → 기획 프롬프트 V0.1 → 누락·위험 ID 확인 → 최종 V1.0 → 입문자용 설명(용어·비유·Mermaid·종이 실습) → GitHub 독립 정적 QA → 문서 판정·다음 단계 인계.

## 구조 개요 (Mermaid, 교육용)
~~~mermaid
flowchart LR
 A["CLI 입력"] --> B["서비스 규칙"]
 B --> C["3개 JSONL 파일"]
 C --> D["거래 조회/요약"]
 B --> E["오류+힌트"]
 D --> F["터미널 출력"]
~~~
- 명령줄 인터페이스(Command-Line Interface, CLI): 터미널 명령으로 프로그램을 제어한다.
- 파일 입출력(Input/Output, I/O): 프로그램 종료 후 데이터를 보존하고 다시 읽는다.
- JSONL: 한 줄에 JSON 객체 하나를 저장한다. 이름이 비슷한 JSON 배열 파일과 구분한다.

## 상태와 한계
문서 설계만으로 기능이 동작하거나 학습자가 L4/L5 수준이라고 선언하지 않는다. 승인된 04 구현의 05 실제 시험·06 증빙은 완료했고, 07 사용자 직접 평가·동료평가는 별도로 남아 있다. 이전 archive의 코드·Evidence·PASS를 신규 기준으로 사용하지 않는다.
