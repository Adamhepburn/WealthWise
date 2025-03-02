import plotly.express as px
import plotly.graph_objects as go

def create_expense_pie_chart(expenses_by_category):
    fig = px.pie(
        values=expenses_by_category.values,
        names=expenses_by_category.index,
        title='Expenses by Category',
        color_discrete_sequence=['#00B386', '#FF6B6B', '#4299E1', '#38A169', '#2D3748']
    )
    return fig

def create_portfolio_pie_chart(investments):
    fig = px.pie(
        investments,
        values='current_value',
        names='asset',
        title='Portfolio Allocation',
        color_discrete_sequence=['#00B386', '#FF6B6B', '#4299E1', '#38A169']
    )
    return fig

def create_goals_progress_chart(goals):
    fig = go.Figure()
    
    for _, goal in goals.iterrows():
        progress = (goal['current'] / goal['target']) * 100
        fig.add_trace(go.Bar(
            x=[goal['name']],
            y=[progress],
            name=goal['name'],
            marker_color='#00B386'
        ))
        
    fig.update_layout(
        title='Financial Goals Progress',
        yaxis_title='Progress (%)',
        yaxis_range=[0, 100],
        showlegend=False
    )
    
    return fig

def create_expense_trend_chart(expenses):
    daily_expenses = expenses.groupby('date')['amount'].sum().reset_index()
    fig = px.line(
        daily_expenses,
        x='date',
        y='amount',
        title='Daily Expenses Trend',
        line_shape='spline'
    )
    fig.update_traces(line_color='#00B386')
    return fig
