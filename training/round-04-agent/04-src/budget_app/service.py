"""Business rules for a file-backed budget application."""
from __future__ import annotations
import csv
import os
import tempfile
import uuid
from pathlib import Path
from typing import Iterator
from .models import (BudgetError, Transaction, parse_tags, validate_amount,
                     validate_date, validate_month, validate_type)
from .storage import Store

CSV_FIELDS = ["date", "type", "category", "amount", "memo", "tags"]


class BudgetService:
    def __init__(self, folder: Path) -> None:
        self.store = Store(folder)

    def categories(self) -> list[str]:
        return [str(item["name"]) for item in self.store.stream("categories")]

    def require_category(self, value: str) -> str:
        value = value.strip()
        if value not in self.categories():
            raise BudgetError("등록되지 않은 카테고리입니다: " + value,
                              "category list 또는 category add 명령을 사용하세요.")
        return value

    def add_category(self, name: str) -> None:
        name = name.strip()
        if not name or "," in name or "\n" in name:
            raise BudgetError("카테고리명이 올바르지 않습니다.", "비어 있지 않은 이름을 입력하세요.")
        current = self.categories()
        if name in current:
            raise BudgetError("이미 존재하는 카테고리입니다.", "category list로 확인하세요.")
        self.store.save("categories", [{"name": v} for v in current + [name]])

    def remove_category(self, name: str) -> None:
        current = self.categories()
        if name not in current:
            raise BudgetError("카테고리를 찾을 수 없습니다.", "category list로 확인하세요.")
        if any(t.category == name for t in self.store.transaction_stream()):
            raise BudgetError("사용 중인 카테고리는 삭제할 수 없습니다.", "거래의 카테고리를 먼저 변경하세요.")
        self.store.save("categories", [{"name": v} for v in current if v != name])

    def make_transaction(self, *, date: str, type: str, category: str,
                         amount: object, memo: str = "", tags: str | list[str] | None = None,
                         identifier: str | None = None) -> Transaction:
        return Transaction(id=identifier or "TX-" + uuid.uuid4().hex,
                           date=validate_date(date), type=validate_type(type),
                           category=self.require_category(category), amount=validate_amount(amount),
                           memo=memo.strip(), tags=parse_tags(tags))

    def add(self, **values: object) -> Transaction:
        current = self.store.transactions()
        item = self.make_transaction(**values)
        ids = {t.id for t in current}
        while item.id in ids:
            item = self.make_transaction(**values)
        self.store.save_transactions(current + [item])
        return item

    def list(self, limit: int = 20) -> Iterator[Transaction]:
        if limit <= 0:
            raise BudgetError("--limit은 1 이상이어야 합니다.")
        for n, item in enumerate(self.store.transaction_stream()):
            if n >= limit:
                break
            yield item

    def search(self, *, date_from: str | None = None, date_to: str | None = None,
               category: str | None = None, type: str | None = None,
               query: str | None = None, tag: str | None = None) -> Iterator[Transaction]:
        if date_from:
            validate_date(date_from)
        if date_to:
            validate_date(date_to)
        if date_from and date_to and date_from > date_to:
            raise BudgetError("기간 시작일이 종료일보다 늦습니다.", "--from과 --to의 순서를 확인하세요.")
        if category:
            category = self.require_category(category)
        if type:
            validate_type(type)
        for item in self.store.transaction_stream():
            if date_from and item.date < date_from:
                continue
            if date_to and item.date > date_to:
                continue
            if category and item.category != category:
                continue
            if type and item.type != type:
                continue
            if query and query.lower() not in item.memo.lower():
                continue
            if tag and tag not in item.tags:
                continue
            yield item

    def update(self, identifier: str, **changes: object) -> Transaction:
        current = self.store.transactions()
        match = next((t for t in current if t.id == identifier), None)
        if match is None:
            raise BudgetError("수정할 거래를 찾지 못했습니다.", "list로 거래 ID를 확인하세요.")
        merged = match.to_dict()
        merged.update({k: v for k, v in changes.items() if v is not None})
        merged.pop("id")
        item = self.make_transaction(identifier=identifier, **merged)
        self.store.save_transactions([item if t.id == identifier else t for t in current])
        return item

    def delete(self, identifier: str) -> None:
        current = self.store.transactions()
        if not any(t.id == identifier for t in current):
            raise BudgetError("삭제할 거래를 찾지 못했습니다.", "list로 거래 ID를 확인하세요.")
        self.store.save_transactions([t for t in current if t.id != identifier])

    def set_budget(self, month: str, amount: object) -> None:
        month = validate_month(month)
        amount = validate_amount(amount)
        existing = [row for row in self.store.stream("budgets") if row.get("month") != month]
        existing.append({"month": month, "amount": amount})
        self.store.save("budgets", existing)

    def summary(self, month: str, top: int = 3) -> dict:
        month = validate_month(month)
        if top <= 0:
            raise BudgetError("--top은 1 이상이어야 합니다.")
        income = expense = count = 0
        by_category: dict[str, int] = {}
        for item in self.store.transaction_stream():
            if not item.date.startswith(month + "-"):
                continue
            count += 1
            if item.type == "income":
                income += item.amount
            else:
                expense += item.amount
                by_category[item.category] = by_category.get(item.category, 0) + item.amount
        budget = next((int(row["amount"]) for row in self.store.stream("budgets")
                       if row.get("month") == month), None)
        return {"count": count, "income": income, "expense": expense,
                "balance": income - expense, "budget": budget,
                "usage": round(100 * expense / budget, 2) if budget else None,
                "over": expense > budget if budget else False,
                "top": sorted(by_category.items(), key=lambda x: (-x[1], x[0]))[:top]}

    def import_csv(self, source: Path) -> tuple[int, list[str]]:
        new_items: list[Transaction] = []
        failures: list[str] = []
        try:
            with source.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames != CSV_FIELDS:
                    raise BudgetError("CSV 헤더가 올바르지 않습니다.",
                                      "date,type,category,amount,memo,tags 순서의 헤더를 사용하세요.")
                for line_no, row in enumerate(reader, 2):
                    try:
                        if None in row or any(v is None for v in row.values()):
                            raise BudgetError("CSV 열 개수가 올바르지 않습니다.")
                        new_items.append(self.make_transaction(
                            date=row["date"], type=row["type"], category=row["category"],
                            amount=row["amount"], memo=row["memo"], tags=row["tags"]))
                    except BudgetError as error:
                        failures.append(f"{line_no}행: {error.reason}")
        except (OSError, UnicodeError, csv.Error) as error:
            raise BudgetError("CSV 파일을 읽을 수 없습니다.", "경로·UTF-8 인코딩·CSV 형식을 확인하세요.") from error
        if new_items:
            self.store.save_transactions(self.store.transactions() + new_items)
        return len(new_items), failures

    def export_csv(self, dest: Path, *, month: str | None = None,
                   date_from: str | None = None, date_to: str | None = None,
                   overwrite: bool = False) -> int:
        if month:
            validate_month(month)
            date_from = month + "-01"
            date_to = month + "-31"
        elif not date_from or not date_to:
            raise BudgetError("내보낼 기간을 지정해야 합니다.", "--month 또는 --from과 --to를 지정하세요.")
        # Search will validate real dates; end-of-month is a filter bound, not an actual date.
        if not month:
            validate_date(date_from)
            validate_date(date_to)
            if date_from > date_to:
                raise BudgetError("기간 시작일이 종료일보다 늦습니다.")
        if dest.resolve() in {self.store.path(n).resolve() for n in ("transactions", "categories", "budgets")}:
            raise BudgetError("내부 데이터 파일에 CSV를 덮어쓸 수 없습니다.", "다른 --out 경로를 지정하세요.")
        if dest.exists() and not overwrite:
            raise BudgetError("내보낼 CSV가 이미 존재합니다.", "--overwrite를 지정하거나 새 파일명을 사용하세요.")
        temp: Path | None = None
        written = 0
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                             dir=dest.parent, prefix=".export-", suffix=".tmp",
                                             delete=False) as handle:
                temp = Path(handle.name)
                writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
                writer.writeheader()
                for item in self.store.transaction_stream():
                    if not date_from <= item.date <= date_to:
                        continue
                    writer.writerow({"date": item.date, "type": item.type,
                                     "category": item.category, "amount": item.amount,
                                     "memo": item.memo, "tags": ",".join(item.tags)})
                    written += 1
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, dest)
        except (OSError, UnicodeError, csv.Error) as error:
            raise BudgetError("CSV를 내보내지 못했습니다.", "출력 경로와 쓰기 권한을 확인하세요.") from error
        finally:
            if temp is not None:
                try:
                    temp.unlink(missing_ok=True)
                except OSError:
                    pass
        return written
