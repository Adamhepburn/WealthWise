import pandas as pd
from datetime import datetime
from .models import get_db, Expense, Investment, FinancialGoal, PlaidAccount, Transaction
from .plaid_client import PlaidClient
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

class DataManager:
    def __init__(self):
        self.db = next(get_db())
        self.plaid_client = PlaidClient()
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

    # Plaid Integration Methods
    def create_link_token(self, user_id='user-1'):
        return self.plaid_client.create_link_token(user_id)

    def add_plaid_account(self, public_token, accounts_metadata):
        access_token = self.plaid_client.exchange_public_token(public_token)

        for account in accounts_metadata:
            plaid_account = PlaidAccount(
                plaid_account_id=account['id'],
                access_token=access_token,
                account_name=account.get('name'),
                account_type=account.get('type'),
                institution_name=account.get('institution_name')
            )
            self.db.add(plaid_account)

        self.db.commit()
        return True

    def sync_transactions(self):
        accounts = self.db.query(PlaidAccount).all()
        for account in accounts:
            transactions = self.plaid_client.get_transactions(account.access_token)

            for txn in transactions:
                existing = self.db.query(Transaction).filter_by(
                    plaid_transaction_id=txn.transaction_id
                ).first()

                if not existing:
                    transaction = Transaction(
                        plaid_transaction_id=txn.transaction_id,
                        account_id=account.id,
                        date=txn.date,
                        amount=txn.amount,
                        category=txn.category[0] if txn.category else None,
                        merchant_name=txn.merchant_name,
                        description=txn.name
                    )
                    self.db.add(transaction)

        self.db.commit()

    def get_linked_accounts(self):
        accounts = self.db.query(PlaidAccount).all()
        return pd.DataFrame([{
            'name': a.account_name,
            'type': a.account_type,
            'institution': a.institution_name,
            'last_sync': a.last_sync
        } for a in accounts])

    # Existing methods remain unchanged
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
        # Combine manual expenses and Plaid transactions
        manual_expenses = self.db.query(Expense).all()
        plaid_transactions = self.db.query(Transaction).all()

        all_expenses = []

        # Add manual expenses
        for e in manual_expenses:
            all_expenses.append({
                'date': e.date,
                'category': e.category,
                'amount': e.amount,
                'description': e.description,
                'source': 'manual'
            })

        # Add Plaid transactions
        for t in plaid_transactions:
            all_expenses.append({
                'date': t.date,
                'category': t.category or 'Uncategorized',
                'amount': t.amount,
                'description': t.description,
                'source': 'bank'
            })

        return pd.DataFrame(all_expenses)

    def get_total_expenses(self):
        manual_total = self.db.query(func.sum(Expense.amount)).scalar() or 0.0
        plaid_total = self.db.query(func.sum(Transaction.amount)).scalar() or 0.0
        return manual_total + plaid_total

    def get_expenses_by_category(self):
        # Combine manual and Plaid transaction categories
        manual_expenses = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label('amount')
        ).group_by(Expense.category).all()

        plaid_transactions = self.db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('amount')
        ).group_by(Transaction.category).all()

        # Combine results
        category_totals = {}
        for category, amount in manual_expenses:
            category_totals[category] = amount

        for category, amount in plaid_transactions:
            if category in category_totals:
                category_totals[category] += amount
            else:
                category_totals[category] = amount

        return pd.Series(category_totals)

    # Investment and Goals methods remain unchanged
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