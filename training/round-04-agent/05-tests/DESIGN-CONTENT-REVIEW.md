# B2-1 Round 04 — 00~03 설계 내용 3회 검토 및 보완 결과 (V1.1)

> **검토일: 2026-10-30. 대상: 문서·설계만.** 공식 제2기 B2-1 미션 PDF 1~10쪽과 기존 평가표, 중앙 공통 03-1~03-8 표준을 대조했다.
> **판정 범위:** DOC_STATIC_PASS(이전 문서·링크 검사) + DOC_CONTENT_REVIEW_PASS(이번 내부 설계 일관성 검토). **RUNTIME/LEARNER/EVIDENCE/CLEAR = NOT_VERIFIED**; 신규 소스와 실행은 NOT_STARTED; 개발 승인 PENDING.

## 공식 기준과 검토 자료
1. 사용자 제공 `B2-1.나만의 용돈 기입장 프로그램 만들기.pdf` (10쪽): CLI·JSONL/CSV·3개 파일·add/list/search/summary/budget/category/update/delete/import/export·generator/decorator/type hints·오류 종료 등.
2. 루트 `b2-1-evaluation.md`: E1 기능·예외, E2 모듈·클래스, E3 generator/decorator/type hints, E4 저장 형식·확장성.
3. 중앙 `standards/ROUND-04-AGENT-MISSION-PROCESS-STANDARD.md`: 00~09 단계 및 03-1~03-8, 매 단계 V0.1→위험 검토→V1.0·독립 확인.
4. 과거 참고 `training/archive/round-01-clear/reference/`: 코드·테스트를 GitHub에서 읽기 전용 분석. 이전 PASS를 신규 PASS로 사용하지 않는다.

## 실제 검토 1회차 — 요구사항/평가의 충실도
- 확인: 내부 REQ-01~23 **23/23**, BON-01~04 **4/4**와 T-ID 연결. 01 요구표에 공식 요구와 **내부 선택 규칙**을 따로 표시.
- 보완: '최신순'을 거래 날짜 내림차순(동률 ID 오름차순)으로 명시. 공식 PDF가 정렬 키 자체를 지정한 것으로 과장하지 않음.
- 보완: 숫자 기대값(잔액 70000, 예산 사용률 150%, 비순차 날짜 조회), 예산/CSV/파일 경로의 수용 사례 추가.
- 보완: PRE-07 사전·사후 문항의 다른 측정 역량을 동일 CSV 부분 성공 능력으로 정렬하고 PRE-08 저장 형식 비교를 별도 구성. 총점 14→16점(문항 8개×2점).
- 판정: 문서상의 요구→설계→테스트 **매핑 적합**. 실제 기능 증빙은 없음.

## 실제 검토 2회차 — 기술 설계·과거 구현 정적 비교
- 과거 `repositories.py: iter_latest()`가 `iter_jsonl_reverse`를 사용하고, 이전 대표 테스트는 거래 날짜가 입력순으로 증가하므로 **날짜 비순차 입력을 검증하지 못함**을 확인.
- 수정: 정렬된 거래 JSONL을 저장 중 유지하고 list/search는 정렬된 파일을 줄마다 `yield`하는 설계로 전환. add/update/import/delete가 정렬 불변식 유지; 성능/재작성 부담은 E4 한계로 명시.
- 과거 `next_id()`가 현재 최대 거래번호 기반이므로 삭제 후 ID 재사용 위험을 분석. UUID 기반 활성 ID 중복 검증·T-ID-EDGE 추가(구현 전).
- 수정: 읽기 명령/쓰기 명령/요약·CSV 생성 흐름을 분리. `--data-dir` 내부 3파일과 `--out` 외부 CSV를 구분.
- 수정: 부분 성공 CSV는 imported/skipped/행별 원인 + **exit=2**(공식 세부 코드가 아닌 내부 정책). CSV 헤더 불량은 기록 0건·비0, 재시도 중복 가능성 경고. export 대상 파일 존재 시 기본 거부·명시적 `--overwrite`만 허용(추가 옵션).
- 보완 시험: T-ORDER-EDGE, T-CSV-PARTIAL, T-DATA-SAFETY, T-ID-EDGE, T-EXPORT-OVERWRITE.
- 판정: **설계 내 논리 모순을 해소한 문서 수준 검토**. 새 코드·실제 성능·종료코드는 검증 전.

