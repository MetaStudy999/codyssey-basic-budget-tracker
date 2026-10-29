"""Additional edge/negative cases for the B2-1 Round 04 CLI."""
from __future__ import annotations
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from budget_app.cli import main
from budget_app.models import BudgetError
from budget_app.service import BudgetService


class EdgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.data = Path(self.tmp.name) / "records"
        self.app = BudgetService(self.data)

    def test_corrupt_jsonl_has_explanation(self):
        (self.data / "transactions.jsonl").write_text("{invalid json\n", encoding="utf-8")
        with self.assertRaisesRegex(BudgetError, "손상|읽을 수"):
            list(self.app.list())

    def test_atomic_replace_failure_keeps_old_transactions(self):
        original = self.app.add(date="2026-10-01", type="expense", category="food", amount=1000)
        before = (self.data / "transactions.jsonl").read_bytes()
        with patch("budget_app.storage.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(BudgetError):
                self.app.update(original.id, amount=2000)
        self.assertEqual((self.data / "transactions.jsonl").read_bytes(), before)
        self.assertEqual(list(self.data.glob("*.tmp")), [])

    def test_same_date_stable_order(self):
        first = self.app.add(date="2026-10-30", type="expense", category="food", amount=2000)
        second = self.app.add(date="2026-10-30", type="expense", category="food", amount=1000)
        expected = sorted([first.id, second.id])
        self.assertEqual([x.id for x in self.app.list()], expected)

    def test_export_date_range_and_no_period_is_error(self):
        self.app.add(date="2026-10-15", type="income", category="salary", amount=80000)
        self.app.add(date="2026-11-01", type="expense", category="food", amount=1000)
        dest = Path(self.tmp.name) / "range.csv"
        self.assertEqual(self.app.export_csv(dest, date_from="2026-10-01", date_to="2026-10-31"), 1)
        with self.assertRaises(BudgetError):
            self.app.export_csv(Path(self.tmp.name) / "invalid.csv")

    def test_no_account_key_or_password_is_needed(self):
        self.assertEqual(self.app.categories(), ["food", "transport", "rent", "salary", "etc"])
        self.assertTrue((self.data / "budgets.jsonl").exists())

    def test_cli_subcommand_helps(self):
        commands = ["add", "list", "search", "update", "delete", "summary",
                    "budget", "category", "import", "export"]
        for command in commands:
            with self.subTest(command=command):
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(SystemExit) as cm:
                        main([command, "--help"])
                self.assertEqual(cm.exception.code, 0)

    def test_cli_missing_id_error_code_and_hint(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(["--data-dir", str(self.data), "update", "--id", "none", "--amount", "20"])
        self.assertEqual(code, 2)
        self.assertIn("[힌트]", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())


if __name__ == "__main__":
    unittest.main()
