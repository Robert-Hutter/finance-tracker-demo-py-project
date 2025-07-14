from typing import List, Dict, Optional
from finance_tracker.expenses import ExpenseTracker
from finance_tracker.budgets import BudgetManager
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

class FinancialReport:
    """Generates financial reports for a user."""
    def __init__(self, user_id: str, expense_tracker: ExpenseTracker, budget_manager: BudgetManager):
        self.user_id = user_id
        self.expense_tracker = expense_tracker
        self.budget_manager = budget_manager
        self.report_dir = f"reports_{user_id}"
        os.makedirs(self.report_dir, exist_ok=True)

    def generate_category_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """Generate a summary of expenses by category."""
        expenses = self.expense_tracker.expenses
        if start_date and end_date:
            expenses = [exp for exp in expenses if start_date <= exp.date <= end_date]
        
        categories = {}
        for exp in expenses:
            cat = exp.category
            categories[cat] = categories.get(cat, 0.0) + exp.amount
        
        return {
            "user_id": self.user_id,
            "period": f"{start_date or 'all'} to {end_date or 'all'}",
            "category_totals": categories,
            "total": sum(categories.values())
        }

    def generate_budget_comparison(self, period: str = "monthly") -> List[Dict]:
        """Compare spending against budgets."""
        budgets = self.budget_manager.get_all_budgets()
        comparison = []
        for budget in budgets:
            if budget["period"] == period:
                status = self.budget_manager.get_budget_status(budget["category"], period)
                comparison.append(status)
        return comparison

    def generate_trend_analysis(self, months: int = 6) -> Dict:
        """Analyze spending trends over the specified number of months."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")
        
        expenses = self.expense_tracker.expenses
        expenses = [exp for exp in expenses if start_date_str <= exp.date <= end_date_str]
        
        monthly_data = {}
        current_date = start_date
        while current_date <= end_date:
            month_key = current_date.strftime("%Y-%m")
            monthly_data[month_key] = 0.0
            current_date += timedelta(days=30)
        
        for exp in expenses:
            month_key = exp.date[:7]  # YYYY-MM
            monthly_data[month_key] = monthly_data.get(month_key, 0.0) + exp.amount
        
        return {
            "user_id": self.user_id,
            "period": f"{months} months",
            "monthly_totals": monthly_data
        }

    def generate_report_pdf(self, report_type: str, start_date: str = None, end_date: str = None) -> str:
        """Generate a PDF report (placeholder for LaTeX generation)."""
        # Note: Actual PDF generation requires LaTeX, implemented as placeholder
        report_file = f"{self.report_dir}/{report_type}_{start_date or 'all'}_{end_date or 'all'}.txt"
        with open(report_file, 'w') as f:
            if report_type == "category_summary":
                report_data = self.generate_category_summary(start_date, end_date)
                f.write(json.dumps(report_data, indent=2))
            elif report_type == "budget_comparison":
                report_data = self.generate_budget_comparison()
                f.write(json.dumps(report_data, indent=2))
            elif report_type == "trend_analysis":
                report_data = self.generate_trend_analysis()
                f.write(json.dumps(report_data, indent=2))
        return report_file

    def plot_category_distribution(self, start_date: str = None, end_date: str = None) -> str:
        """Generate a pie chart of category distribution."""
        summary = self.generate_category_summary(start_date, end_date)
        categories = summary["category_totals"]
        labels = list(categories.keys())
        values = list(categories.values())
        
        plt.figure(figsize=(8, 8))
        plt.pie(values, labels=labels, autopct='%1.1f%%')
        plt.title(f"Expense Distribution for {self.user_id}")
        plot_file = f"{self.report_dir}/category_distribution.png"
        plt.savefig(plot_file)
        plt.close()
        return plot_file