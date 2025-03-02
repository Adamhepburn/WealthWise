import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataManager:
    def __init__(self):
        # Initialize with mock data
        self.expenses = self._generate_mock_expenses()
        self.investments = self._generate_mock_investments()
        self.goals = self._generate_mock_goals()

    def _generate_mock_expenses(self):
        categories = ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills']
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        
        data = []
        for _ in range(100):
            date = np.random.choice(dates)
            data.append({
                'date': date,
                'category': np.random.choice(categories),
                'amount': round(np.random.uniform(10, 500), 2),
                'description': f'Sample expense {_}'
            })
        
        return pd.DataFrame(data)

    def _generate_mock_investments(self):
        assets = ['Stocks', 'Bonds', 'Real Estate', 'Crypto']
        data = []
        
        for asset in assets:
            current_value = np.random.uniform(5000, 50000)
            initial_value = current_value * (1 - np.random.uniform(-0.3, 0.3))
            data.append({
                'asset': asset,
                'current_value': round(current_value, 2),
                'initial_value': round(initial_value, 2),
                'return': round(((current_value - initial_value) / initial_value) * 100, 2)
            })
        
        return pd.DataFrame(data)

    def _generate_mock_goals(self):
        goals = [
            {'name': 'Emergency Fund', 'target': 10000, 'current': 7500, 'deadline': '2024-06-30'},
            {'name': 'House Down Payment', 'target': 50000, 'current': 15000, 'deadline': '2025-12-31'},
            {'name': 'Vacation Fund', 'target': 5000, 'current': 2500, 'deadline': '2024-03-31'}
        ]
        return pd.DataFrame(goals)

    def get_total_expenses(self):
        return self.expenses['amount'].sum()

    def get_expenses_by_category(self):
        return self.expenses.groupby('category')['amount'].sum()

    def get_portfolio_value(self):
        return self.investments['current_value'].sum()

    def get_portfolio_return(self):
        total_current = self.investments['current_value'].sum()
        total_initial = self.investments['initial_value'].sum()
        return ((total_current - total_initial) / total_initial) * 100

    def get_asset_allocation(self):
        return (self.investments['current_value'] / self.investments['current_value'].sum()) * 100
