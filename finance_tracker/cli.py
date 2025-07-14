import cmd
import argparse
from finance_tracker.expenses import ExpenseTracker
from finance_tracker.budgets import BudgetManager
from finance_tracker.users import UserManager
from finance_tracker.reports import FinancialReport
from datetime import datetime

class FinanceTrackerCLI(cmd.Cmd):
    """Command-line interface for the finance tracker."""
    prompt = "FinanceTracker> "
    intro = "Welcome to the Personal Finance Tracker. Type 'help' for commands."

    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.current_user = None
        self.expense_tracker = None
        self.budget_manager = None
        self.report_generator = None

    def do_login(self, arg):
        """Login to the system: login <username> <password>"""
        args = arg.split()
        if len(args) != 2:
            print("Usage: login <username> <password>")
            return
        username, password = args
        if self.user_manager.authenticate_user(username, password):
            self.current_user = username
            self.expense_tracker = ExpenseTracker(username)
            self.budget_manager = BudgetManager(username)
            self.report_generator = FinancialReport(username, self.expense_tracker, self.budget_manager)
            print(f"Logged in as {username}")
        else:
            print("Invalid username or password")

    def do_register(self, arg):
        """Register a new user: register <username> <password> <email>"""
        args = arg.split()
        if len(args) != 3:
            print("Usage: register <username> <password> <email>")
            return
        try:
            self.user_manager.register_user(*args)
            print(f"User {args[0]} registered successfully")
        except ValueError as e:
            print(f"Error: {e}")

    def do_add_expense(self, arg):
        """Add an expense: add_expense <amount> <category> <description> [tags] [recurring] [period]"""
        if not self.current_user:
            print("Please login first")
            return
        args = arg.split()
        if len(args) < 3:
            print("Usage: add_expense <amount> <category> <description> [tags] [recurring] [period]")
            return
        amount, category, description = args[:3]
        tags = args[3].split(",") if len(args) > 3 else []
        is_recurring = args[4].lower() == "true" if len(args) > 4 else False
        period = args[5] if len(args) > 5 else None
        try:
            expense_id = self.expense_tracker.add_expense(float(amount), category, description, 
                                                         tags=tags, is_recurring=is_recurring, 
                                                         recurrence_period=period)
            print(f"Expense added with ID: {expense_id}")
        except ValueError as e:
            print(f"Error: {e}")

    def do_set_budget(self, arg):
        """Set a budget: set_budget <category> <amount> [period] [alert_threshold]"""
        if not self.current_user:
            print("Please login first")
            return
        args = arg.split()
        if len(args) < 2:
            print("Usage: set_budget <category> <amount> [period] [alert_threshold]")
            return
        category, amount = args[:2]
        period = args[2] if len(args) > 2 else "monthly"
        alert_threshold = float(args[3]) if len(args) > 3 else 0.8
        try:
            self.budget_manager.set_budget(category, float(amount), period, alert_threshold)
            print(f"Budget set for {category} ({period})")
        except ValueError as e:
            print(f"Error: {e}")

    def do_generate_report(self, arg):
        """Generate a report: generate_report <type> [start_date] [end_date]"""
        if not self.current_user:
            print("Please login first")
            return
        args = arg.split()
        if len(args) < 1:
            print("Usage: generate_report <type> [start_date] [end_date]")
            return
        report_type = args[0]
        start_date = args[1] if len(args) > 1 else None
        end_date = args[2] if len(args) > 2 else None
        try:
            report_file = self.report_generator.generate_report_pdf(report_type, start_date, end_date)
            print(f"Report generated: {report_file}")
        except Exception as e:
            print(f"Error: {e}")

    def do_exit(self, arg):
        """Exit the CLI."""
        print("Goodbye!")
        return True

    def preloop(self):
        """Initialize CLI state."""
        print("Personal Finance Tracker CLI. Type 'register' or 'login' to begin.")