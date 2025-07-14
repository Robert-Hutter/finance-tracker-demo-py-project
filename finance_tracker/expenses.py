from datetime import datetime
from typing import List, Dict, Optional
import json
import os
from uuid import uuid4

class Expense:
    """Represents a single expense entry."""
    def __init__(self, amount: float, category: str, description: str, date: str = None, 
                 tags: List[str] = None, is_recurring: bool = False, recurrence_period: str = None):
        self.id = str(uuid4())
        self.amount = float(amount)
        self.category = category.strip()
        self.description = description.strip()
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.tags = tags or []
        self.is_recurring = is_recurring
        self.recurrence_period = recurrence_period  # e.g., 'monthly', 'weekly'

    def to_dict(self) -> Dict:
        """Convert expense to dictionary for serialization."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
            "tags": self.tags,
            "is_recurring": self.is_recurring,
            "recurrence_period": self.recurrence_period
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Expense':
        """Create expense from dictionary."""
        return cls(
            amount=data["amount"],
            category=data["category"],
            description=data["description"],
            date=data["date"],
            tags=data.get("tags", []),
            is_recurring=data.get("is_recurring", False),
            recurrence_period=data.get("recurrence_period", None)
        )

class ExpenseTracker:
    """Manages expense tracking for a user."""
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.expenses: List[Expense] = []
        self.data_file = f"expenses_{user_id}.json"

    def add_expense(self, amount: float, category: str, description: str, 
                    date: str = None, tags: List[str] = None, 
                    is_recurring: bool = False, recurrence_period: str = None) -> str:
        """Add a new expense and return its ID."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if not category or not description:
            raise ValueError("Category and description cannot be empty")
        if is_recurring and not recurrence_period:
            raise ValueError("Recurring expenses must specify a period")
        expense = Expense(amount, category, description, date, tags, is_recurring, recurrence_period)
        self.expenses.append(expense)
        self._save_to_file()
        return expense.id

    def get_expense_by_id(self, expense_id: str) -> Optional[Dict]:
        """Retrieve an expense by its ID."""
        for expense in self.expenses:
            if expense.id == expense_id:
                return expense.to_dict()
        return None

    def get_expenses_by_category(self, category: str) -> List[Dict]:
        """Retrieve expenses for a specific category."""
        return [exp.to_dict() for exp in self.expenses if exp.category.lower() == category.lower()]

    def get_expenses_by_tag(self, tag: str) -> List[Dict]:
        """Retrieve expenses with a specific tag."""
        return [exp.to_dict() for exp in self.expenses if tag.lower() in [t.lower() for t in exp.tags]]

    def get_total_expenses(self, start_date: str = None, end_date: str = None) -> float:
        """Calculate total expenses, optionally within a date range."""
        total = 0.0
        for expense in self.expenses:
            if start_date and end_date:
                if start_date <= expense.date <= end_date:
                    total += expense.amount
            else:
                total += expense.amount
        return total

    def get_recurring_expenses(self) -> List[Dict]:
        """Retrieve all recurring expenses."""
        return [exp.to_dict() for exp in self.expenses if exp.is_recurring]

    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense by ID."""
        initial_len = len(self.expenses)
        self.expenses = [exp for exp in self.expenses if exp.id != expense_id]
        if len(self.expenses) < initial_len:
            self._save_to_file()
            return True
        return False

    def update_expense(self, expense_id: str, amount: float = None, category: str = None,
                      description: str = None, tags: List[str] = None) -> bool:
        """Update an existing expense."""
        for expense in self.expenses:
            if expense.id == expense_id:
                if amount is not None:
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                    expense.amount = float(amount)
                if category is not None:
                    if not category:
                        raise ValueError("Category cannot be empty")
                    expense.category = category.strip()
                if description is not None:
                    if not description:
                        raise ValueError("Description cannot be empty")
                    expense.description = description.strip()
                if tags is not None:
                    expense.tags = tags
                self._save_to_file()
                return True
        return False

    def _save_to_file(self) -> None:
        """Save expenses to a JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump([exp.to_dict() for exp in self.expenses], f, indent=2)

    def load_from_file(self) -> None:
        """Load expenses from a JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.expenses = [Expense.from_dict(item) for item in data]
        except FileNotFoundError:
            self.expenses = []

    def __str__(self) -> str:
        """String representation of the expense tracker."""
        return f"ExpenseTracker for user {self.user_id} with {len(self.expenses)} expenses"