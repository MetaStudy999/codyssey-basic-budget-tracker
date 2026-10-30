"""명령줄 인터페이스(Command-Line Interface, CLI): 사용자 입력과 결과 출력 담당.

__main__.py → main → BudgetService → Store → JSONL 파일 순서로 요청한다.
Service는 업무 규칙, Store는 저장소 접근, Model은 거래 모양과 검증을 맡는다.
이 파일에서는 argparse로 명령을 해석하고, 예상 실패를 이유·힌트로 안내한다.
JSON Lines(JSONL)는 한 줄에 JSON 객체 하나를 저장하는 내부 파일 형식이다.
"""
from __future__ import annotations
# argparse는 명령·옵션을 등록하면 입력 해석과 --help 작성을 해 주는 표준 라이브러리이다.
import argparse
import functools
import sys
from pathlib import Path
from typing import Callable
from .models import BudgetError
from .service import BudgetService


# === 명령 실행을 감싸는 공통 오류 처리 ===
def safe_cli(func: Callable[..., int]) -> Callable[..., int]:
    """종료 코드 정수를 반환하는 함수 func를 받아 오류 처리 함수를 반환한다.

    데코레이터(Decorator)는 함수를 감싸 공통 기능을 더하는 방식이며 @safe_cli로 쓴다.
    예외(Exception)는 작업 실패를 호출한 쪽에 알린다. 예상 오류는 안내 후 2로 바꾸고,
    그 밖의 예외는 그대로 전달한다. 명령마다 같은 try/except를 반복하지 않기 위함이다.
    Callable[..., int]는 인자를 받는 방식은 다양하되 int를 반환한다는 타입 힌트이다.
    타입 힌트(type hint)는 예상 자료형 설명이며 자동 입력 검증 기능은 아니다.
    """
    # wraps는 감싼 함수의 이름과 docstring(함수 설명 문자열)을 보존한다.
    @functools.wraps(func)
    def wrapped(*args: object, **kwargs: object) -> int:
        """받은 위치·이름 인자를 func에 전달하고 종료 코드를 반환한다.

        예상 사용자·입출력 오류에는 2를 반환한다. argparse의 SystemExit는 잡지 않는다.
        """
        try:
            return func(*args, **kwargs)
        except BudgetError as error:
            # Model/Service/Store가 정한 이유와 해결 안내를 표준 오류 출력(stderr)에 쓴다.
            print("[오류] " + error.reason, file=sys.stderr)
            print("[힌트] " + error.hint, file=sys.stderr)
            return 2
        except (EOFError, KeyboardInterrupt):
            # 입력이 끝났거나 Ctrl+C로 중단된 경우에도 사용자가 재시도할 수 있게 안내한다.
            print("[오류] 입력이 중단되었습니다.", file=sys.stderr)
            print("[힌트] 명령을 다시 실행하고 입력을 완료하세요.", file=sys.stderr)
            return 2
        except (OSError, UnicodeError) as error:
            # 입출력(Input/Output, I/O)은 파일 읽기·쓰기 등 외부와 데이터를 주고받는 일이다.
            # 아래 계층에서 변환되지 않은 파일·문자 인코딩 오류를 마지막으로 안내한다.
            print("[오류] 파일 입출력을 완료할 수 없습니다.", file=sys.stderr)
            print("[힌트] 입력 경로, 인코딩, 읽기/쓰기 권한을 확인하세요.", file=sys.stderr)
            return 2
    return wrapped


# === 명령과 옵션의 문법 정의 ===
class HelpfulParser(argparse.ArgumentParser):
    """argparse.ArgumentParser를 확장하여 입력 문법 오류에 힌트를 붙인다.

    부모 클래스의 생성 인자를 그대로 사용한다. 잘못된 명령·필수 옵션 누락은
    부모 error가 사용법을 출력하고 SystemExit(2)로 종료한다.
    서비스 실행 전에 문법 오류를 설명하기 위한 클래스이다.
    """
    def error(self, message: str) -> None:
        """오류 문자열을 받아 도움말 힌트와 함께 안내하고 종료한다. 정상 반환하지 않는다."""
        super().error(message + "\n[힌트] 해당 명령의 --help로 필수 인자와 형식을 확인하세요.")