## 실제 검토 3회차 — 문서·링크·추적 구조
- 원격 GitHub 작업 브랜치에서 archive Round01/02의 트리 SHA 유지 확인.
- 00~02와 루트 **13개 문서·59개 링크**, 03 설계 **10개 문서·53개 링크**를 검사.
- 처음 검사에서 이 QA 보고서가 아직 없어 상대 링크 5개가 예정된 파일을 가리키는 문제 발견 → **이 문서를 실제 생성하여 해결**.
- 앞선 파일 검사에서 깨진 코드펜스/숨은 문자 없음. 이번 수정본도 검사 대상으로 포함.
- 03-1~03-8 각각 독립 문서 존재, 추가 `DESIGN-PROMPTS-AND-REVIEWS.md`에 **8개 V0.1 및 8개 V1.1 프롬프트 실문** 작성. 당시 프롬프트 실행 이력을 소급해 주장하지 않음.
- `04-src/`는 안내 README만 존재; 기존 자료는 그대로 보존.
- 판정: 검증 후 **문서 일관성 PASS**. Mermaid 코드 블록이 존재한다는 사실과 실제 렌더링 성공은 구분한다.

## 판단 기준과 남아 있는 작업
| 구분 | 현 상태 | 근거/다음 단계 |
|---|---|---|
| 공식 요구 매핑 | DOC_CONTENT_REVIEW_PASS | REQ 23개 ↔ T-ID 23개 |
| 03 세부 설계 | DOC_CONTENT_REVIEW_PASS | 8 독립 문서 + 재사용 프롬프트 |
| 링크·문서 구조 | DOC_STATIC_PASS(추가 재확인 대상) | 00~03 GitHub 원격 재조회 |
| 정렬·CSV·ID 정책 | 설계 확정 / RUNTIME 미검증 | 04 신규 구현 후 실제 시연 |
| Python 실행·표준 라이브러리 | NOT_VERIFIED | 별도 개발 승인 후 Preflight |
| 05~07 시험·증빙·평가 | NOT_STARTED | 실제 출력·SHA·독립 평가 |
| 08~09 발표·인계 | 기존 계획 유지 | Runtime 근거 생성 뒤 제작 |

### 명시적인 한계
- 본 보고서는 **정적 소스 검토 및 설계 검토**다. 실행 테스트, 입문자 사용성 시험, 실제 Mermaid 렌더링, 운영 성능 측정이 아니다.
- JSONL 정렬 유지의 추가/수정 비용은 크며, 데이터가 대량인 경우 성능 개선 대안을 평가 때 설명해야 한다.
- 저장소의 `owner_mission_development_approval: PENDING`은 변경하지 않는다.
- `DOC_CONTENT_REVIEW_PASS`는 이번 문서의 구성·정합성에 한정한다. 소스, Runtime, 학습 MASTER, 미션 CLEAR 판정으로 승격하지 않는다.

## GitHub 반영 후 확인 항목
- [ ] main에 이 QA 파일·새 프롬프트 등록표·03-1~03-8 존재
- [ ] 새 문서에서 상대 링크 누락 없음
- [ ] archive Round01/02 SHA 원본과 동일
- [ ] 04-src 소스 미작성, 승인 PENDING, Runtime NOT_VERIFIED
- [ ] PR 병합 결과 확인

위 체크박스는 **main 반영 후 재검증 기록으로 채워야 하며**, 본 문서 작성만으로 완료 처리하지 않는다.
