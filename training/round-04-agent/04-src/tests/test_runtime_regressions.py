"""Regressions discovered during independent WSL2 execution; synthetic data only."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from budget_app.cli import main
from budget_app.models import BudgetError
from budget_app.service import BudgetService


class RuntimeRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="b2-regression-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / "data"
        self.app = BudgetService(self.data)
        self.item = self.app.add(date="2026-10-30", type="expense", category="food", amount=1000)

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.data.glob("*.jsonl")}

    def run_cli(self, *args, stdin=None):
        return subprocess.run(
            [sys.executable, "-m", "budget_app", "--data-dir", str(self.data), *args],
            input=stdin, text=True, capture_output=True,
            cwd=Path(__file__).resolve().parents[1],
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False)

    def assert_friendly_error(self, result):
        self.assertEqual(result.returncode, 2)
        self.assertIn("[힌트]", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_eof_during_add_preserves_all_files(self):
        before = self.snapshot()
        self.assert_friendly_error(self.run_cli("add", stdin="2026-10-30\nexpense\n"))
        self.assertEqual(self.snapshot(), before)

    def test_keyboard_interrupt_preserves_all_files(self):
        before = self.snapshot()
        err = io.StringIO()
        with patch("builtins.input", side_effect=KeyboardInterrupt), contextlib.redirect_stderr(err):
            self.assertEqual(main(["--data-dir", str(self.data), "add"]), 2)
        self.assertIn("[힌트]", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())
        self.assertEqual(self.snapshot(), before)

    def test_corrupt_category_schema_is_friendly_and_preserved(self):
        for value in ({}, {"name": []}, {"name": ""}):
            with self.subTest(value=value):
                (self.data / "categories.jsonl").write_text(json.dumps(value) + "\n")
                before = self.snapshot()
                self.assert_friendly_error(self.run_cli("category", "add", "--name", "health"))
                self.assertEqual(self.snapshot(), before)

    def test_corrupt_budget_schema_is_friendly_and_preserved(self):
        for value in ({}, {"month": "2026-10", "amount": "broken"},
                      {"month": "2026-10", "amount": 0},
                      {"month": "2026-13", "amount": 1000},
                      {"month": "2026-10", "amount": True}):
            with self.subTest(value=value):
                (self.data / "budgets.jsonl").write_text(json.dumps(value) + "\n")
                before = self.snapshot()
                self.assert_friendly_error(self.run_cli("summary", "--month", "2026-10"))
                self.assert_friendly_error(self.run_cli("budget", "set", "--month", "2026-10", "--amount", "2000"))
                self.assertEqual(self.snapshot(), before)

    def test_argument_errors_have_hint_and_do_not_mutate(self):
        before = self.snapshot()
        for args in (("delete",), ("list", "--limit", "bad"), ("summary", "--unknown")):
            with self.subTest(args=args):
                self.assert_friendly_error(self.run_cli(*args))
        self.assertEqual(self.snapshot(), before)

    def test_partial_import_reports_hint_for_bad_row(self):
        source = self.root / "mixed.csv"
        source.write_text("date,type,category,amount,memo,tags\n"
                          "2026-10-30,expense,food,1000,ok,meal\n"
                          "2026-02-30,expense,food,1000,bad,meal\n", encoding="utf-8")
        result = self.run_cli("import", "--from", str(source))
        self.assertEqual(result.returncode, 2)
        self.assertIn("imported=1, skipped=1", result.stdout)
        self.assertIn("[힌트]", result.stdout)
        self.assertEqual(len(list(BudgetService(self.data).list())), 2)

    def test_export_replace_failure_preserves_existing_output(self):
        target = self.root / "out.csv"
        target.write_bytes(b"original report\n")
        before = self.snapshot()
        with patch("budget_app.service.os.replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(BudgetError):
                self.app.export_csv(target, month="2026-10", overwrite=True)
        self.assertEqual(target.read_bytes(), b"original report\n")
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(self.root.glob(".*.tmp")), [])

    def test_import_save_failure_preserves_all_files(self):
        source = self.root / "valid.csv"
        source.write_text("date,type,category,amount,memo,tags\n"
                          "2026-10-30,expense,food,1000,ok,meal\n", encoding="utf-8")
        before = self.snapshot()
        with patch("budget_app.storage.os.replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(BudgetError):
                self.app.import_csv(source)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(list(self.data.glob(".*.tmp")), [])
