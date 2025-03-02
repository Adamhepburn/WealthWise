import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.charts import (
    create_expense_pie_chart,
    create_portfolio_pie_chart,
    create_goals_progress_chart,
    create_expense_trend_chart
)
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="💰",
    layout="wide"
)

# Load custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Expenses", "Investments", "Goals"]
)

# Overview Page
if page == "Overview":
    st.title("Financial Overview")
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Expenses",
            f"${data_manager.get_total_expenses():,.2f}",
            "-12.5%"
        )
    
    with col2:
        portfolio_value = data_manager.get_portfolio_value()
        portfolio_return = data_manager.get_portfolio_return()
        st.metric(
            "Portfolio Value",
            f"${portfolio_value:,.2f}",
            f"{portfolio_return:.1f}%"
        )
    
    with col3:
        st.metric(
            "Net Worth",
            f"${portfolio_value - data_manager.get_total_expenses():,.2f}",
            "8.2%"
        )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        expenses_by_category = data_manager.get_expenses_by_category()
        st.plotly_chart(
            create_expense_pie_chart(expenses_by_category),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_portfolio_pie_chart(data_manager.investments),
            use_container_width=True
        )

# Expenses Page
elif page == "Expenses":
    st.title("Expense Tracking")

    # Expense input form
    with st.form("expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            amount = st.number_input("Amount", min_value=0.0)
        with col2:
            category = st.selectbox(
                "Category",
                ["Food", "Transport", "Shopping", "Entertainment", "Bills"]
            )
        with col3:
            date = st.date_input("Date")

        description = st.text_input("Description")
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            data_manager.add_expense(date, category, amount, description)
            st.success("Expense added successfully!")
            st.rerun()

    # Display expense trend
    st.plotly_chart(
        create_expense_trend_chart(data_manager.expenses),
        use_container_width=True
    )
    
    # Recent expenses table
    st.subheader("Recent Expenses")
    st.dataframe(
        data_manager.expenses.sort_values('date', ascending=False).head(10),
        use_container_width=True
    )

# Investments Page
elif page == "Investments":
    st.title("Investment Portfolio")
    
    # Portfolio summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total Portfolio Value",
            f"${data_manager.get_portfolio_value():,.2f}",
            f"{data_manager.get_portfolio_return():.1f}%"
        )
    
    with col2:
        st.plotly_chart(
            create_portfolio_pie_chart(data_manager.investments),
            use_container_width=True
        )
    
    # Investment details table
    st.subheader("Portfolio Details")
    st.dataframe(data_manager.investments, use_container_width=True)

# Goals Page
else:
    st.title("Financial Goals")

    # Goal input form
    with st.form("goal_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            goal_name = st.text_input("Goal Name")
        with col2:
            target_amount = st.number_input("Target Amount", min_value=0.0)
        with col3:
            deadline = st.date_input("Target Date")

        current_amount = st.number_input("Current Amount", min_value=0.0)
        submitted = st.form_submit_button("Add Goal")

        if submitted:
            data_manager.add_goal(goal_name, target_amount, current_amount, deadline)
            st.success("Goal added successfully!")
            st.rerun()

    # Goals progress chart
    st.plotly_chart(
        create_goals_progress_chart(data_manager.goals),
        use_container_width=True
    )
    
    # Goals table
    st.subheader("Current Goals")
    st.dataframe(data_manager.goals, use_container_width=True)