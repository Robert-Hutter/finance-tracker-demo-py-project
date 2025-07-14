import unittest
import os
from finance_tracker.budgets import BudgetManager

class TestBudgetManager(unittest.TestCase):
    def setUp(self):
        self.user_id = "test_user"
        self.manager = BudgetManager(self.user_id)
        self.data_file = f"budgets_{self.user_id}.json"
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_set_valid_budget(self):
        self.manager.set_budget("Food", 200.0, "monthly", 0.9)
        self.assertEqual(self.manager.budgets["Food_monthly"].amount, 200.0)
        self.assertEqual(self.manager.budgets["Food_monthly"].alert_threshold, 0.9)

    def test_set_invalid_budget(self):
        with self.assertRaises(ValueError):
            self.manager.set_budget("Food", -100.0)
        with self.assertRaises(ValueError):
            self.manager.set_budget("", 100.0)
        with self.assertRaises(ValueError):
            self.manager.set_budget("Food", 100.0, period="invalid")

    def test_add_spending(self):
        self.manager.set_budget("Food", 200.0)
        self.manager.add_spending("Food", 50.0)
        self.assertEqual(self.manager.budgets["Food_monthly"].spending, 50.0)

    def test_add_invalid_spending(self):
        with self.assertRaises(ValueError):
            self.manager.add_spending("Invalid category", 50.0)
        self.manager.set_budget("Food", 200.0)
        with self.assertRaises(ValueError):
            self.manager.add_spending("Food", -50.0)

    def test_get_budget_status(self):
        self.manager.set_budget("Food", 200.0, alert_threshold=0.8)
        self.manager.add_spending("Food", 170.0)
        status = self.manager.get_budget_status("Food")
        self.assertEqual(status["remaining"], 30.0)
        self.assertTrue(status["alert_triggered"])
        self.assertFalse(status["over_budget"])

    def test_reset_budget(self):
        self.manager.set_budget("Food", 200.0)
        self.manager.add_spending("Food", 100.0)
        self.assertTrue(self.manager.reset_budget("Food"))
        self.assertEqual(self.manager.budgets["Food_monthly"].spending, 0.0)