"""B2-1 Round 04 용돈기입장 패키지의 소개와 버전 정보.

패키지(package)는 관련 Python 파일을 하나의 이름으로 묶은 단위이다.
이 앱은 명령줄 인터페이스(Command-Line Interface, CLI)로 입력을 받으며
Python 표준 라이브러리만 사용한다. 실행 시작점은 __main__.py이다.

읽는 순서: __main__.py → cli.py → service.py → storage.py / models.py.
cli.py는 명령을 해석하고, Service(업무 규칙 담당)는 거래를 검사한다.
Store는 Repository(저장소 접근 담당) 역할로 파일을 읽고 쓰며,
Model(데이터 모양과 검증 담당)인 Transaction으로 거래를 표현한다.
"""
# 버전 문자열은 패키지를 구분하는 정보이며, 여기서 파일을 읽거나 쓰지 않는다.
__version__ = "0.1.0"
