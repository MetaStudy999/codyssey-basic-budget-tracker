"""Functional, failure-path and persistence tests for the new Round 04 implementation."""
import contextlib
import csv
import io
import inspect
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from budget_app.cli import main
from budget_app.models import BudgetError
from budget_app.service import BudgetService, CSV_FIELDS


class BudgetMissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / "data"
        self.app = BudgetService(self.folder)

    def add(self, date, amount=1000, type="expense", category="food", memo="meal", tags="a,b"):
        return self.app.add(date=date, type=type, category=category, amount=amount,
                            memo=memo, tags=tags)

    def test_three_files_and_persistence(self):
        self.app.add_category("health")
        item = self.add("2026-10-30", category="health")
        self.app.set_budget("2026-10", 2000)
        again = BudgetService(self.folder)
        self.assertTrue(all((self.folder / (x + ".jsonl")).exists()
                            for x in ("transactions", "categories", "budgets")))
        self.assertEqual([x.id for x in again.list()], [item.id])
        self.assertIn("health", again.categories())
        self.assertEqual(again.summary("2026-10")["budget"], 2000)

    def test_out_of_order_input_still_lists_latest_date_first(self):
        first = self.add("2026-10-30", 3000)
        later = self.add("2026-10-01", 2000)
        self.assertTrue(inspect.isgenerator(self.app.list()))
        self.assertTrue(inspect.isgenerator(self.app.search(category="food")))
        self.assertEqual([x.id for x in self.app.list(2)], [first.id, later.id])
        self.assertEqual([x.id for x in self.app.search(tag="a")], [first.id, later.id])

    def test_search_all_filters(self):
        self.add("2026-10-01", memo="walk", tags="move")
        found = self.add("2026-10-30", memo="lunch", tags="meal")
        result = list(self.app.search(date_from="2026-10-01", date_to="2026-10-31",
                                      category="food", type="expense", query="LUNCH", tag="meal"))
        self.assertEqual([x.id for x in result], [found.id])

    def test_update_date_reorders_and_keeps_id(self):
        a = self.add("2026-10-01")
        b = self.add("2026-10-10")
        updated = self.app.update(a.id, date="2026-10-30", amount="3400")
        self.assertEqual(updated.id, a.id)
        self.assertEqual(updated.amount, 3400)
        self.assertEqual([x.id for x in BudgetService(self.folder).list()], [a.id, b.id])
        self.app.delete(a.id)
        self.assertEqual(len(list(self.app.list())), 1)
        c = self.add("2026-10-11")
        self.assertNotIn(c.id, {a.id, b.id})

    def test_missing_id_leaves_original(self):
        original = self.add("2026-10-30")
        before = (self.folder / "transactions.jsonl").read_bytes()
        with self.assertRaises(BudgetError):
            self.app.update("no-such-id", amount=333)
        with self.assertRaises(BudgetError):
            self.app.delete("no-such-id")
        self.assertEqual(before, (self.folder / "transactions.jsonl").read_bytes())
        self.assertEqual(next(self.app.list()).id, original.id)

    def test_summary_and_budget(self):
        self.app.add(date="2026-10-01", type="income", category="salary", amount=100000)
        self.add("2026-10-30", 30000)
        self.app.set_budget("2026-10", 20000)
        s = self.app.summary("2026-10")
        self.assertEqual(s["balance"], 70000)
        self.assertEqual(s["usage"], 150.0)
        self.assertTrue(s["over"])
        self.assertEqual(s["top"], [("food", 30000)])
        self.assertEqual(self.app.summary("2026-09")["count"], 0)

    def test_category_in_use_protected(self):
        self.add("2026-10-30")
        with self.assertRaises(BudgetError):
            self.app.remove_category("food")
        self.app.add_category("health")
        self.app.remove_category("health")
        self.assertNotIn("health", self.app.categories())

    def test_validation(self):
        for payload in [dict(date="2026-02-30"), dict(amount="0"), dict(amount="-10"),
                        dict(type="unknown"), dict(category="unknown")]:
            args = dict(date="2026-10-30", type="expense", category="food", amount=1000)
            args.update(payload)
            with self.assertRaises(BudgetError):
                self.app.add(**args)
        with self.assertRaises(BudgetError):
            list(self.app.search(date_from="2026-11-02", date_to="2026-11-01"))

    def test_csv_export_header_and_overwrite(self):
        self.add("2026-10-30", tags="meal,night")
        target = Path(self.tmp.name) / "report.csv"
        self.assertEqual(self.app.export_csv(target, month="2026-10"), 1)
        with target.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(list(rows[0]), CSV_FIELDS)
        self.assertEqual(rows[0]["tags"], "meal,night")
        with self.assertRaises(BudgetError):
            self.app.export_csv(target, month="2026-10")
        self.assertEqual(self.app.export_csv(target, month="2026-10", overwrite=True), 1)
        with self.assertRaises(BudgetError):
            self.app.export_csv(self.folder / "transactions.jsonl", month="2026-10", overwrite=True)

    def test_import_partial_and_exit_code(self):
        source = Path(self.tmp.name) / "in.csv"
        with source.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(CSV_FIELDS)
            w.writerow(["2026-10-30", "expense", "food", "1000", "a", "x"])
            w.writerow(["2026-02-30", "expense", "food", "1000", "bad", "x"])
            w.writerow(["2026-10-01", "income", "salary", "10000", "ok", "y"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = main(["--data-dir", str(self.folder), "import", "--from", str(source)])
        self.assertEqual(rc, 2)
        self.assertIn("imported=2, skipped=1", output.getvalue())
        self.assertEqual(len(list(BudgetService(self.folder).list())), 2)

    def test_bad_header_import_writes_nothing(self):
        source = Path(self.tmp.name) / "bad.csv"
        source.write_text("bad,header\n1,2\n", encoding="utf-8")
        with self.assertRaises(BudgetError):
            self.app.import_csv(source)
        self.assertEqual(len(list(self.app.list())), 0)

    def test_cli_help_error_and_decorator(self):
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as help_exit:
                main(["--help"])
        self.assertEqual(help_exit.exception.code, 0)
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            rc = main(["--data-dir", str(self.folder), "delete", "--id", "missing"])
        self.assertNotEqual(rc, 0)
        self.assertIn("[힌트]", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())

    def test_cli_interactive_add(self):
        output = io.StringIO()
        with patch("builtins.input", side_effect=["2026-10-30", "expense", "food", "1200", "점심", "lunch"]):
            with contextlib.redirect_stdout(output):
                rc = main(["--data-dir", str(self.folder), "add"])
        self.assertEqual(rc, 0)
        self.assertIn("[저장 완료]", output.getvalue())
        self.assertEqual(len(list(BudgetService(self.folder).list())), 1)


if __name__ == "__main__":
    unittest.main()
