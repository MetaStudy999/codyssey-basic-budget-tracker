"""Data contracts; no file access or CLI logic in this module."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import date as Date


class BudgetError(Exception):
    def __init__(self, reason: str, hint: str = "입력값과 --help를 확인하세요.") -> None:
        super().__init__(reason)
        self.reason = reason
        self.hint = hint


@dataclass(frozen=True)
class Transaction:
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict) -> "Transaction":
        try:
            result = cls(**value)
            if (not isinstance(result.tags, list) or
                not all(isinstance(tag, str) for tag in result.tags) or
                not isinstance(result.memo, str) or
                not isinstance(result.category, str) or
                not isinstance(result.amount, int) or isinstance(result.amount, bool)):
                raise ValueError("invalid persisted field type")
            validate_date(result.date)
            validate_type(result.type)
            validate_amount(result.amount)
            if not isinstance(result.id, str) or not result.id:
                raise ValueError("invalid id")
            return result
        except (TypeError, ValueError, KeyError, BudgetError) as error:
            raise BudgetError("거래 저장 파일의 데이터가 손상되었습니다.", "거래 JSONL의 필드와 값을 확인하세요.") from error


def validate_date(value: str) -> str:
    try:
        parsed = Date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError("noncanonical date")
        return value
    except (ValueError, TypeError) as error:
        raise BudgetError("날짜가 올바르지 않습니다.", "YYYY-MM-DD 형식으로 입력하세요.") from error


def validate_month(value: str) -> str:
    try:
        if len(value) != 7 or value[4] != "-":
            raise ValueError("invalid month")
        Date.fromisoformat(value + "-01")
        return value
    except (ValueError, TypeError) as error:
        raise BudgetError("월 형식이 올바르지 않습니다.", "YYYY-MM 형식으로 입력하세요.") from error


def validate_type(value: str) -> str:
    if value not in ("income", "expense"):
        raise BudgetError("거래 유형이 올바르지 않습니다.", "income 또는 expense를 사용하세요.")
    return value


def validate_amount(value: object) -> int:
    try:
        if isinstance(value, bool) or not str(value).isdigit():
            raise ValueError("not unsigned integer")
        number = int(str(value))
        if number <= 0:
            raise ValueError("not positive")
        return number
    except (TypeError, ValueError) as error:
        raise BudgetError("금액은 양의 정수여야 합니다.", "1 이상의 정수를 입력하세요.") from error


def parse_tags(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    chunks = value.split(",") if isinstance(value, str) else value
    return list(dict.fromkeys(t.strip() for t in chunks if t.strip()))
