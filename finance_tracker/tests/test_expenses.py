import unittest
import os
from finance_tracker.expenses import ExpenseTracker, Expense

class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        self.user_id = "test_user"
        self.tracker = ExpenseTracker(self.user_id)
        self.data_file = f"expenses_{self.user_id}.json"
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def test_add_valid_expense(self):
        expense_id = self.tracker.add_expense(50.0, "Food", "Grocery shopping", tags=["essentials"])
        self.assertEqual(len(self.tracker.expenses), 1)
        expense = self.tracker.get_expense_by_id(expense_id)
        self.assertEqual(expense["amount"], 50.0)
        self.assertEqual(expense["category"], "Food")
        self.assertEqual(expense["tags"], ["essentials"])

    def test_add_recurring_expense(self):
        expense_id = self.tracker.add_expense(100.0, "Rent", "Monthly rent", is_recurring=True, recurrence_period="monthly")
        recurring = self.tracker.get_recurring_expenses()
        self.assertEqual(len(recurring), 1)
        self.assertEqual(recurring[0]["recurrence_period"], "monthly")

    def test_add_invalid_expense(self):
        with self.assertRaises(ValueError):
            self.tracker.add_expense(-10.0, "Food", "Invalid")
        with self.assertRaises(ValueError):
            self.tracker.add_expense(50.0, "", "No category")
        with self.assertRaises(ValueError):
            self.tracker.add_expense(50.0, "Food", "", is_recurring=True)

    def test_get_expenses_by_category(self):
        self.tracker.add_expense(50.0, "Food", "Lunch")
        self.tracker.add_expense(30.0, "Transport", "Bus")
        food_expenses = self.tracker.get_expenses_by_category("Food")
        self.assertEqual(len(food_expenses), 1)
        self.assertEqual(food_expenses[0]["amount"], 50.0)

    def test_get_expenses_by_tag(self):
        self.tracker.add_expense(50.0, "Food", "Lunch", tags=["meal", "daily"])
        self.tracker.add_expense(30.0, "Transport", "Bus", tags=["daily"])
        tagged_expenses = self.tracker.get_expenses_by_tag("daily")
        self.assertEqual(len(tagged_expenses), 2)

    def test_delete_expense(self):
        expense_id = self.tracker.add_expense(50.0, "Food", "Lunch")
        self.assertTrue(self.tracker.delete_expense(expense_id))
        self.assertIsNone(self.tracker.get_expense_by_id(expense_id))
        self.assertFalse(self.tracker.delete_expense("nonexistent"))

    def test_update_expense(self):
        expense_id = self.tracker.add_expense(50.0, "Food", "Lunch")
        self.assertTrue(self.tracker.update_expense(expense_id, amount=75.0, description="Dinner"))
        expense = self.tracker.get_expense_by_id(expense_id)
        self.assertEqual(expense["amount"], 75.0)
        self.assertEqual(expense["description"], "Dinner")
        self.assertFalse(self.tracker.update_expense("nonexistent"))

    def test_save_and_load(self):
        self.tracker.add_expense(50.0, "Food", "Lunch")
        self.tracker._save_to_file()
        new_tracker = ExpenseTracker(self.user_id)
        new_tracker.load_from_file()
        self.assertEqual(len(new_tracker.expenses), 1)