import pandas as pd
from datetime import datetime
from .models import get_db, Expense, Investment, FinancialGoal
from sqlalchemy.orm import Session
from sqlalchemy import func

class DataManager:
    def __init__(self):
        self.db = next(get_db())
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        # Only add demo data if tables are empty
        if self.db.query(Expense).count() == 0:
            # Add sample expenses
            sample_expenses = [
                Expense(
                    date=datetime(2023, 1, 1),
                    category='Food',
                    amount=50.0,
                    description='Groceries'
                ),
                Expense(
                    date=datetime(2023, 1, 2),
                    category='Transport',
                    amount=30.0,
                    description='Bus fare'
                )
            ]
            self.db.add_all(sample_expenses)

        if self.db.query(Investment).count() == 0:
            # Add sample investments
            sample_investments = [
                Investment(
                    asset='Stocks',
                    current_value=10000.0,
                    initial_value=9000.0
                ),
                Investment(
                    asset='Bonds',
                    current_value=5000.0,
                    initial_value=5100.0
                )
            ]
            self.db.add_all(sample_investments)

        if self.db.query(FinancialGoal).count() == 0:
            # Add sample goals
            sample_goals = [
                FinancialGoal(
                    name='Emergency Fund',
                    target=10000.0,
                    current=7500.0,
                    deadline=datetime(2024, 12, 31)
                ),
                FinancialGoal(
                    name='House Down Payment',
                    target=50000.0,
                    current=15000.0,
                    deadline=datetime(2025, 12, 31)
                )
            ]
            self.db.add_all(sample_goals)

        self.db.commit()

    def add_expense(self, date, category, amount, description):
        expense = Expense(
            date=date,
            category=category,
            amount=amount,
            description=description
        )
        self.db.add(expense)
        self.db.commit()
        return expense

    def get_expenses(self):
        expenses = self.db.query(Expense).all()
        return pd.DataFrame([{
            'date': e.date,
            'category': e.category,
            'amount': e.amount,
            'description': e.description
        } for e in expenses])

    def get_total_expenses(self):
        return self.db.query(func.sum(Expense.amount)).scalar() or 0.0

    def get_expenses_by_category(self):
        result = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label('amount')
        ).group_by(Expense.category).all()

        return pd.Series(
            {r.category: r.amount for r in result}
        )

    def get_investments(self):
        investments = self.db.query(Investment).all()
        return pd.DataFrame([{
            'asset': i.asset,
            'current_value': i.current_value,
            'initial_value': i.initial_value,
            'return': ((i.current_value - i.initial_value) / i.initial_value) * 100
        } for i in investments])

    def get_portfolio_value(self):
        return self.db.query(func.sum(Investment.current_value)).scalar() or 0.0

    def get_portfolio_return(self):
        investments = self.get_investments()
        if len(investments) == 0:
            return 0.0
        total_current = investments['current_value'].sum()
        total_initial = investments['initial_value'].sum()
        return ((total_current - total_initial) / total_initial) * 100

    def get_goals(self):
        goals = self.db.query(FinancialGoal).all()
        return pd.DataFrame([{
            'name': g.name,
            'target': g.target,
            'current': g.current,
            'deadline': g.deadline
        } for g in goals])

    def add_goal(self, name, target, current, deadline):
        goal = FinancialGoal(
            name=name,
            target=target,
            current=current,
            deadline=deadline
        )
        self.db.add(goal)
        self.db.commit()
        return goal