def build_parser() -> argparse.ArgumentParser:
    """인자 없이 명령 해석기를 구성해 반환한다. 아직 입력 해석·파일 접근은 하지 않는다.

    옵션 이름을 한곳에 모아 도움말과 실제 입력 문법을 일치시킨다.
    required=True는 필수 입력, default는 생략 시 값, dest는 해석 결과의 속성 이름이다.
    parse_args에서 잘못된 입력이면 HelpfulParser.error로 종료한다.
    """
    parser = HelpfulParser(prog="python -m budget_app", description="B2-1 개인 용돈기입장")
    parser.add_argument("--data-dir", default="./data", help="내부 JSONL 저장 폴더 (명령 앞에 입력)")
    # 상위 옵션 --data-dir는 하위 명령 앞에 쓴다. 기본 ./data는 실행 위치 기준이다.
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("add", help="대화형 거래 추가")
    listing = sub.add_parser("list", help="거래 목록을 최신순으로 출력")
    listing.add_argument("--limit", type=int, default=20)
    # type=int는 문자열 옵션을 정수로 바꾼다. 양수인지 여부는 Service가 검사한다.
    search = sub.add_parser("search", help="조건별 거래 검색")
    search.add_argument("--from", dest="date_from")
    search.add_argument("--to", dest="date_to")
    for option in ("category", "type", "q", "tag"):
        # 같은 형태의 검색 옵션을 반복 등록한다. 검색에 쓰지 않은 옵션은 None이 된다.
        search.add_argument("--" + option)
    update = sub.add_parser("update", help="거래 필드 수정(옵션 방식)")
    update.add_argument("--id", required=True)
    for name in ("date", "type", "category", "amount", "memo", "tags"):
        # 사용자가 지정한 필드만 나중에 changes 사전에 모아 기존 값에 합친다.
        update.add_argument("--" + name)
    deleting = sub.add_parser("delete", help="거래 삭제")
    deleting.add_argument("--id", required=True)
    summary = sub.add_parser("summary", help="월별 수입/지출/잔액·TOP·예산")
    summary.add_argument("--month", required=True)
    summary.add_argument("--top", type=int, default=3)
    budget = sub.add_parser("budget", help="월 예산 관리")
    # budget set, category add/list/remove는 하위 명령 안에 다시 action을 선택한다.
    bsub = budget.add_subparsers(dest="action", required=True)
    setting = bsub.add_parser("set", help="월별 예산 지정")
    setting.add_argument("--month", required=True)
    setting.add_argument("--amount", required=True)
    category = sub.add_parser("category", help="카테고리 관리")
    csub = category.add_subparsers(dest="action", required=True)
    cadd = csub.add_parser("add", help="카테고리 추가")
    cadd.add_argument("--name")
    csub.add_parser("list", help="카테고리 목록")
    crem = csub.add_parser("remove", help="카테고리 제거")
    crem.add_argument("--name")
    importing = sub.add_parser("import", help="CSV에서 거래 가져오기")
    # 쉼표 구분 값(Comma-Separated Values, CSV)은 표의 행과 열을 텍스트로 옮긴 형식이다.
    # 명령 import의 --from은 source 경로, search/export의 --from은 시작 날짜가 된다.
    importing.add_argument("--from", dest="source", required=True)
    exporting = sub.add_parser("export", help="CSV 거래 내보내기")
    exporting.add_argument("--out", required=True)
    exporting.add_argument("--month")
    exporting.add_argument("--from", dest="date_from")
    exporting.add_argument("--to", dest="date_to")
    exporting.add_argument("--overwrite", action="store_true", help="기존 출력 파일 교체(선택 옵션)")
    # store_true는 옵션이 있으면 True, 없으면 False로 보관한다.
    return parser


# === 명령 실행과 결과 표시 ===
def display(item: object) -> None:
    """거래 속성을 가진 item을 받아 한 줄 출력한다. 반환값은 없다.

    list/search의 표시 순서를 통일한다. object 힌트와 달리 실제로는 Transaction의
    속성을 기대하며, 속성이 없는 객체의 오류를 여기서 변환하지 않는다. 파일 쓰기는 없다.
    """
    print(f"{item.id} | {item.date} | {item.type} | {item.category} | {item.amount} | {item.memo}")


