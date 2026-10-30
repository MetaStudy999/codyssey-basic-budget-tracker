"""User-facing CLI, argument parsing and expected-error boundary."""
from __future__ import annotations
import argparse
import functools
import sys
from pathlib import Path
from typing import Callable
from .models import BudgetError
from .service import BudgetService


def safe_cli(func: Callable[..., int]) -> Callable[..., int]:
    """Decorator: prevent raw tracebacks for expected user/data failures."""
    @functools.wraps(func)
    def wrapped(*args: object, **kwargs: object) -> int:
        try:
            return func(*args, **kwargs)
        except BudgetError as error:
            print("[오류] " + error.reason, file=sys.stderr)
            print("[힌트] " + error.hint, file=sys.stderr)
            return 2
        except (EOFError, KeyboardInterrupt):
            print("[오류] 입력이 중단되었습니다.", file=sys.stderr)
            print("[힌트] 명령을 다시 실행하고 입력을 완료하세요.", file=sys.stderr)
            return 2
        except (OSError, UnicodeError) as error:
            print("[오류] 파일 입출력을 완료할 수 없습니다.", file=sys.stderr)
            print("[힌트] 입력 경로, 인코딩, 읽기/쓰기 권한을 확인하세요.", file=sys.stderr)
            return 2
    return wrapped


class HelpfulParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        super().error(message + "\n[힌트] 해당 명령의 --help로 필수 인자와 형식을 확인하세요.")


def build_parser() -> argparse.ArgumentParser:
    parser = HelpfulParser(prog="python -m budget_app", description="B2-1 개인 용돈기입장")
    parser.add_argument("--data-dir", default="./data", help="내부 JSONL 저장 폴더 (명령 앞에 입력)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("add", help="대화형 거래 추가")
    listing = sub.add_parser("list", help="거래 목록을 최신순으로 출력")
    listing.add_argument("--limit", type=int, default=20)
    search = sub.add_parser("search", help="조건별 거래 검색")
    search.add_argument("--from", dest="date_from")
    search.add_argument("--to", dest="date_to")
    for option in ("category", "type", "q", "tag"):
        search.add_argument("--" + option)
    update = sub.add_parser("update", help="거래 필드 수정(옵션 방식)")
    update.add_argument("--id", required=True)
    for name in ("date", "type", "category", "amount", "memo", "tags"):
        update.add_argument("--" + name)
    deleting = sub.add_parser("delete", help="거래 삭제")
    deleting.add_argument("--id", required=True)
    summary = sub.add_parser("summary", help="월별 수입/지출/잔액·TOP·예산")
    summary.add_argument("--month", required=True)
    summary.add_argument("--top", type=int, default=3)
    budget = sub.add_parser("budget", help="월 예산 관리")
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
    importing.add_argument("--from", dest="source", required=True)
    exporting = sub.add_parser("export", help="CSV 거래 내보내기")
    exporting.add_argument("--out", required=True)
    exporting.add_argument("--month")
    exporting.add_argument("--from", dest="date_from")
    exporting.add_argument("--to", dest="date_to")
    exporting.add_argument("--overwrite", action="store_true", help="기존 출력 파일 교체(선택 옵션)")
    return parser


def display(item: object) -> None:
    print(f"{item.id} | {item.date} | {item.type} | {item.category} | {item.amount} | {item.memo}")


@safe_cli
def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    app = BudgetService(Path(args.data_dir))
    command = args.command
    if command == "add":
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
        for item in app.list(args.limit):
            display(item)
    elif command == "search":
        for item in app.search(date_from=args.date_from, date_to=args.date_to,
                               category=args.category, type=args.type, query=args.q,
                               tag=args.tag):
            display(item)
    elif command == "update":
        changes = {k: getattr(args, k) for k in ("date", "type", "category", "amount", "memo", "tags")
                   if getattr(args, k) is not None}
        if not changes:
            raise BudgetError("수정할 필드가 없습니다.", "--date, --amount 등 하나 이상 지정하세요.")
        item = app.update(args.id, **changes)
        print("[수정 완료] id=" + item.id)
    elif command == "delete":
        app.delete(args.id)
        print("[삭제 완료] id=" + args.id)
    elif command == "category":
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
        app.set_budget(args.month, args.amount)
        print(f"[저장 완료] {args.month} 예산 {args.amount}원")
    elif command == "summary":
        s = app.summary(args.month, args.top)
        if s["count"] == 0:
            print("해당 월 거래 데이터 없음")
        print(f"총 수입: {s['income']}원")
        print(f"총 지출: {s['expense']}원")
        print(f"잔액: {s['balance']}원")
        if s["budget"] is not None:
            print(f"예산: {s['budget']}원 (사용률 {s['usage']:.2f}%)")
            if s["over"]:
                print("[경고] 월 예산 초과")
        for i, (name, total) in enumerate(s["top"], 1):
            print(f"{i}) {name}: {total}원")
    elif command == "import":
        added, failed = app.import_csv(Path(args.source))
        print(f"[완료] imported={added}, skipped={len(failed)}")
        for message in failed:
            print("[건너뜀] " + message)
        return 2 if failed else 0
    elif command == "export":
        count = app.export_csv(Path(args.out), month=args.month,
                               date_from=args.date_from, date_to=args.date_to,
                               overwrite=args.overwrite)
        print(f"[완료] {args.out} ({count} records)")
    return 0
