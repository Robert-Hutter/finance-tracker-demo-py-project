from typing import Dict, List
from datetime import datetime
import json
import os

class Budget:
    """Represents a budget for a category and period."""
    def __init__(self, category: str, amount: float, period: str, alert_threshold: float = 0.8):
        self.category = category.strip()
        self.amount = float(amount)
        self.period = period.lower()
        self.alert_threshold = alert_threshold  # Percentage of budget to trigger alert
        self.spending = 0.0

    def to_dict(self) -> Dict:
        """Convert budget to dictionary."""
        return {
            "category": self.category,
            "amount": self.amount,
            "period": self.period,
            "alert_threshold": self.alert_threshold,
            "spending": self.spending
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Budget':
        """Create budget from dictionary."""
        budget = cls(data["category"], data["amount"], data["period"], data["alert_threshold"])
        budget.spending = data["spending"]
        return budget

class BudgetManager:
    """Manages budgets for a user."""
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.budgets: Dict[str, Budget] = {}
        self.data_file = f"budgets_{user_id}.json"
        self._load_from_file()

    def set_budget(self, category: str, amount: float, period: str = "monthly",
                   alert_threshold: float = 0.8) -> None:
        """Set a budget for a category and period."""
        if amount <= 0:
            raise ValueError("Budget amount must be positive")
        if not category:
            raise ValueError("Category cannot be empty")
        if period not in ["daily", "weekly", "monthly", "yearly"]:
            raise ValueError("Invalid period. Choose: daily, weekly, monthly, yearly")
        if not 0 <= alert_threshold <= 1:
            raise ValueError("Alert threshold must be between 0 and 1")
        key = f"{category}_{period}"
        self.budgets[key] = Budget(category, amount, period, alert_threshold)
        self._save_to_file()

    def add_spending(self, category: str, amount: float, period: str = "monthly") -> None:
        """Add spending to a budget."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        key = f"{category}_{period}"
        if key not in self.budgets:
            raise ValueError(f"No budget set for {category} in {period} period")
        self.budgets[key].spending += float(amount)
        self._save_to_file()

    def get_budget_status(self, category: str, period: str = "monthly") -> Dict:
        """Get status of a budget."""
        key = f"{category}_{period}"
        budget = self.budgets.get(key)
        if not budget:
            return {"error": f"No budget for {category} in {period} period"}
        spent = budget.spending
        return {
            "category": budget.category,
            "period": budget.period,
            "budget": budget.amount,
            "spent": spent,
            "remaining": budget.amount - spent,
            "over_budget": spent > budget.amount,
            "alert_triggered": spent >= budget.amount * budget.alert_threshold
        }

    def get_all_budgets(self) -> List[Dict]:
        """Retrieve all budgets."""
        return [budget.to_dict() for budget in self.budgets.values()]

    def reset_budget(self, category: str, period: str = "monthly") -> bool:
        """Reset spending for a budget."""
        key = f"{category}_{period}"
        if key in self.budgets:
            self.budgets[key].spending = 0.0
            self._save_to_file()
            return True
        return False

    def update_budget(self, category: str, amount: float = None, period: str = "monthly",
                     alert_threshold: float = None) -> bool:
        """Update budget amount or alert threshold."""
        key = f"{category}_{period}"
        if key not in self.budgets:
            return False
        if amount is not None:
            if amount <= 0:
                raise ValueError("Budget amount must be positive")
            self.budgets[key].amount = float(amount)
        if alert_threshold is not None:
            if not 0 <= alert_threshold <= 1:
                raise ValueError("Alert threshold must be between 0 and 1")
            self.budgets[key].alert_threshold = alert_threshold
        self._save_to_file()
        return True

    def _save_to_file(self) -> None:
        """Save budgets to a JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump([budget.to_dict() for budget in self.budgets.values()], f, indent=2)

    def _load_from_file(self) -> None:
        """Load budgets from a JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.budgets = {f"{item['category']}_{item['period']}": Budget.from_dict(item) 
                               for item in data}
        except FileNotFoundError:
            self.budgets = {}