@safe_cli
def main(argv: list[str] | None = None) -> int:
    """명령 문자열 목록 argv를 받아 실행하고 성공 0, 예상 실패 2를 반환한다.

    argv=None이면 실제 프로그램 명령줄을 읽으므로 테스트에서는 목록을 직접 줄 수 있다.
    argparse의 --help는 SystemExit(0), 문법 오류는 SystemExit(2)로 종료한다.
    입력 → Service 검증 → Store 저장 → 결과 출력 순서이며 저장 경로는 --data-dir이다.
    Store 생성 시 파일 준비가 일어나므로 조회 명령도 초기 파일을 만들 수 있다.
    """
    args = build_parser().parse_args(argv)
    app = BudgetService(Path(args.data_dir))
    command = args.command
    if command == "add":
        # 입력 여섯 개를 모두 받은 뒤 서비스에 넘긴다. 중간 입력 중단 시 거래 추가는 안 된다.
        info = {
            "date": input("날짜(YYYY-MM-DD): ").strip(),
            "type": input("유형(income/expense): ").strip(),
            "category": input("카테고리: ").strip(),
            "amount": input("금액(양수 정수): ").strip(),
            "memo": input("메모(선택): ").strip(),
            "tags": input("태그(쉼표로 구분, 선택): ").strip(),
        }
        item = app.add(**info)
        print("[저장 완료] id=" + item.id)
    elif command == "list":
        # 제너레이터(Generator)는 yield로 거래 하나를 건네고 다음 요청까지 멈춘다.
        # for가 다음 값을 요구할 때 읽기가 이어진다. 여기서는 결과 전체를 목록에 모으지 않는다.
        for item in app.list(args.limit):
            display(item)
    elif command == "search":
        # argparse의 속성 이름을 서비스 인자 이름에 연결한다. --q는 메모 검색 query이다.
        for item in app.search(date_from=args.date_from, date_to=args.date_to,
                               category=args.category, type=args.type, query=args.q,
                               tag=args.tag):
            display(item)
    elif command == "update":
        # getattr는 이름으로 속성을 읽는다. 미지정 None은 빼되, 빈 문자열은 수정값으로 남긴다.
        changes = {k: getattr(args, k) for k in ("date", "type", "category", "amount", "memo", "tags")
                   if getattr(args, k) is not None}
        if not changes:
            raise BudgetError("수정할 필드가 없습니다.", "--date, --amount 등 하나 이상 지정하세요.")
        item = app.update(args.id, **changes)
        # 서비스가 원래 ID를 유지하고 새 거래 객체로 바꿔 전체 파일을 재저장한다.
        print("[수정 완료] id=" + item.id)
    elif command == "delete":
        # 화면에 보인 ID로 삭제 대상을 지정한다. 서비스가 나머지 거래만 재저장한다.
        app.delete(args.id)
        print("[삭제 완료] id=" + args.id)
    elif command == "category":
        # --name이 없을 때만 대화형 입력을 받는다. 사용 중인 분류 삭제는 서비스가 막는다.
        if args.action == "list":
            for name in app.categories():
                print("- " + name)
        elif args.action == "add":
            name = args.name if args.name is not None else input("카테고리명: ").strip()
            app.add_category(name)
            print("[저장 완료] category=" + name)
        else:
            name = args.name if args.name is not None else input("삭제할 카테고리: ").strip()
            app.remove_category(name)
            print("[삭제 완료] category=" + name)
    elif command == "budget":
        # 월별 예산은 거래 금액과 별개로 budgets.jsonl에 저장된다.
        app.set_budget(args.month, args.amount)
        print(f"[저장 완료] {args.month} 예산 {args.amount}원")
    elif command == "summary":
        # 서비스가 계산한 사전 s를 출력한다. 거래가 없는 월도 0원 집계가 표시된다.
        s = app.summary(args.month, args.top)
        if s["count"] == 0:
            print("해당 월 거래 데이터 없음")
        print(f"총 수입: {s['income']}원")
        print(f"총 지출: {s['expense']}원")
        print(f"잔액: {s['balance']}원")
        if s["budget"] is not None:
            # 등록된 예산이 있을 때만 사용률을 소수 둘째 자리까지 표시한다.
            print(f"예산: {s['budget']}원 (사용률 {s['usage']:.2f}%)")
            if s["over"]:
                print("[경고] 월 예산 초과")
        for i, (name, total) in enumerate(s["top"], 1):
            # 서비스에서 지출액 내림차순·동률 분류명 오름차순으로 정렬한 TOP 목록이다.
            print(f"{i}) {name}: {total}원")
    elif command == "import":
        # 유효한 행만 저장하는 부분 성공이 가능하다. 실패 행에는 사유·힌트를 따로 표시한다.
        added, failed = app.import_csv(Path(args.source))
        print(f"[완료] imported={added}, skipped={len(failed)}")
        for message in failed:
            print("[건너뜀] " + message)
        return 2 if failed else 0
    elif command == "export":
        # 월 또는 시작·종료 날짜를 서비스에 전달한다. 내부 JSONL은 읽기만 하고 CSV를 쓴다.
        count = app.export_csv(Path(args.out), month=args.month,
                               date_from=args.date_from, date_to=args.date_to,
                               overwrite=args.overwrite)
        print(f"[완료] {args.out} ({count} records)")
    return 0
