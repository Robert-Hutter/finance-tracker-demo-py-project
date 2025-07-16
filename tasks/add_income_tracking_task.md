# Add Income Tracking Feature to Personal Finance Tracker

## Objective
Enhance the `finance_tracker` project by adding income tracking functionality to complement the existing expense, budget, user, and reporting features. The feature allows users to record income sources, track income by category and date, calculate net balance, and integrate with reporting and CLI.

## Requirements

1. **Create a new `IncomeTracker` class** in a new file `finance_tracker/income.py` with:
   - Record income with amount, category, description, date, tags, and optional recurrence (e.g., `add_income(amount, category, description, date=None, tags=None, is_recurring=False, recurrence_period=None) -> str`)
   - Retrieve income by ID (`get_income_by_id(income_id: str) -> Optional[Dict]`)
   - Retrieve income by category (`get_incomes_by_category(category: str) -> List[Dict]`)
   - Retrieve income by tag (`get_incomes_by_tag(tag: str) -> List[Dict]`)
   - Retrieve recurring incomes (`get_recurring_incomes() -> List[Dict]`)
   - Calculate total income for a date range (`get_total_income(start_date: str = None, end_date: str = None) -> float`)
   - Save and load income data to/from `income_<user_id>.json`
   - Delete income by ID (`delete_income(income_id: str) -> bool`)
   - Update income fields (`update_income(income_id: str, amount: float = None, category: str = None, description: str = None, tags: List[str] = None) -> bool`)
   - Input validation for positive amounts, non-empty fields, and valid recurrence periods

2. **Update `ExpenseTracker`** in `finance_tracker/expenses.py` to add:
   - `get_net_balance(income_tracker: IncomeTracker, start_date: str = None, end_date: str = None) -> float` to calculate total income minus total expenses

3. **Update `FinancialReport`** in `finance_tracker/reports.py` to include:
   - `generate_income_summary(start_date: str = None, end_date: str = None) -> Dict` for income by category
   - Update `generate_budget_comparison` to include net balance
   - Update `generate_trend_analysis` to include monthly net balance
   - Update `generate_report_pdf` to support "income_summary" report type

4. **Update `FinanceTrackerCLI`** in `finance_tracker/cli.py` to add:
   - Command `add_income <amount> <category> <description> [tags] [recurring] [period]`
   - Command `generate_income_report [start_date] [end_date]`
   - Initialize `IncomeTracker` in `__init__` and inject into `FinancialReport`

5. **Update README.md** to include:
   - Usage instructions for `IncomeTracker`
   - CLI commands for income tracking
   - Example of generating income reports

## Notes
- Model `IncomeTracker` after `ExpenseTracker`, with an `Income` class similar to `Expense`.
- Use JSON for persistence, storing data in `income_<user_id>.json`.
- Ensure compatibility with existing user authentication (user_id-based data storage).
- Handle edge cases (e.g., no income, invalid dates, empty tags).
- Test cases are provided in `finance_tracker/tests/test_income.py` and should not be modified.
