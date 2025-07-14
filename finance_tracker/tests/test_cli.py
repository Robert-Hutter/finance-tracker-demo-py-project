import unittest
from io import StringIO
from contextlib import redirect_stdout
from finance_tracker.cli import FinanceTrackerCLI

class TestFinanceTrackerCLI(unittest.TestCase):
    def setUp(self):
        self.cli = FinanceTrackerCLI()

    def test_register_user(self):
        with redirect_stdout(StringIO()) as output:
            self.cli.do_register("testuser1 password123 test@example.com")
            self.assertIn("registered successfully", output.getvalue())

    def test_login(self):
        self.cli.do_register("testuser2 password123 test@example.com")
        with redirect_stdout(StringIO()) as output:
            self.cli.do_login("testuser2 password123")
            self.assertIn("Logged in as testuser2", output.getvalue())

    def test_add_expense(self):
        self.cli.do_register("testuser3 password123 test@example.com")
        self.cli.do_login("testuser3 password123")
        with redirect_stdout(StringIO()) as output:
            self.cli.do_add_expense("50.0 Food Lunch essentials true monthly")
            self.assertIn("Expense added with ID", output.getvalue())