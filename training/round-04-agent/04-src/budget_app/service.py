"""Service(업무 규칙 계층): 거래·분류·예산과 CSV 처리 규칙을 모은다.

cli.main → BudgetService → Store → JSONL 파일 순으로 요청이 흐른다.
models.py는 값 검사와 Transaction 생성을, storage.py는 Repository(저장소 접근)
역할로 파일 입출력(Input/Output, I/O)을 맡는다. 이 모듈은 화면에 직접 출력하지 않고
결과를 반환하거나 BudgetError로 이유·힌트를 전달하므로 CLI와 분리해 사용할 수 있다.
JSON Lines(JSONL)는 한 줄에 JSON 객체 하나를 저장하는 내부 형식이다.
쉼표 구분 값(Comma-Separated Values, CSV)은 표 데이터를 주고받을 때 사용한다.
"""
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

# CSV의 헤더 이름과 순서는 입출력 양쪽에서 같아야 한다. ID는 CSV에 포함하지 않는다.
CSV_FIELDS = ["date", "type", "category", "amount", "memo", "tags"]


class BudgetService:
    """저장 폴더를 받아 용돈기입장의 업무 기능을 제공하는 객체.

    입력값 검증과 데이터 변경을 묶어 CLI 명령마다 규칙이 달라지지 않게 한다.
    잘못된 입력과 저장 오류는 BudgetError로 전달하며, 파일 준비는 생성 시 일어난다.
    """
    def __init__(self, folder: Path) -> None:
        """folder를 Store에 전달해 저장소를 준비한다. 반환값은 없고 준비 오류는 전달한다."""
        self.store = Store(folder)

    # === category: 거래에서 사용할 분류 이름 관리 ===
    def categories(self) -> list[str]:
        """인자 없이 categories.jsonl의 이름 목록을 파일 순서대로 반환한다.

        기본 분류와 사용자가 추가한 분류를 같은 저장소에서 읽기 위한 공통 함수이다.
        Store의 읽기·형식 오류는 BudgetError로 전달된다.
        """
        return [str(item["name"]) for item in self.store.stream("categories")]

    def require_category(self, value: str) -> str:
        """분류 문자열의 앞뒤 공백을 정리하고 등록된 이름이면 반환한다.

        미등록 이름은 category list/add를 안내하는 BudgetError이다.
        거래 생성과 검색에 같은 규칙을 적용하려고 현재 분류 파일을 다시 확인한다.
        """
        value = value.strip()
        if value not in self.categories():
            raise BudgetError("등록되지 않은 카테고리입니다: " + value,
                              "category list 또는 category add 명령을 사용하세요.")
        return value

    def add_category(self, name: str) -> None:
        """분류명을 받아 정리·검사한 후 categories.jsonl에 추가한다. 반환값은 없다.

        빈 이름·쉼표·줄바꿈·중복은 BudgetError이다. 기존 이름을 모두 읽고
        새 이름을 붙인 전체 목록을 Store.save로 교체하여 다른 분류를 보존한다.
        """
        name = name.strip()
        if not name or "," in name or "\n" in name:
            raise BudgetError("카테고리명이 올바르지 않습니다.", "비어 있지 않은 이름을 입력하세요.")
        current = self.categories()
        if name in current:
            raise BudgetError("이미 존재하는 카테고리입니다.", "category list로 확인하세요.")
        self.store.save("categories", [{"name": v} for v in current + [name]])

    def remove_category(self, name: str) -> None:
        """등록된 분류명을 받아 목록에서 제거한다. 반환값은 없다.

        없는 이름·거래에서 사용 중인 이름은 BudgetError이다. 거래가 가리키는 분류가
        사라지지 않게 거래 파일을 먼저 확인한 후 분류 파일만 다시 쓴다.
        add_category와 달리 이 메서드에서는 인자의 앞뒤 공백을 제거하지 않는다.
        """
        current = self.categories()
        if name not in current:
            raise BudgetError("카테고리를 찾을 수 없습니다.", "category list로 확인하세요.")
        if any(t.category == name for t in self.store.transaction_stream()):
            # any는 사용 중인 거래 하나만 찾아도 멈춘다. 분류 삭제가 거래를 지우지는 않는다.
            raise BudgetError("사용 중인 카테고리는 삭제할 수 없습니다.", "거래의 카테고리를 먼저 변경하세요.")
        self.store.save("categories", [{"name": v} for v in current if v != name])

    # === 거래 생성·조회·수정·삭제 ===
    def make_transaction(self, *, date: str, type: str, category: str,
                         amount: object, memo: str = "", tags: str | list[str] | None = None,
                         identifier: str | None = None) -> Transaction:
        """이름으로 지정한 거래 필드를 검증하여 새 Transaction을 반환한다. 저장은 하지 않는다.

        date/type/category/amount는 필수, memo/tags는 선택, identifier는 ID 보존용이다.
        날짜·유형·등록 분류·양수 정수가 잘못되면 BudgetError이다. memo는 문자열,
        tags 목록의 원소는 문자열을 기대한다. CLI/CSV는 이 입력 형태를 맞춰 전달한다.
        추가·수정·import가 같은 검증과 공백·태그 정리를 공유하도록 만든 함수이다.
        """
        # * 뒤의 인자는 이름으로 전달한다. identifier가 없거나 비면 새 ID를 만든다.
        # 범용 고유 식별자(Universally Unique Identifier, UUID)의 무작위 값을 사용한다.
        # ID는 날짜나 줄 번호와 분리되어 날짜 수정·정렬 후에도 대상을 식별할 수 있다.
        return Transaction(id=identifier or "TX-" + uuid.uuid4().hex,
                           date=validate_date(date), type=validate_type(type),
                           category=self.require_category(category), amount=validate_amount(amount),
                           memo=memo.strip(), tags=parse_tags(tags))

    def add(self, **values: object) -> Transaction:
        """make_transaction에 넘길 필드를 받아 거래를 저장하고 그 객체를 반환한다.

        기존 목록을 읽어 ID 중복을 확인하고 전체 거래를 재저장한다. 검증·저장 실패는
        BudgetError이다. **values는 여러 이름 인자를 사전으로 받는 문법이다.
        일반 CLI 추가는 identifier를 주지 않는다. 고정된 중복 identifier를 직접 주면
        아래 재생성 루프가 끝나지 않을 수 있으므로 그런 호출은 피해야 한다.
        """
        current = self.store.transactions()
        item = self.make_transaction(**values)
        ids = {t.id for t in current}
        while item.id in ids:
            # 보통은 즉시 통과한다. 무작위 ID가 기존 ID와 겹치면 거래를 다시 만든다.
            item = self.make_transaction(**values)
        self.store.save_transactions(current + [item])
        # Store가 날짜 내림차순·동일 날짜 ID 오름차순 정렬 후 transactions.jsonl을 교체한다.
        return item

    def list(self, limit: int = 20) -> Iterator[Transaction]:
        """최대 limit개 거래를 파일 순서대로 제공한다. limit은 기본 20인 양수 정수이다.

        제너레이터(Generator)는 전체 결과를 미리 만들지 않고 yield마다 하나씩 건넨다.
        호출 시에는 실행을 준비하고, for/next로 순회할 때 검증·읽기가 시작된다.
        limit 오류와 읽기 BudgetError도 그때 발생한다. Iterator는 순회 가능한 반환형을
        설명하는 타입 힌트(type hint)이며 실행 중 검사를 자동으로 하지는 않는다.
        """
        if limit <= 0:
            raise BudgetError("--limit은 1 이상이어야 합니다.")
        for n, item in enumerate(self.store.transaction_stream()):
            # n은 0부터 센다. 중단 판단 전에 다음 거래를 읽으므로 한 건 더 읽을 수 있다.
            if n >= limit:
                break
            yield item

    def search(self, *, date_from: str | None = None, date_to: str | None = None,
               category: str | None = None, type: str | None = None,
               query: str | None = None, tag: str | None = None) -> Iterator[Transaction]:
        """선택 조건을 모두 만족하는 거래를 하나씩 제공한다. 파일 내용은 바꾸지 않는다.

        date_from/date_to는 양 끝을 포함하는 날짜, category/type은 정확히 같은 값,
        query는 대소문자 구분 없는 메모 부분 문자열, tag는 태그 목록의 정확한 항목이다.
        생략하거나 빈 문자열인 조건은 적용하지 않는다. 순회 시 잘못된 날짜·역순 기간·
        미등록 분류·유형·읽기 오류가 BudgetError로 전달된다. 조건별 continue로
        불일치를 제외하므로 조합 검색도 별도 결과 목록 없이 처리할 수 있다.
        """
        if date_from:
            validate_date(date_from)
        if date_to:
            validate_date(date_to)
        if date_from and date_to and date_from > date_to:
            # 검증된 YYYY-MM-DD는 문자열 비교와 날짜 비교의 순서가 같다.
            raise BudgetError("기간 시작일이 종료일보다 늦습니다.", "--from과 --to의 순서를 확인하세요.")
        if category:
            category = self.require_category(category)
        if type:
            validate_type(type)
        for item in self.store.transaction_stream():
            # 하나라도 조건에 맞지 않으면 continue로 다음 거래로 넘어간다.
            # 끝의 yield에 도달한 거래만 반환되며 파일의 최신순이 유지된다.
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
        """거래 ID와 변경할 필드를 받아 수정 거래를 저장·반환한다.

        없는 ID나 잘못된 변경값은 BudgetError이다. CLI에서 선택한 필드만 전달하며
        None은 변경에서 제외한다. 기존 값과 합친 뒤 재검증하여 누락 필드를 보존한다.
        ID는 유지하고 날짜가 바뀌면 Store의 재정렬로 조회 위치가 달라질 수 있다.
        """
        current = self.store.transactions()
        match = next((t for t in current if t.id == identifier), None)
        # next(..., None)는 첫 일치 거래를 찾고, 없으면 None을 돌려준다.
        if match is None:
            raise BudgetError("수정할 거래를 찾지 못했습니다.", "list로 거래 ID를 확인하세요.")
        merged = match.to_dict()
        merged.update({k: v for k, v in changes.items() if v is not None})
        # 저장용 필드명 id를 제거하고 identifier로 원래 ID를 명시해 새 거래 객체를 만든다.
        merged.pop("id")
        item = self.make_transaction(identifier=identifier, **merged)
        self.store.save_transactions([item if t.id == identifier else t for t in current])
        # 해당 ID의 거래만 바꾼 목록으로 파일 전체를 교체한다. 다른 거래는 유지한다.
        return item

    def delete(self, identifier: str) -> None:
        """ID에 해당하는 거래를 빼고 transactions.jsonl을 재저장한다. 반환값은 없다.

        없는 ID는 BudgetError이다. 파일의 한 줄을 직접 지우는 대신 남길 거래를
        모아 Store에 전달하므로 정렬·안전한 교체 방식이 다른 변경 작업과 같다.
        """
        current = self.store.transactions()
        if not any(t.id == identifier for t in current):
            raise BudgetError("삭제할 거래를 찾지 못했습니다.", "list로 거래 ID를 확인하세요.")
        self.store.save_transactions([t for t in current if t.id != identifier])

    # === 월별 예산과 집계 ===
    def set_budget(self, month: str, amount: object) -> None:
        """월 YYYY-MM과 금액을 받아 budgets.jsonl에 지정한다. 반환값은 없다.

        월·양수 정수 검증 실패나 저장 실패는 BudgetError이다. 같은 월의 기존 행은
        제외하고 새 행을 붙여 갱신하며, 다른 월 예산과 거래 파일은 유지한다.
        """
        month = validate_month(month)
        amount = validate_amount(amount)
        existing = [row for row in self.store.stream("budgets") if row.get("month") != month]
        existing.append({"month": month, "amount": amount})
        self.store.save("budgets", existing)

    def summary(self, month: str, top: int = 3) -> dict:
        """월과 양수 TOP 개수를 받아 수입·지출·잔액·예산·지출 분류 순위 사전을 반환한다.

        월·top 오류와 읽기 실패는 BudgetError이다. 거래를 한 번씩 읽으며 더하므로
        전체 거래 목록은 필요하지 않다. 등록 예산이 없으면 budget/usage는 None,
        over는 False이다. 조회만 하며 파일을 수정하지 않는다.
        """
        month = validate_month(month)
        if top <= 0:
            raise BudgetError("--top은 1 이상이어야 합니다.")
        income = expense = count = 0
        by_category: dict[str, int] = {}
        for item in self.store.transaction_stream():
            # 선택 월만 집계하고, 분류별 TOP은 수입을 제외한 지출만 합산한다.
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
        # 사용률은 지출/예산의 백분율을 소수 둘째 자리로 반올림한다.
        # TOP은 지출 합계 내림차순, 동률이면 분류명 문자열 오름차순으로 top개를 고른다.
        return {"count": count, "income": income, "expense": expense,
                "balance": income - expense, "budget": budget,
                "usage": round(100 * expense / budget, 2) if budget else None,
                "over": expense > budget if budget else False,
                "top": sorted(by_category.items(), key=lambda x: (-x[1], x[0]))[:top]}

    # === CSV import: 유효한 행만 모아 한 번 저장 ===
    def import_csv(self, source: Path) -> tuple[int, list[str]]:
        """CSV 경로를 받아 (추가 건수, 실패 행 안내 목록)을 반환한다.

        헤더 이름·순서가 다르거나 파일 읽기에 실패하면 BudgetError이며 거래 반영은 없다.
        개별 행의 검증 실패는 안내 목록에 모으고, 나머지 유효 행만 마지막에 저장한다.
        이 부분 성공을 CLI가 종료 코드 2로 알린다. 저장 실패는 BudgetError로 전달한다.
        CSV에는 ID가 없으므로 새 ID를 발급하며 같은 파일을 재import하면 중복 거래가 생긴다.
        분류는 미리 등록되어 있어야 하며 CSV에서 새 분류를 자동 생성하지 않는다.
        """
        new_items: list[Transaction] = []
        failures: list[str] = []
        try:
            # utf-8-sig는 UTF-8의 시작 표식(Byte Order Mark, BOM)이 있어도 헤더에서 제거한다.
            # newline=""는 줄바꿈 처리를 csv 모듈에 맡겨 따옴표 안 줄바꿈 등을 읽게 한다.
            with source.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                # 첫 행을 키로 사용한다. 필수 헤더 전체와 순서가 정확히 같아야 한다.
                if reader.fieldnames != CSV_FIELDS:
                    raise BudgetError("CSV 헤더가 올바르지 않습니다.",
                                      "date,type,category,amount,memo,tags 순서의 헤더를 사용하세요.")
                for line_no, row in enumerate(reader, 2):
                    # 헤더 다음을 2행으로 센다. 셀 안 줄바꿈이 있으면 실제 물리 행과 다를 수 있다.
                    try:
                        # 열이 넘치면 None 키, 열이 부족하면 None 값이 생기므로 둘 다 거른다.
                        if None in row or any(v is None for v in row.values()):
                            raise BudgetError("CSV 열 개수가 올바르지 않습니다.")
                        new_items.append(self.make_transaction(
                            date=row["date"], type=row["type"], category=row["category"],
                            amount=row["amount"], memo=row["memo"], tags=row["tags"]))
                    except BudgetError as error:
                        # 예외(Exception)를 행 단위로 처리하므로 다음 행 검사는 계속된다.
                        failures.append(f"{line_no}행: {error.reason} [힌트] {error.hint}")
        except (OSError, UnicodeError, csv.Error) as error:
            raise BudgetError("CSV 파일을 읽을 수 없습니다.", "경로·UTF-8 인코딩·CSV 형식을 확인하세요.") from error
        if new_items:
            # 전체 읽기가 끝난 후 기존 거래 + 유효 행을 정렬하여 JSONL 한 파일을 교체한다.
            # 유효 행이 하나도 없으면 저장을 호출하지 않아 거래 파일을 다시 쓰지 않는다.
            self.store.save_transactions(self.store.transactions() + new_items)
        return len(new_items), failures

    # === CSV export: 기간 선택, 대상 보호, 임시 파일 교체 ===
    def export_csv(self, dest: Path, *, month: str | None = None,
                   date_from: str | None = None, date_to: str | None = None,
                   overwrite: bool = False) -> int:
        """목적지와 월 또는 양 끝 포함 날짜 범위를 받아 CSV를 쓰고 거래 건수를 반환한다.

        month가 있으면 날짜 범위보다 우선한다. 기간 오류·내부 JSONL 대상 지정·허용하지
        않은 기존 파일 교체·출력 실패는 BudgetError이다. overwrite=True일 때만 기존
        CSV 교체를 허용한다. 거래를 순서대로 읽어 임시 CSV에 쓰고 완성 후 교체하므로
        쓰는 도중 실패해 기존 출력이 일부 내용으로 잘리는 일을 줄인다. 내부 저장은 바꾸지 않는다.
        """
        if month:
            validate_month(month)
            date_from = month + "-01"
            date_to = month + "-31"
        elif not date_from or not date_to:
            raise BudgetError("내보낼 기간을 지정해야 합니다.", "--month 또는 --from과 --to를 지정하세요.")
        # 월 지정의 '-31'은 문자열 범위의 상한이다. 2월 31일을 거래 날짜로 만드는 것이 아니다.
        # search를 호출하지 않고 직접 필터링하므로 명시한 날짜 범위만 실제 날짜로 검사한다.
        if not month:
            validate_date(date_from)
            validate_date(date_to)
            if date_from > date_to:
                raise BudgetError("기간 시작일이 종료일보다 늦습니다.")
        if dest.resolve() in {self.store.path(n).resolve() for n in ("transactions", "categories", "budgets")}:
            # resolve로 절대 경로와 심볼릭 링크를 해석해 내부 세 파일과 같은 대상을 거른다.
            raise BudgetError("내부 데이터 파일에 CSV를 덮어쓸 수 없습니다.", "다른 --out 경로를 지정하세요.")
        if dest.exists() and not overwrite:
            raise BudgetError("내보낼 CSV가 이미 존재합니다.", "--overwrite를 지정하거나 새 파일명을 사용하세요.")
        temp: Path | None = None
        written = 0
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            # 같은 폴더에 임시 파일을 만들면 동일 파일 시스템 안에서 교체할 수 있다.
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                             dir=dest.parent, prefix=".export-", suffix=".tmp",
                                             delete=False) as handle:
                temp = Path(handle.name)
                writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
                writer.writeheader()
                # 최신순으로 읽고 기간 밖은 제외한다. ID는 내보내지 않고 tags는 쉼표로 합친다.
                # csv 모듈이 쉼표·따옴표·줄바꿈을 포함한 셀의 따옴표 처리를 맡는다.
                for item in self.store.transaction_stream():
                    if not date_from <= item.date <= date_to:
                        continue
                    writer.writerow({"date": item.date, "type": item.type,
                                     "category": item.category, "amount": item.amount,
                                     "memo": item.memo, "tags": ",".join(item.tags)})
                    written += 1
                # flush는 Python 버퍼를 운영체제로, fsync는 파일 내용을 저장 장치로 보낸다.
                handle.flush()
                os.fsync(handle.fileno())
            # 파일을 닫은 뒤 os.replace로 완성된 파일을 원자적으로 교체한다.
            # 한 파일 교체만 보호한다. 동시 쓰기 잠금이나 여러 파일 일괄 반영은 하지 않는다.
            # 부모 디렉터리 fsync도 없어 모든 전원 장애의 복구를 보장하지 않는다.
            # 앞의 exists 확인과 교체 사이에 다른 프로세스가 파일을 만들 가능성도 남는다.
            os.replace(temp, dest)
        except (OSError, UnicodeError, csv.Error) as error:
            raise BudgetError("CSV를 내보내지 못했습니다.", "출력 경로와 쓰기 권한을 확인하세요.") from error
        finally:
            # 실패해도 남은 임시 파일을 정리한다. 정리 오류는 원래 실패 이유를 가리지 않는다.
            if temp is not None:
                try:
                    temp.unlink(missing_ok=True)
                except OSError:
                    pass
        return written
