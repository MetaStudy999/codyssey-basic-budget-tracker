"""python -m budget_app 명령을 cli.main에 연결하는 실행 시작점.

입력된 명령은 cli.main → BudgetService → Store → JSONL 파일 순으로
전달된다. JSON Lines(JSONL)는 한 줄마다 JSON 데이터 하나를 저장하는 형식이다.
JSON(JavaScript Object Notation)은 이름과 값을 텍스트로 표현하는 형식이다.
main이 돌려준 정수를 프로그램 종료 코드로 전달한다.
"""
from .cli import main

# 이 파일이 실행 시작점일 때만 명령을 처리한다. import만 할 때는 실행하지 않는다.
if __name__ == "__main__":
    # SystemExit는 Python 실행을 끝낸다. 0은 성공, 이 앱의 예상 오류는 2이다.
    raise SystemExit(main())
