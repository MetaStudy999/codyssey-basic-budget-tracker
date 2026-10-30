"""Independent CLI verification. Run with PYTHONDONTWRITEBYTECODE=1; no personal data."""
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys
import tempfile


SOURCE = Path(__file__).resolve().parents[1] / "04-src"


def verify():
    root = Path(tempfile.mkdtemp(prefix="b2-round04-runtime-"))
    data = root / "data"
    calls = 0
    print("Actual execution UTC:", datetime.now(timezone.utc).isoformat())
    print("Platform:", platform.system(), platform.release(), "Python", platform.python_version())
    print("Base HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCE, text=True).strip())
    print("Worktree source SHA256 (includes uncommitted fixes):")
    for file in sorted((SOURCE / "budget_app").glob("*.py")):
        print(file.name, hashlib.sha256(file.read_bytes()).hexdigest())
    print("Synthetic data only:", root)

    def snapshot():
        return {p.name: p.read_bytes() for p in data.glob("*.jsonl")}

    def run(*args, stdin=None, code=0, contains=(), unchanged=False, help_only=False):
        nonlocal calls
        before = snapshot()
        argv = [sys.executable, "-m", "budget_app", "--data-dir", str(data), *args]
        result = subprocess.run(argv, cwd=SOURCE, text=True, input=stdin, capture_output=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
        calls += 1
        print("\n$", shlex.join(argv))
        if stdin is not None:
            print("stdin (synthetic):", repr(stdin))
        if result.stdout:
            print(result.stdout.splitlines()[0] + " [remaining help omitted]" if help_only
                  else result.stdout.rstrip())
        if result.stderr:
            print("stderr:", result.stderr.rstrip())
        print("exit=", result.returncode)
        assert result.returncode == code, (args, result)
        assert "Traceback" not in result.stdout + result.stderr
        for text in contains:
            assert text in result.stdout + result.stderr, (args, text)
        if unchanged:
            assert snapshot() == before, args
            print("CHECK: all three JSONL file contents unchanged PASS")
        return result.stdout

    try:
        run("--help", help_only=True)
        for command in ("add", "list", "search", "update", "delete", "category", "budget", "summary", "import", "export"):
            run(command, "--help", help_only=True)
        for args in (("category", "add"), ("category", "list"), ("category", "remove"), ("budget", "set")):
            run(*args, "--help", help_only=True)
        run("category", "list", contains=("food", "salary"))
        assert len(snapshot()) == 3
        run("category", "add", stdin="study\n", contains=("category=study",))
        run("category", "add", "--name", "unused")
        run("category", "remove", "--name", "unused")

        def add(date, kind, category, amount, memo, tags):
            output = run("add", stdin="\n".join((date, kind, category, amount, memo, tags)) + "\n",
                         contains=("[저장 완료] id=TX-",))
            return output.split("id=")[-1].strip()

        newest = add("2026-10-30", "expense", "food", "1500", "가상 lunch", "meal,lunch")
        oldest = add("2026-10-01", "income", "salary", "10000", "가상 income", "pay")
        middle = add("2026-10-15", "expense", "study", "2000", "가상 book", "learn")
        output = run("list", "--limit", "2")
        assert [line.split(" | ")[0] for line in output.splitlines()] == [newest, middle]
        output = run("search", "--from", "2026-10-01", "--to", "2026-10-31",
                     "--category", "food", "--type", "expense", "--q", "LUNCH", "--tag", "meal")
        assert output.split(" | ")[0] == newest
        run("update", "--id", oldest, "--date", "2026-10-31", "--amount", "12000",
            "--memo", "가상 updated", "--tags", "pay,updated")
        output = run("list", "--limit", "3")
        assert [line.split(" | ")[0] for line in output.splitlines()] == [oldest, newest, middle]
        output = run("search", "--type", "expense")
        assert [line.split(" | ")[0] for line in output.splitlines()] == [newest, middle]
        run("budget", "set", "--month", "2026-10", "--amount", "3000")
        run("summary", "--month", "2026-10", "--top", "2",
            contains=("총 수입: 12000원", "총 지출: 3500원", "잔액: 8500원", "사용률 116.67%", "월 예산 초과", "1) study: 2000원", "2) food: 1500원"))
        # Every command starts a fresh process: this also proves persisted custom category/budget/transactions.
        run("category", "list", contains=("study",))
        rows = [json.loads(line) for line in (data / "transactions.jsonl").read_text().splitlines()]
        assert {r["id"] for r in rows} == {newest, oldest, middle}
        print("CHECK: restart persistence, three JSONL files, newest order PASS")
        run("summary", "--month", "2026-09", contains=("데이터 없음", "총 지출: 0원"))
        run("category", "remove", "--name", "study", code=2, contains=("사용 중", "[힌트]"), unchanged=True)
        run("update", "--id", "MISSING", "--amount", "10", code=2, contains=("[힌트]",), unchanged=True)
        run("delete", "--id", "MISSING", code=2, contains=("[힌트]",), unchanged=True)
        for values in (("2026-02-30", "expense", "food", "1"),
                       ("2026-10-30", "expense", "food", "0"),
                       ("2026-10-30", "expense", "food", "-1"),
                       ("2026-10-30", "expense", "food", "1.5"),
                       ("2026-10-30", "invalid", "food", "1"),
                       ("2026-10-30", "expense", "MISSING", "1")):
            run("add", stdin="\n".join((*values, "", "")) + "\n", code=2, contains=("[힌트]",), unchanged=True)
        run("add", stdin="2026-10-30\n", code=2, contains=("입력이 중단", "[힌트]"), unchanged=True)
        run("delete", code=2, contains=("[힌트]",), unchanged=True)
        run("search", "--from", "2026-11-01", "--to", "2026-10-01", code=2, contains=("[힌트]",), unchanged=True)

        report = root / "report.csv"
        run("export", "--out", str(report), "--month", "2026-10", contains=("(3 records)",))
        with report.open(encoding="utf-8", newline="") as handle:
            exported = list(csv.reader(handle))
        assert exported[0] == ["date", "type", "category", "amount", "memo", "tags"]
        assert len(exported) == 4 and exported[2][5] == "meal,lunch"
        print("ACTUAL CSV UTF-8 contents:\n" + report.read_text(encoding="utf-8"))
        before_report = report.read_bytes()
        run("export", "--out", str(report), "--month", "2026-10", code=2,
            contains=("이미 존재", "[힌트]"), unchanged=True)
        assert report.read_bytes() == before_report
        print("CHECK: duplicate output protection (byte comparison) PASS")
        run("export", "--out", str(report), "--month", "2026-10", "--overwrite", contains=("(3 records)",))
        run("export", "--out", str(root / "range.csv"), "--from", "2026-10-15", "--to", "2026-10-30", contains=("(2 records)",))
        run("export", "--out", str(root / "no-period.csv"), code=2, contains=("[힌트]",), unchanged=True)
        for name in ("transactions", "categories", "budgets"):
            run("export", "--out", str(data / (name + ".jsonl")), "--month", "2026-10", "--overwrite",
                code=2, contains=("내부 데이터", "[힌트]"), unchanged=True)

        mixed = root / "mixed.csv"
        mixed.write_text("date,type,category,amount,memo,tags\n"
                         "2026-10-20,expense,food,100,가상 imported,meal\n"
                         "2026-02-30,expense,food,500,가상 invalid,meal\n"
                         "2026-10-21,income,salary,200,가상 imported,pay\n", encoding="utf-8")
        print("ACTUAL synthetic import CSV:\n" + mixed.read_text(encoding="utf-8"))
        run("import", "--from", str(mixed), code=2,
            contains=("imported=2, skipped=1", "3행", "[힌트]"))
        assert len((data / "transactions.jsonl").read_text().splitlines()) == 5
        valid = root / "valid.csv"
        valid.write_text("date,type,category,amount,memo,tags\n"
                         "2026-11-01,expense,food,100,가상 valid,meal\n", encoding="utf-8")
        run("import", "--from", str(valid), contains=("imported=1, skipped=0",))
        bad = root / "bad.csv"
        bad.write_text("bad,header\n1,2\n", encoding="utf-8")
        run("import", "--from", str(bad), code=2, contains=("CSV 헤더", "[힌트]"), unchanged=True)
        run("import", "--from", str(root / "missing.csv"), code=2, contains=("[힌트]",), unchanged=True)
        run("delete", "--id", middle)
        run("category", "remove", "--name", "study")
        assert "study" not in run("category", "list")
        assert middle not in run("list", "--limit", "20")
        run("summary", "--month", "2026-10", contains=("총 수입: 12200원", "총 지출: 1600원", "잔액: 10600원"))

        original = (data / "transactions.jsonl").read_bytes()
        (data / "transactions.jsonl").write_text("{broken JSON\n", encoding="utf-8")
        run("list", code=2, contains=("[힌트]",), unchanged=True)
        (data / "transactions.jsonl").write_bytes(original)
        print("\nPASS:", calls, "fresh CLI processes; all assertions passed")
    finally:
        shutil.rmtree(root)
        print("CLEANUP: temporary synthetic data removed:", not root.exists())


if __name__ == "__main__":
    verify()
