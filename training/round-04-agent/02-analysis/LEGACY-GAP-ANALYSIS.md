# B2-1 기존 자산·갭 분석 V1.0

> 2026-10-30 GitHub 기본 브랜치의 정적 파일 확인. WSL2 실환경 실행·버전·가계부 동작은 아직 확인하지 않았다.

## 기존 데이터의 위치 (아카이브 이후)
- training/archive/round-01-clear/ — BEGINNER-GUIDE, CHECKLIST, REFERENCE-BUILD, REFERENCE-STATUS, reference/budget_app 8개 Python 모듈과 테스트, environment/verify.sh, docs/evaluation-qa 등.
- training/archive/round-02-clear/ — README, CHECKLIST, presentation/README.
- 루트 b2-1-mission.pdf / b2-1-mission.md / b2-1-evaluation.md — 공식·평가 참조 (원본 변경 금지).
- training/round-04-agent/ — 신규 문서 작업; 04-src/는 안내 README 이외 신규 구현 없음.

## 정적 확인된 과거 준비·현재 갭
| 대상 | 과거 Round 01 자체보고(참고만) | Round 04에서 필요한 작업 |
|---|---|---|
| 모델·클래스·모듈 | dataclass, models/repositories/services/cli/utils/errors | 공식 REQ 재설계·신규 구현(승인 후) |
| JSONL 거래·분류·예산 | 3파일 구성, 기본 카테고리 정책 | 신규 런타임 재시작 후 3파일 실증 |
| add/list/search 등 | 명령 및 generator 구현 보고 | 현재 10기능 CLI 독립 시험·증빙 |
| update/delete | temp+fsync+os.replace 사용 보고 | 새 파일 경로와 오류 상황 검증 |
| import/export | 고정 CSV, 불량 행 부분 성공 보고 | 신규 스키마·불량 행 검증·정책 설명 |
| 평가·가이드 | 과거 시험 설계, 교육 문서 | 신규 REQ→T→Evidence→E 연결 및 독립 평가 |
| 00~03 문서 | 00 개요/학습 계획, 01~03 계획 골격 | 실제 01·02·03-1~8 독립 문서와 QA |
| 개발환경 | 과거 Python 3.10+를 목표로 설계 | WSL2/Ubuntu Python·권한·경로 실제 preflight는 승인 후 |

## 재사용 금지/허용 경계
과거 참고자료는 읽고 비교해 빠진 요구를 찾아낼 수 있다. 과거 코드를 복사하여 신규 구현 완료로 표시하거나, 기존 verify의 보고를 Round 04 실제 PASS로 승격하지 않는다. GitHub archive의 상대 링크 및 스크립트 경로는 과거 위치를 포함할 수 있으므로 실행 전 새 위치 기준으로 해석한다. **archive 파일 자체는 수정하지 않는다.**

## 최소 통과 경로
CLI/모델/3종 파일 영속성 → add/list/category → search/update/delete → summary/budget → CSV → generator/decorator/type hints/오류코드 → 실제 05~07 검증·설명. 보너스는 공식 필수 요구 충족 뒤. 설계 검증 단계는 03-1~03-8 필수.

## 위험과 선제 보완
| ID | 위험 | 예방/확인 |
|---|---|---|
| GAP-01 | 보관 후 과거 경로 링크 불일치 | 현재 경로를 새 문서에만 사용, 보관 원본 불변 |
| GAP-02 | 과거 Phase A CORE READY를 현재 Runtime PASS로 혼동 | RUNTIME NOT_VERIFIED 강제 |
| GAP-03 | PDF 단일/이중 하이픈 상충 | 구체적 --help/--option 규칙 선택 이유 기록 |
| GAP-04 | 데이터 재작성 중 손실 | 임시 파일·os.replace 설계 및 장애 테스트 |
| GAP-05 | 학습 자료로 가짜 실행 증거 생성 | 교육용 예제와 실제 SHA·로그 구분 |
| GAP-06 | 라이브 환경을 검사하지 않고 PASS 선언 | 승인 후 정확한 preflight/로그 수집 |

## 설계 인계
실제로 비교한 자료는 GitHub 파일과 폴더 구조이며, 로컬 WSL 상태 및 사용자 실습 기록은 아직 점검하지 않았다. 03단계는 이 사실을 전제로 진행한다.
