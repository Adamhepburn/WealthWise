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
                st.write("Debug: Link token created:", link_token[:10] + "...")

                # Create Plaid Link HTML with improved script loading
                plaid_html = f"""
                <!DOCTYPE html>
                <html>
                <body>
                    <div id="plaid-status">Loading Plaid...</div>
                    <script
                        src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"
                        onload="initializePlaid()"
                        onerror="handleScriptError()">
                    </script>
                    <script type="text/javascript">
                        function handleScriptError() {{
                            document.getElementById('plaid-status').innerHTML = 'Failed to load Plaid script';
                            console.error('Failed to load Plaid script');
                        }}

                        function initializePlaid() {{
                            try {{
                                document.getElementById('plaid-status').innerHTML = 'Initializing Plaid...';
                                console.log('Initializing Plaid with token:', '{link_token[:10]}...');

                                const plaidConfig = {{
                                    token: '{link_token}',
                                    onSuccess: handleSuccess,
                                    onLoad: handleLoad,
                                    onExit: handleExit,
                                    onEvent: handleEvent
                                }};

                                const handler = Plaid.create(plaidConfig);
                                handler.open();
                            }} catch (error) {{
                                console.error('Plaid initialization error:', error);
                                document.getElementById('plaid-status').innerHTML = 'Failed to initialize Plaid: ' + error.message;
                            }}
                        }}

                        function handleSuccess(public_token, metadata) {{
                            console.log('Success - got public token');
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
                                console.log('Exchange response:', data);
                                if (data.success) {{
                                    document.getElementById('plaid-status').innerHTML = 'Account connected!';
                                    window.location.reload();
                                }} else {{
                                    throw new Error(data.error || 'Failed to exchange token');
                                }}
                            }})
                            .catch(error => {{
                                console.error('Exchange error:', error);
                                document.getElementById('plaid-status').innerHTML = 'Error: ' + error.message;
                            }});
                        }}

                        function handleLoad() {{
                            console.log('Plaid Link loaded');
                            document.getElementById('plaid-status').innerHTML = 'Opening Plaid interface...';
                        }}

                        function handleExit(err, metadata) {{
                            if (err != null) {{
                                console.error('Plaid exit error:', err);
                                document.getElementById('plaid-status').innerHTML = 'Error: ' + err.display_message;
                            }} else {{
                                console.log('Plaid Link closed');
                                document.getElementById('plaid-status').innerHTML = 'Interface closed';
                            }}
                        }}

                        function handleEvent(eventName, metadata) {{
                            console.log('Plaid event:', eventName, metadata);
                        }}
                    </script>
                </body>
                </html>
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

# Overview Page
if page == "Overview":
    st.title("Overview")
    # Add overview content here

# Expenses Page
if page == "Expenses":
    st.title("Expenses")
    # Add expenses content here

# Investments Page
if page == "Investments":
    st.title("Investments")
    # Add investments content here

# Goals Page
if page == "Goals":
    st.title("Goals")
    # Add goals content here

from flask import Flask, request, jsonify #This import remains here because it is used in server.py