"""JSONL persistence, consistent transaction order and atomic file replacement."""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Iterator
from .models import BudgetError, Transaction, validate_amount, validate_month

DEFAULT_CATEGORIES = ("food", "transport", "rent", "salary", "etc")


class Store:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        try:
            folder.mkdir(parents=True, exist_ok=True)
            for name in ("transactions", "categories", "budgets"):
                (folder / (name + ".jsonl")).touch(exist_ok=True)
            if (folder / "categories.jsonl").stat().st_size == 0:
                self.save("categories", [{"name": item} for item in DEFAULT_CATEGORIES])
        except OSError as error:
            raise BudgetError("저장 폴더를 준비할 수 없습니다.", "경로와 쓰기 권한을 확인하세요.") from error

    def path(self, name: str) -> Path:
        if name not in ("transactions", "categories", "budgets"):
            raise BudgetError("알 수 없는 저장 파일입니다.")
        return self.folder / (name + ".jsonl")

    def stream(self, name: str) -> Iterator[dict]:
        try:
            with self.path(name).open("r", encoding="utf-8") as handle:
                for line_no, line in enumerate(handle, 1):
                    if not line.strip():
                        continue
                    try:
                        value = json.loads(line)
                        if not isinstance(value, dict):
                            raise ValueError("not an object")
                        if name == "categories":
                            category = value["name"]
                            if (not isinstance(category, str) or not category.strip() or
                                    category != category.strip() or "," in category or "\n" in category):
                                raise ValueError("invalid category")
                        elif name == "budgets":
                            validate_month(value["month"])
                            amount = value["amount"]
                            if not isinstance(amount, int) or isinstance(amount, bool):
                                raise ValueError("invalid budget amount type")
                            validate_amount(amount)
                    except (ValueError, TypeError, KeyError, BudgetError) as error:
                        raise BudgetError(f"{name}.jsonl의 {line_no}행을 읽을 수 없습니다.", "백업 파일과 JSONL 형식을 확인하세요.") from error
                    yield value
        except (OSError, UnicodeError) as error:
            raise BudgetError("저장 파일을 읽을 수 없습니다.", "파일 경로·권한·UTF-8 인코딩을 확인하세요.") from error

    def load(self, name: str) -> list[dict]:
        return list(self.stream(name))

    def save(self, name: str, records: list[dict]) -> None:
        target = self.path(name)
        temp: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=target.parent, prefix="."+target.name+".",
                                             suffix=".tmp", delete=False) as handle:
                temp = Path(handle.name)
                for row in records:
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp, target)
        except (OSError, TypeError, ValueError) as error:
            raise BudgetError("파일 저장이 완료되지 않았습니다.", "폴더 권한과 디스크 공간을 확인하세요.") from error
        finally:
            if temp is not None:
                try:
                    temp.unlink(missing_ok=True)
                except OSError:
                    pass

    def transactions(self) -> list[Transaction]:
        return [Transaction.from_dict(row) for row in self.stream("transactions")]

    def transaction_stream(self) -> Iterator[Transaction]:
        for row in self.stream("transactions"):
            yield Transaction.from_dict(row)

    def save_transactions(self, values: list[Transaction]) -> None:
        # Canonical invariant: date descending, then ID ascending. list/search can stream.
        ordered = sorted(values, key=lambda x: (-int(x.date.replace("-", "")), x.id))
        self.save("transactions", [item.to_dict() for item in ordered])
