# B2-1 Round 04 — 검증 증빙 인덱스 (실제 CI)

> 실제 GitHub Actions 시험 결과를 인용합니다. 출력 예시와 학습용 그림은 Evidence로 인정하지 않습니다.

| Evidence ID | 시험 환경 | 출처 / 실제 결과 | 소스 SHA |
|---|---|---|---|
| EV-CI-01 | Ubuntu / Python3.10,3.12 | [1회차 13/13 PASS](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40960764834) | `2145b4447762d851bfa65eaaa57ecd4e9b1fb6b7` |
| EV-CI-02 | Ubuntu / Python3.10,3.12 | [2회차 20/20 PASS](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40960980367) | `bdf42bdabcf0f3196bf242a20374c753f920bc6c` |
| EV-CI-03 | Ubuntu / Python3.10,3.12 | [3회차 21/21 PASS](https://github.com/MetaStudy999/codyssey-basic-budget-tracker/actions/runs/40961200893) | `024e59bb719f9b1d0c266399780d2ccee960d716` |

GitHub Job 3회차: `123754104509` (Python3.10), `123754104184` (Python3.12), 각 `Ran 21 tests` / `OK`. [테스트 설명](../05-tests/RUNTIME-TEST-RESULTS.md) 참조.

## 미증빙 항목
- 사용자의 WSL2 실제 실행·입문자 독립 시연: **NOT_VERIFIED**.
- 07 공식 동료평가에서의 구술 설명·추가 질문: **NOT_VERIFIED**.
- 08 슬라이드 실물: 준비/제작 별도 점검.
- 비용·배포: CLI 과제에 클라우드 배포 요구 없음.

이 문서의 CI 결과는 서버가 보고한 성공 로그에 근거하며, 원래 수행하지 않은 시험을 수행했다고 표현하지 않습니다.
