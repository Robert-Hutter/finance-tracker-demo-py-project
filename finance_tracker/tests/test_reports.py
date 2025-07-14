import unittest
import os
from datetime import datetime, timedelta
from finance_tracker.expenses import ExpenseTracker
from finance_tracker.budgets import BudgetManager
from finance_tracker.reports import FinancialReport

class TestFinancialReport(unittest.TestCase):
    def setUp(self):
        self.user_id = "test_user"
        self.expense_tracker = ExpenseTracker(self.user_id)
        self.budget_manager = BudgetManager(self.user_id)
        self.report_generator = FinancialReport(self.user_id, self.expense_tracker, self.budget_manager)
        self.report_dir = f"reports_{self.user_id}"
        if os.path.exists(self.report_dir):
            import shutil
            shutil.rmtree(self.report_dir)

    def test_generate_category_summary(self):
        self.expense_tracker.add_expense(50.0, "Food", "Lunch", date="2025-01-01")
        self.expense_tracker.add_expense(30.0, "Transport", "Bus", date="2025-01-02")
        summary = self.report_generator.generate_category_summary("2025-01-01", "2025-01-02")
        self.assertEqual(summary["category_totals"]["Food"], 50.0)
        self.assertEqual(summary["category_totals"]["Transport"], 30.0)
        self.assertEqual(summary["total"], 80.0)

    def test_generate_budget_comparison(self):
        self.budget_manager.set_budget("Food", 200.0)
        self.budget_manager.add_spending("Food", 150.0)
        comparison = self.report_generator.generate_budget_comparison()
        self.assertEqual(len(comparison), 1)
        self.assertEqual(comparison[0]["remaining"], 50.0)

    def test_generate_trend_analysis(self):
        first_date = datetime.now() - timedelta(days=10)
        second_date = datetime.now() - timedelta(days=45)
        self.expense_tracker.add_expense(50.0, "Food", "Lunch", date=first_date.strftime("%Y-%m-%d"))
        self.expense_tracker.add_expense(30.0, "Food", "Dinner", date=second_date.strftime("%Y-%m-%d"))
        trend = self.report_generator.generate_trend_analysis(months=2)
        self.assertIn(first_date.strftime("%Y-%m"), trend["monthly_totals"])
        self.assertIn(second_date.strftime("%Y-%m"), trend["monthly_totals"])
        self.assertEqual(trend["monthly_totals"][first_date.strftime("%Y-%m")], 50.0)