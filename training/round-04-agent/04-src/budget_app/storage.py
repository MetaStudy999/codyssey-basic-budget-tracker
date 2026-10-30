"""Repository(저장소 접근 계층) 역할의 Store: JSONL 파일 입출력 담당.

service.py → Store → --data-dir의 transactions/categories/budgets.jsonl로 이어진다.
JSON Lines(JSONL)는 한 줄에 JSON(JavaScript Object Notation) 객체 하나를
적는 텍스트 형식이다. 읽은 사전은 models.Transaction으로 검증·복원한다.
입출력(Input/Output, I/O) 중 실패하면 BudgetError를 서비스와 CLI로 전달한다.
"""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Iterator
from .models import BudgetError, Transaction, validate_amount, validate_month

# category는 거래의 분류 이름이다. 실제 저장값과 명령에 쓰이는 이름을 유지한다.
DEFAULT_CATEGORIES = ("food", "transport", "rent", "salary", "etc")


class Store:
    """저장 폴더를 받아 파일을 준비하고 읽기·전체 재저장 기능을 제공한다.

    Service가 업무 규칙에 집중하도록 경로, JSONL 형식, 파일 교체를 모은다.
    준비·읽기·쓰기 실패는 BudgetError이며, 동시 쓰기를 잠그는 기능은 없다.
    """

    # === 저장 폴더 준비와 경로 제한 ===
    def __init__(self, folder: Path) -> None:
        """folder와 필요한 상위 폴더·3개 파일을 준비한다. 반환값은 없다.

        빈 categories.jsonl에는 기본 분류를 저장하므로 조회용 생성도 쓰기를 할 수 있다.
        파일 시스템 오류는 경로와 권한을 확인하라는 BudgetError로 바꾼다.
        """
        self.folder = folder
        try:
            folder.mkdir(parents=True, exist_ok=True)
            for name in ("transactions", "categories", "budgets"):
                # touch는 없는 파일을 만들고 기존 파일 내용은 지우지 않는다.
                (folder / (name + ".jsonl")).touch(exist_ok=True)
            if (folder / "categories.jsonl").stat().st_size == 0:
                self.save("categories", [{"name": item} for item in DEFAULT_CATEGORIES])
        except OSError as error:
            raise BudgetError("저장 폴더를 준비할 수 없습니다.", "경로와 쓰기 권한을 확인하세요.") from error

    def path(self, name: str) -> Path:
        """허용된 저장 이름을 받아 폴더 안의 .jsonl 경로를 반환한다.

        다른 이름은 BudgetError이다. 저장 대상 이름을 세 가지로 제한하여
        실수로 다른 파일을 선택하는 일을 막는다. 파일 자체를 읽거나 쓰지는 않는다.
        """
        if name not in ("transactions", "categories", "budgets"):
            raise BudgetError("알 수 없는 저장 파일입니다.")
        return self.folder / (name + ".jsonl")

    # === 한 줄씩 읽기와 데이터 검증 ===
    def stream(self, name: str) -> Iterator[dict]:
        """저장 이름에 해당하는 파일을 읽어 사전을 하나씩 내어준다.

        제너레이터(Generator)는 yield에서 값을 하나 전달하고 실행을 잠시 멈춘다.
        for/next로 다음 값을 요구하면 이어서 실행하므로 전체 목록을 미리 만들지 않는다.
        Iterator는 이처럼 순서대로 값을 얻을 수 있다는 타입 힌트(type hint)이다.
        함수 호출만으로 파일을 읽지 않으며, 실제 순회 중 BudgetError가 날 수 있다.
        분류·예산은 여기서 검사하고 거래 필드는 Transaction.from_dict에서 검사한다.
        """
        try:
            with self.path(name).open("r", encoding="utf-8") as handle:
                # with는 정상 종료와 예외 발생 때 모두 파일을 닫는다.
                # enumerate(..., 1)은 오류 안내에 사용할 원본 파일 행 번호도 센다.
                for line_no, line in enumerate(handle, 1):
                    if not line.strip():
                        continue
                    try:
                        # 비어 있지 않은 각 줄을 사전으로 해석한다. 배열·숫자 한 개는 거른다.
                        value = json.loads(line)
                        if not isinstance(value, dict):
                            raise ValueError("not an object")
                        if name == "categories":
                            # 분류명은 비어 있거나 앞뒤 공백·쉼표·줄바꿈을 포함하면 안 된다.
                            category = value["name"]
                            if (not isinstance(category, str) or not category.strip() or
                                    category != category.strip() or "," in category or "\n" in category):
                                raise ValueError("invalid category")
                        elif name == "budgets":
                            # 저장된 예산은 월과 실제 정수 금액이어야 한다. bool도 제외한다.
                            validate_month(value["month"])
                            amount = value["amount"]
                            if not isinstance(amount, int) or isinstance(amount, bool):
                                raise ValueError("invalid budget amount type")
                            validate_amount(amount)
                    except (ValueError, TypeError, KeyError, BudgetError) as error:
                        # 어느 파일의 몇 번째 줄인지 포함해야 손상 지점을 찾을 수 있다.
                        raise BudgetError(f"{name}.jsonl의 {line_no}행을 읽을 수 없습니다.", "백업 파일과 JSONL 형식을 확인하세요.") from error
                    yield value
        except (OSError, UnicodeError) as error:
            raise BudgetError("저장 파일을 읽을 수 없습니다.", "파일 경로·권한·UTF-8 인코딩을 확인하세요.") from error

    def load(self, name: str) -> list[dict]:
        """저장 이름을 받아 모든 사전을 목록으로 반환한다. 읽기 BudgetError는 전달한다.

        stream과 달리 전체 데이터를 메모리에 모으므로 여러 번 사용할 목록에 적합하다.
        """
        return list(self.stream(name))

    # === 임시 파일 작성 후 한 파일을 교체 ===
    def save(self, name: str, records: list[dict]) -> None:
        """저장 이름과 사전 목록으로 대상 파일 전체를 교체한다. 반환값은 없다.

        records는 호출자가 검증한 값이어야 한다. 경로·직렬화·쓰기 실패는 BudgetError이다.
        원본에 바로 쓰다가 중간에 실패해 내용이 잘리는 일을 줄이기 위해 임시 파일을 쓴다.
        교체 전 실패하면 원본을 유지한다. 원자적 교체는 한 파일에만 적용되며,
        동시 수정의 유실·여러 파일의 일괄 반영·모든 전원 장애 복구를 보장하지 않는다.
        상위 디렉터리 자체를 fsync하지 않으므로 교체 이름의 영속성에도 한계가 있다.
        """
        target = self.path(name)
        temp: Path | None = None
        try:
            # 대상과 같은 폴더에 임시 파일을 만들어 동일 파일 시스템에서 교체한다.
            # delete=False는 with로 파일을 닫은 뒤에도 교체할 경로를 남긴다는 뜻이다.
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=target.parent, prefix="."+target.name+".",
                                             suffix=".tmp", delete=False) as handle:
                temp = Path(handle.name)
                for row in records:
                    # 사전을 JSON 텍스트로 바꾸고 줄바꿈을 붙인다. 한글은 그대로 기록한다.
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                # flush: Python의 쓰기 버퍼를 운영체제로 보낸다.
                handle.flush()
                # fsync: 운영체제에 파일 내용을 저장 장치로 동기화하도록 요청한다.
                os.fsync(handle.fileno())
            # 닫힌 임시 파일로 대상 경로를 원자적으로 교체한다. 독자는 완성된 파일을 본다.
            os.replace(temp, target)
        except (OSError, TypeError, ValueError) as error:
            raise BudgetError("파일 저장이 완료되지 않았습니다.", "폴더 권한과 디스크 공간을 확인하세요.") from error
        finally:
            # 성공·실패와 관계없이 남은 임시 파일 삭제를 시도한다.
            # 교체 성공 시 임시 경로는 이미 없다. 정리 실패가 원래 결과를 가리지 않게 한다.
            if temp is not None:
                try:
                    temp.unlink(missing_ok=True)
                except OSError:
                    pass

    # === 거래 객체 변환과 일관된 저장 순서 ===
    def transactions(self) -> list[Transaction]:
        """인자 없이 전체 거래 목록을 반환한다. 읽기·복원 BudgetError는 전달한다.

        추가·수정·삭제가 파일 전체를 다시 쓰므로 기존 거래를 모두 모을 때 사용한다.
        """
        return [Transaction.from_dict(row) for row in self.stream("transactions")]

    def transaction_stream(self) -> Iterator[Transaction]:
        """인자 없이 거래를 파일 순서대로 하나씩 제공한다. 순회 중 BudgetError가 날 수 있다.

        각 JSON 사전을 검증하여 거래로 바꾸며 여기서 재정렬하지 않는다.
        저장 때 정렬해 두므로 list/search/summary/export가 같은 순서를 사용한다.
        """
        for row in self.stream("transactions"):
            yield Transaction.from_dict(row)

    def save_transactions(self, values: list[Transaction]) -> None:
        """거래 목록을 정렬해 transactions.jsonl 전체에 저장한다. 반환값은 없다.

        검증된 Transaction을 받아 사전으로 바꾸며 저장 BudgetError는 전달한다.
        날짜 내림차순, 같은 날짜는 ID 문자열 오름차순으로 저장해 조회 순서를 통일한다.
        """
        # YYYY-MM-DD의 '-'를 지우고 음수로 바꾸면 작은 값 우선 정렬에서 최신 날짜가 앞선다.
        # 두 번째 기준인 ID는 입력 순서가 아니라 동일 날짜 거래의 일관된 순서를 정한다.
        ordered = sorted(values, key=lambda x: (-int(x.date.replace("-", "")), x.id))
        self.save("transactions", [item.to_dict() for item in ordered])
