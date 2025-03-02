import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.charts import (
    create_expense_pie_chart,
    create_portfolio_pie_chart,
    create_goals_progress_chart,
    create_expense_trend_chart
)
import requests
import streamlit.components.v1 as components

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
            st.write("Connecting to Plaid service...")
            response = requests.post('http://0.0.0.0:5001/api/create_link_token')

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
                            console.log('Initializing Plaid Link...');
                            const handler = Plaid.create({{
                                token: '{link_token}',
                                onSuccess: function(public_token, metadata) {{
                                    console.log('Plaid Link success');
                                    document.getElementById('plaid-status').innerHTML = 'Connecting account...';

                                    fetch('http://0.0.0.0:5001/api/exchange_token', {{
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
                                            window.location.reload();
                                        }} else {{
                                            document.getElementById('plaid-status').innerHTML = 'Error: ' + (data.error || 'Unknown error');
                                            console.error('Error:', data);
                                        }}
                                    }})
                                    .catch(error => {{
                                        console.error('Error:', error);
                                        document.getElementById('plaid-status').innerHTML = 'Error connecting to server';
                                    }});
                                }},
                                onLoad: function() {{
                                    console.log('Plaid Link loaded');
                                    handler.open();
                                }},
                                onExit: function(err, metadata) {{
                                    console.log('Plaid Link exit:', err, metadata);
                                    if (err != null) {{
                                        document.getElementById('plaid-status').innerHTML = 'Error: ' + err.display_message;
                                    }}
                                }},
                                onEvent: function(eventName, metadata) {{
                                    console.log('Plaid event:', eventName, metadata);
                                }}
                            }});
                        }};
                    </script>
                </div>
                """
                components.html(plaid_html, height=600)
            else:
                st.error(f"Failed to get link token from server. Status code: {response.status_code}")
                st.write("Response:", response.text)
        except requests.exceptions.ConnectionError as e:
            st.error("Could not connect to the Flask server. Make sure it's running on port 5001.")
            st.write("Error details:", str(e))
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

# Overview Page (Example -  Needs to be implemented based on your requirements)
if page == "Overview":
    st.title("Overview")
    # Add your overview content here

# Expenses Page (Example -  Needs to be implemented based on your requirements)
if page == "Expenses":
    st.title("Expenses")
    # Add your expenses content here

# Investments Page (Example -  Needs to be implemented based on your requirements)
if page == "Investments":
    st.title("Investments")
    # Add your investments content here

# Goals Page (Example - Needs to be implemented based on your requirements)
if page == "Goals":
    st.title("Goals")
    # Add your goals content here

from flask import Flask, request, jsonify #This import remains here because it is used in server.py