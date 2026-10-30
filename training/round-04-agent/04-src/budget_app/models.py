"""거래의 데이터 모양과 공통 입력 검사를 정의하는 Model(데이터 모델).

cli.py의 입력을 service.py가 이 모듈로 검증하고 Transaction으로 만든다.
storage.py는 저장된 사전을 Transaction으로 복원한다. 여기서는 화면 출력이나
파일 입출력(Input/Output, I/O)을 하지 않아 같은 검사를 여러 곳에서 재사용한다.
검사 실패는 BudgetError에 이유와 힌트를 담아 CLI까지 전달한다.
"""
# 타입 힌트(type hint)는 인자와 반환값의 예상 자료형을 적은 설명이다.
# 예: str은 문자열, int는 정수, list[str]은 문자열 목록, None은 값 없음이다.
# 힌트가 자동으로 값을 검사하지는 않으므로 아래 함수에서 실제 검사를 수행한다.
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import date as Date


# === CLI에서 안내할 오류 ===
class BudgetError(Exception):
    """예외(Exception): 정상 흐름을 멈추고 호출한 쪽에 실패를 알리는 객체.

    reason(이유)과 hint(해결 안내)를 받아 보관한다. CLI의 safe_cli가 이를
    출력하므로 서비스와 저장소가 출력 문구 처리에 직접 관여하지 않아도 된다.
    """
    def __init__(self, reason: str, hint: str = "입력값과 --help를 확인하세요.") -> None:
        """이유와 선택 힌트를 저장한다. 반환값은 없으며 기본 예외에도 이유를 전달한다."""
        super().__init__(reason)
        self.reason = reason
        self.hint = hint


# === 거래 한 건의 표현과 저장용 변환 ===
# 데코레이터(Decorator)는 @ 아래의 클래스나 함수를 감싸 기능을 붙이는 문법이다.
# dataclass(데이터 클래스)는 필드 선언으로 생성자 등을 자동으로 만든다.
# frozen=True는 생성 후 필드 재대입을 막는다. tags 목록 내부까지 불변은 아니다.
@dataclass(frozen=True)
class Transaction:
    """id·type·date·amount·category·memo·tags를 담는 거래 한 건.

    생성자는 각 필드를 받아 객체를 만들며, 생성만으로 모든 값이 검증되지는 않는다.
    사용자 입력은 Service.make_transaction, 저장 데이터는 from_dict로 검사한다.
    수정 시 새 객체를 만드는 방식으로 원래 거래와 변경 결과를 구분한다.
    """
    id: str
    type: str
    date: str
    amount: int
    category: str
    memo: str = ""
    # default_factory는 거래마다 새 목록을 만들어 기본 tags가 서로 공유되지 않게 한다.
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """인자 없이 거래 필드를 새 사전으로 반환한다. JSONL 저장에 쓰기 위한 변환이다."""
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict) -> "Transaction":
        """저장 파일에서 읽은 사전을 검증하여 Transaction으로 반환한다.

        필수 필드 누락·알 수 없는 필드·잘못된 값은 BudgetError로 알린다.
        저장 파일도 직접 수정되거나 손상될 수 있으므로 읽을 때 다시 검사한다.
        category는 문자열인지 검사하며 등록 여부는 이 메서드에서 확인하지 않는다.
        """
        # classmethod는 객체 없이 Transaction.from_dict(...)로 호출할 수 있게 한다.
        try:
            # **value는 사전의 키를 생성자 인자 이름으로, 값을 해당 인자 값으로 넘긴다.
            result = cls(**value)
            # bool은 Python에서 int의 하위 자료형이므로 금액의 True/False를 따로 거른다.
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
            # from error로 원래 원인을 연결하되, CLI에는 아래 이유와 힌트를 안내한다.
            raise BudgetError("거래 저장 파일의 데이터가 손상되었습니다.", "거래 JSONL의 필드와 값을 확인하세요.") from error


# === 입력 형식 검사: 올바른 값은 반환하고 잘못된 값은 예외로 알림 ===
def validate_date(value: str) -> str:
    """날짜 문자열을 받아 실제 YYYY-MM-DD이면 그대로 반환한다.

    존재하지 않는 날짜나 다른 표기는 BudgetError이다. 고정 길이 표기를 유지해야
    서비스에서 문자열 비교만으로도 날짜 순서를 정확하게 판단할 수 있다.
    """
    try:
        parsed = Date.fromisoformat(value)
        # 날짜 해석 성공뿐 아니라 다시 만든 표기도 같아야 허용한다.
        if parsed.isoformat() != value:
            raise ValueError("noncanonical date")
        return value
    except (ValueError, TypeError) as error:
        raise BudgetError("날짜가 올바르지 않습니다.", "YYYY-MM-DD 형식으로 입력하세요.") from error


def validate_month(value: str) -> str:
    """월 문자열을 받아 YYYY-MM이고 존재하는 월이면 반환한다.

    길이·구분자·달력 검사가 실패하면 BudgetError이다. 월의 1일을 만들어
    표준 날짜 도구로 검사하므로 윤년 등의 달력 규칙을 직접 구현할 필요가 없다.
    """
    try:
        if len(value) != 7 or value[4] != "-":
            raise ValueError("invalid month")
        Date.fromisoformat(value + "-01")
        return value
    except (ValueError, TypeError) as error:
        raise BudgetError("월 형식이 올바르지 않습니다.", "YYYY-MM 형식으로 입력하세요.") from error


def validate_type(value: str) -> str:
    """유형 문자열이 income 또는 expense이면 반환하고, 아니면 BudgetError를 낸다.

    저장값을 두 이름으로 통일해야 수입·지출 계산에서 같은 기준을 사용할 수 있다.
    """
    if value not in ("income", "expense"):
        raise BudgetError("거래 유형이 올바르지 않습니다.", "income 또는 expense를 사용하세요.")
    return value


def validate_amount(value: object) -> int:
    """금액 입력을 받아 1 이상의 정수로 반환한다. 부적합하면 BudgetError이다.

    CLI/CSV의 숫자 문자열과 저장된 정수에 같은 규칙을 적용한다.
    bool, 부호·소수점이 있는 표기와 0은 허용하지 않는다.
    """
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
    """쉼표 구분 문자열·문자열 목록·None을 받아 정리한 태그 목록을 반환한다.

    None은 빈 목록이며, 공백·빈 태그·중복은 제거하고 최초 등장 순서를 유지한다.
    목록 원소는 문자열이라고 가정한다. 잘못된 원소 자료형을 별도 안내로 바꾸지는 않는다.
    여러 입력 경로에서 태그의 저장 모양을 통일하기 위한 처리이다.
    """
    if value is None:
        return []
    chunks = value.split(",") if isinstance(value, str) else value
    # 사전 키는 중복되지 않고 삽입 순서를 유지하므로 정리된 태그를 키로 모은다.
    return list(dict.fromkeys(t.strip() for t in chunks if t.strip()))
