import unittest
import os
from finance_tracker.income import IncomeTracker, Income
from finance_tracker.expenses import ExpenseTracker
from finance_tracker.reports import FinancialReport
from finance_tracker.budgets import BudgetManager
from finance_tracker.cli import FinanceTrackerCLI
from io import StringIO
from contextlib import redirect_stdout

class TestIncomeTracker(unittest.TestCase):
    def setUp(self):
        self.user_id = "test_user"
        self.income_tracker = IncomeTracker(self.user_id)
        self.expense_tracker = ExpenseTracker(self.user_id)
        self.budget_manager = BudgetManager(self.user_id)
        self.report_generator = FinancialReport(self.user_id, self.expense_tracker, self.budget_manager)
        self.cli = FinanceTrackerCLI()
        self.data_file = f"income_{self.user_id}.json"
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
        # Register and login for CLI tests
        self.cli.do_register("testuser password123 test@example.com")
        self.cli.do_login("testuser password123")

    def tearDown(self):
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_add_valid_income(self):
        income_id = self.income_tracker.add_income(1000.0, "Salary", "Monthly paycheck", tags=["work"])
        self.assertEqual(len(self.income_tracker.incomes), 1)
        income = self.income_tracker.get_income_by_id(income_id)
        self.assertEqual(income["amount"], 1000.0)
        self.assertEqual(income["category"], "Salary")
        self.assertEqual(income["description"], "Monthly paycheck")
        self.assertEqual(income["tags"], ["work"])

    def test_add_recurring_income(self):
        income_id = self.income_tracker.add_income(500.0, "Freelance", "Project payment", 
                                                  is_recurring=True, recurrence_period="monthly")
        recurring = self.income_tracker.get_recurring_incomes()
        self.assertEqual(len(recurring), 1)
        self.assertEqual(recurring[0]["recurrence_period"], "monthly")
        self.assertEqual(recurring[0]["amount"], 500.0)

    def test_add_invalid_income(self):
        with self.assertRaises(ValueError):
            self.income_tracker.add_income(-100.0, "Salary", "Invalid amount")
        with self.assertRaises(ValueError):
            self.income_tracker.add_income(100.0, "", "No category")
        with self.assertRaises(ValueError):
            self.income_tracker.add_income(100.0, "Salary", "", is_recurring=True)

    def test_get_income_by_category(self):
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck")
        self.income_tracker.add_income(200.0, "Freelance", "Side project")
        self.income_tracker.add_income(500.0, "Salary", "Bonus")
        salary_incomes = self.income_tracker.get_incomes_by_category("Salary")
        self.assertEqual(len(salary_incomes), 2)
        self.assertEqual(sum(inc["amount"] for inc in salary_incomes), 1500.0)

    def test_get_income_by_tag(self):
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck", tags=["work", "monthly"])
        self.income_tracker.add_income(200.0, "Freelance", "Side project", tags=["work"])
        tagged_incomes = self.income_tracker.get_incomes_by_tag("work")
        self.assertEqual(len(tagged_incomes), 2)
        self.assertEqual(sum(inc["amount"] for inc in tagged_incomes), 1200.0)

    def test_get_total_income(self):
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck", date="2025-01-01")
        self.income_tracker.add_income(500.0, "Freelance", "Project", date="2025-01-15")
        self.income_tracker.add_income(200.0, "Investment", "Dividend", date="2025-02-01")
        total = self.income_tracker.get_total_income()
        self.assertEqual(total, 1700.0)
        total_period = self.income_tracker.get_total_income("2025-01-01", "2025-01-31")
        self.assertEqual(total_period, 1500.0)

    def test_save_and_load_income(self):
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck")
        self.income_tracker._save_to_file()
        new_tracker = IncomeTracker(self.user_id)
        new_tracker.load_from_file()
        self.assertEqual(len(new_tracker.incomes), 1)
        self.assertEqual(new_tracker.incomes[0].amount, 1000.0)

    def test_delete_income(self):
        income_id = self.income_tracker.add_income(1000.0, "Salary", "Paycheck")
        self.assertTrue(self.income_tracker.delete_income(income_id))
        self.assertIsNone(self.income_tracker.get_income_by_id(income_id))
        self.assertFalse(self.income_tracker.delete_income("nonexistent"))

    def test_update_income(self):
        income_id = self.income_tracker.add_income(1000.0, "Salary", "Paycheck")
        self.assertTrue(self.income_tracker.update_income(income_id, amount=1200.0, description="Updated paycheck"))
        income = self.income_tracker.get_income_by_id(income_id)
        self.assertEqual(income["amount"], 1200.0)
        self.assertEqual(income["description"], "Updated paycheck")
        self.assertFalse(self.income_tracker.update_income("nonexistent"))

    def test_net_balance(self):
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck", date="2025-01-01")
        self.expense_tracker.add_expense(300.0, "Food", "Grocery", date="2025-01-01")
        self.expense_tracker.add_expense(200.0, "Transport", "Bus", date="2025-01-02")
        net_balance = self.expense_tracker.get_net_balance(self.income_tracker, "2025-01-01", "2025-01-31")
        self.assertEqual(net_balance, 500.0)  # 1000 - (300 + 200)
        net_balance_all = self.expense_tracker.get_net_balance(self.income_tracker)
        self.assertEqual(net_balance_all, 500.0)

    def test_report_income_summary(self):
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck", date="2025-01-01")
        self.income_tracker.add_income(500.0, "Freelance", "Project", date="2025-01-02")
        summary = self.report_generator.generate_income_summary("2025-01-01", "2025-01-02")
        self.assertEqual(summary["category_totals"]["Salary"], 1000.0)
        self.assertEqual(summary["category_totals"]["Freelance"], 500.0)
        self.assertEqual(summary["total"], 1500.0)

    def test_report_net_balance(self):
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck", date="2025-01-01")
        self.expense_tracker.add_expense(400.0, "Food", "Grocery", date="2025-01-01")
        trend = self.report_generator.generate_trend_analysis(months=1)
        self.assertIn("2025-01", trend["net_balance"])
        self.assertEqual(trend["net_balance"]["2025-01"], 600.0)  # 1000 - 400

    def test_cli_add_income(self):
        with redirect_stdout(StringIO()) as output:
            self.cli.income_tracker = self.income_tracker  # Inject for testing
            self.cli.do_add_income("1000.0 Salary Paycheck work true monthly")
            self.assertIn("Income added with ID", output.getvalue())
        self.assertEqual(len(self.income_tracker.incomes), 1)

    def test_cli_generate_income_report(self):
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck", date="2025-01-01")
        with redirect_stdout(StringIO()) as output:
            self.cli.report_generator = self.report_generator  # Inject for testing
            self.cli.do_generate_income_report("2025-01-01 2025-01-01")
            self.assertIn("Income report generated", output.getvalue())

    def test_edge_cases(self):
        # No income
        net_balance = self.expense_tracker.get_net_balance(self.income_tracker)
        self.assertEqual(net_balance, 0.0)
        # No expenses
        self.income_tracker.add_income(1000.0, "Salary", "Paycheck")
        net_balance = self.expense_tracker.get_net_balance(self.income_tracker)
        self.assertEqual(net_balance, 1000.0)
        # Invalid date range
        self.income_tracker.add_income(500.0, "Freelance", "Project", date="2025-01-01")
        total = self.income_tracker.get_total_income("2025-02-01", "2025-01-01")
        self.assertEqual(total, 0.0)
        # Empty tags
        income_id = self.income_tracker.add_income(1000.0, "Salary", "Paycheck", tags=[])
        income = self.income_tracker.get_income_by_id(income_id)
        self.assertEqual(income["tags"], [])

if __name__ == '__main__':
    unittest.main()