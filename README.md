# Personal Finance Tracker

An enhanced Python-based personal finance tracker with user authentication, expense tracking, budget management, reporting, and a CLI.

## Installation

```bash
pip install .
```

## Usage
```python
from finance_tracker.users import UserManager
from finance_tracker.expenses import ExpenseTracker
from finance_tracker.budgets import BudgetManager
from finance_tracker.reports import FinancialReport

# Register and authenticate user
user_manager = UserManager()
user_manager.register_user("testuser", "password123", "test@example.com")

# Track expenses
tracker = ExpenseTracker("testuser")
tracker.add_expense(50.0, "Food", "Grocery shopping", tags=["essentials"])

# Manage budgets
budget_manager = BudgetManager("testuser")
budget_manager.set_budget("Food", 200.0, "monthly", alert_threshold=0.9)

# Generate reports
report_generator = FinancialReport("testuser", tracker, budget_manager)
summary = report_generator.generate_category_summary()
```

## CLI Usage
```bash
python -m finance_tracker.cli
```

Commands:
- `register <username> <password> <email>`
- `login <username> <password>`
- `add_expense <amount> <category> <description> [tags] [recurring] [period]`
- `set_budget <category> <amount> [period] [alert_threshold]`
- `generate_report <type> [start_date] [end_date]`
- `exit`

## Running Tests
```bash
python -m unittest discover finance_tracker/tests
```

## Project Structure
- `expenses.py`: Expense tracking with tags and recurring expenses
- `budgets.py`: Budget management with period-based tracking and alerts
- `users.py`: User authentication and profile management
- `reports.py`: Financial reporting and visualization
- `cli.py`: Command-line interface for user interaction
- `tests/`: Comprehensive test suite