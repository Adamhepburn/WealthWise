import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.charts import (
    create_expense_pie_chart,
    create_portfolio_pie_chart,
    create_goals_progress_chart,
    create_expense_trend_chart
)
import streamlit.components.v1 as components
import requests

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
page = st.sidebar.radio("Go to", ["Overview", "Bank Accounts", "Expenses", "Investments", "Goals"], key="nav")

# Bank Accounts Page
if page == "Bank Accounts":
    st.title("Connected Bank Accounts")

    # Link new account section
    if st.button("+ Link New Account", key="link_account"):
        try:
            # Get link token from Flask backend
            response = requests.post('http://localhost:5001/api/create_link_token')
            if response.status_code == 200:
                link_token = response.json()['link_token']
                st.session_state['link_token'] = link_token
                st.write("Debug: Link token created successfully")

                # Create Plaid Link HTML
                plaid_html = f"""
                <div>
                    <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
                    <div id="plaid-status">Initializing Plaid...</div>
                    <script type="text/javascript">
                        window.onload = function() {{
                            const handler = Plaid.create({{
                                token: '{link_token}',
                                onSuccess: function(public_token, metadata) {{
                                    document.getElementById('plaid-status').innerHTML = 'Connecting account...';
                                    // Send public token to Flask backend
                                    fetch('http://localhost:5001/api/exchange_token', {{
                                        method: 'POST',
                                        headers: {{ 'Content-Type': 'application/json' }},
                                        body: JSON.stringify({{
                                            public_token: public_token,
                                            accounts: metadata.accounts
                                        }})
                                    }})
                                    .then(response => response.json())
                                    .then(data => {{
                                        if (data.success) {{
                                            document.getElementById('plaid-status').innerHTML = 'Account connected successfully!';
                                            // Reload the page to show new accounts
                                            window.location.reload();
                                        }} else {{
                                            document.getElementById('plaid-status').innerHTML = 'Error: ' + data.error;
                                        }}
                                    }});
                                }},
                                onLoad: function() {{
                                    handler.open();
                                }},
                                onExit: function(err, metadata) {{
                                    if (err != null) {{
                                        document.getElementById('plaid-status').innerHTML = 'Error: ' + err.display_message;
                                    }}
                                }},
                                onEvent: function(eventName, metadata) {{
                                    console.log('Event:', eventName);
                                }}
                            }});
                        }};
                    </script>
                </div>
                """
                components.html(plaid_html, height=600)
            else:
                st.error("Failed to get link token from server")
        except Exception as e:
            st.error("Failed to initialize Plaid")
            st.write("Error details:", str(e))

    # Display linked accounts
    accounts = data_manager.get_linked_accounts()
    if not accounts.empty:
        st.subheader("Connected Accounts")
        st.dataframe(accounts, use_container_width=True)

        if st.button("Sync Transactions", key="sync"):
            with st.spinner("Syncing transactions..."):
                data_manager.sync_transactions()
            st.success("Transactions synced successfully!")
    else:
        st.info("No bank accounts connected yet. Click 'Link New Account' to get started!")

# Overview Page
elif page == "Overview":
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
        investments = data_manager.get_investments()
        st.plotly_chart(
            create_portfolio_pie_chart(investments),
            use_container_width=True
        )

# Expenses Page
elif page == "Expenses":
    st.title("Expense Tracking")

    # Expense input form
    with st.form("expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            amount = st.number_input("Amount", min_value=0.0, key="amount")
        with col2:
            category = st.selectbox(
                "Category",
                ["Food", "Transport", "Shopping", "Entertainment", "Bills"],
                key="category"
            )
        with col3:
            date = st.date_input("Date", key="date")

        description = st.text_input("Description", key="description")
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            data_manager.add_expense(date, category, amount, description)
            st.success("Expense added successfully!")
            st.rerun()

    # Display expense trend
    expenses = data_manager.get_expenses()
    st.plotly_chart(
        create_expense_trend_chart(expenses),
        use_container_width=True
    )

    # Recent expenses table
    st.subheader("Recent Expenses")
    st.dataframe(
        expenses.sort_values('date', ascending=False).head(10),
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
        investments = data_manager.get_investments()
        st.plotly_chart(
            create_portfolio_pie_chart(investments),
            use_container_width=True
        )

    # Investment details table
    st.subheader("Portfolio Details")
    st.dataframe(investments, use_container_width=True)

# Goals Page
else:
    st.title("Financial Goals")

    # Goal input form
    with st.form("goal_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            goal_name = st.text_input("Goal Name", key="goal_name")
        with col2:
            target_amount = st.number_input("Target Amount", min_value=0.0, key="target")
        with col3:
            deadline = st.date_input("Target Date", key="deadline")

        current_amount = st.number_input("Current Amount", min_value=0.0, key="current")
        submitted = st.form_submit_button("Add Goal")

        if submitted:
            data_manager.add_goal(goal_name, target_amount, current_amount, deadline)
            st.success("Goal added successfully!")
            st.rerun()

    # Goals progress chart
    goals = data_manager.get_goals()
    st.plotly_chart(
        create_goals_progress_chart(goals),
        use_container_width=True
    )

    # Goals table
    st.subheader("Current Goals")
    st.dataframe(goals, use_container_width=True)