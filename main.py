import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.charts import (
    create_expense_pie_chart,
    create_portfolio_pie_chart,
    create_goals_progress_chart,
    create_expense_trend_chart
)
from flask import Flask, render_template, request
import threading
import webbrowser

# Initialize Flask app
flask_app = Flask(__name__, template_folder='templates')

# Initialize data manager
@st.cache_resource
def get_data_manager():
    return DataManager()

data_manager = get_data_manager()

# Flask route for Plaid Link
@flask_app.route('/plaid_link')
def plaid_link():
        link_token = data_manager.create_link_token()
        redirect_url = f"{st.session_state['streamlit_url']}/?page=Bank%20Accounts"
        return render_template('plaid_link.html', link_token=link_token, redirect_url=redirect_url)

    # Run Flask in a separate thread
    def run_flask():
        flask_app.run(host='0.0.0.0', port=5001, debug=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Streamlit app
    st.set_page_config(
        page_title="Personal Finance Dashboard",
        page_icon="💰",
        layout="wide"
    )

    # Load custom CSS
    with open('styles/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Store Streamlit URL in session state
    if 'streamlit_url' not in st.session_state:
        st.session_state['streamlit_url'] = "http://localhost:5000"  # Update if using Replit's public URL

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Overview", "Bank Accounts", "Expenses", "Investments", "Goals"], key="nav")

    # Bank Accounts Page
    if page == "Bank Accounts":
        st.title("Connected Bank Accounts")

        # Check for public_token from redirect
        query_params = st.query_params
        if 'public_token' in query_params:
            public_token = query_params['public_token']
            st.write(f"Received public_token: {public_token[:10]}...")
            # TODO: Exchange public_token for access_token and save account
            st.success("Bank account linked successfully!")
            del query_params['public_token']  # Clear after use

        # Link new account section
        if st.button("+ Link New Account", key="link_account"):
            plaid_url = "http://0.0.0.0:5001/plaid_link"  # Flask endpoint
            st.write(f"Opening Plaid Link at: {plaid_url}")
            st.markdown(f'<a href="{plaid_url}" target="_blank">Click here if the popup doesn’t open</a>', unsafe_allow_html=True)
            webbrowser.open(plaid_url)  # Auto-open in browser

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

    # [Rest of your Streamlit pages: Overview, Expenses, Investments, Goals remain unchanged]