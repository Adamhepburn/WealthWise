import pandas as pd
from datetime import datetime
from .models import get_db, Expense, Investment, FinancialGoal, PlaidAccount, Transaction
from .plaid_client import PlaidClient
from sqlalchemy import func
import os

class DataManager:
    def __init__(self):
        self.plaid_client = PlaidClient()

    # Plaid Integration Methods
    def create_link_token(self, user_id='user-1'):
        return self.plaid_client.create_link_token(user_id)

    def add_plaid_account(self, public_token, accounts_metadata):
        access_token = self.plaid_client.exchange_public_token(public_token)

        with get_db() as db:
            for account in accounts_metadata:
                plaid_account = PlaidAccount(
                    plaid_account_id=account['id'],
                    access_token=access_token,
                    account_name=account.get('name'),
                    account_type=account.get('type'),
                    institution_name=account.get('institution_name')
                )
                db.add(plaid_account)

        return True

    def sync_transactions(self):
        with get_db() as db:
            accounts = db.query(PlaidAccount).all()
            for account in accounts:
                transactions = self.plaid_client.get_transactions(account.access_token)

                for txn in transactions:
                    existing = db.query(Transaction).filter_by(
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
                        db.add(transaction)

    def get_linked_accounts(self):
        with get_db() as db:
            accounts = db.query(PlaidAccount).all()
            return pd.DataFrame([{
                'name': a.account_name,
                'type': a.account_type,
                'institution': a.institution_name,
                'last_sync': a.last_sync
            } for a in accounts])

    # Expense Methods
    def add_expense(self, date, category, amount, description):
        with get_db() as db:
            expense = Expense(
                date=date,
                category=category,
                amount=amount,
                description=description
            )
            db.add(expense)
            return expense

    def get_expenses(self):
        with get_db() as db:
            # Combine manual expenses and Plaid transactions
            manual_expenses = db.query(Expense).all()
            plaid_transactions = db.query(Transaction).all()

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
        with get_db() as db:
            manual_total = db.query(func.sum(Expense.amount)).scalar() or 0.0
            plaid_total = db.query(func.sum(Transaction.amount)).scalar() or 0.0
            return manual_total + plaid_total

    def get_expenses_by_category(self):
        with get_db() as db:
            # Combine manual and Plaid transaction categories
            manual_expenses = db.query(
                Expense.category,
                func.sum(Expense.amount).label('amount')
            ).group_by(Expense.category).all()

            plaid_transactions = db.query(
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

    # Investment Methods
    def get_investments(self):
        with get_db() as db:
            investments = db.query(Investment).all()
            return pd.DataFrame([{
                'asset': i.asset,
                'current_value': i.current_value,
                'initial_value': i.initial_value,
                'return': ((i.current_value - i.initial_value) / i.initial_value) * 100
            } for i in investments])

    def get_portfolio_value(self):
        with get_db() as db:
            return db.query(func.sum(Investment.current_value)).scalar() or 0.0

    def get_portfolio_return(self):
        investments = self.get_investments()
        if len(investments) == 0:
            return 0.0
        total_current = investments['current_value'].sum()
        total_initial = investments['initial_value'].sum()
        return ((total_current - total_initial) / total_initial) * 100

    # Financial Goals Methods
    def get_goals(self):
        with get_db() as db:
            goals = db.query(FinancialGoal).all()
            return pd.DataFrame([{
                'name': g.name,
                'target': g.target,
                'current': g.current,
                'deadline': g.deadline
            } for g in goals])

    def add_goal(self, name, target, current, deadline):
        with get_db() as db:
            goal = FinancialGoal(
                name=name,
                target=target,
                current=current,
                deadline=deadline
            )
            db.add(goal)
            return goal