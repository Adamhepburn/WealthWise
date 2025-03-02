import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products

class PlaidClient:
    def __init__(self):
        client_id = os.getenv('PLAID_CLIENT_ID')
        secret = os.getenv('PLAID_SECRET')

        if not client_id or not secret:
            raise ValueError(
                "Plaid API keys (PLAID_CLIENT_ID or PLAID_SECRET) are missing or invalid"
            )

        # Initialize the Plaid client with explicit environment
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,  # Using sandbox environment
            api_key={
                'clientId': client_id,
                'secret': secret,
                'plaidVersion': '2020-09-14'  # Explicitly set API version
            }
        )

        self.api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(self.api_client)

    def create_link_token(self, user_id):
        try:
            # Create the request with explicit product enums
            request = LinkTokenCreateRequest(
                products=[Products("auth"), Products("transactions")],
                client_name="WealthWise",
                country_codes=[CountryCode("US")],
                language="en",
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                ),
                redirect_uri=None  # Add this if you need OAuth redirect
            )

            # Make the request and get response
            response = self.client.link_token_create(request)
            return response.link_token

        except plaid.ApiException as e:
            error_response = e.body
            print(f"Plaid API Error: {error_response}")
            raise
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            raise

    def exchange_public_token(self, public_token):
        try:
            exchange_response = self.client.item_public_token_exchange(
                public_token=public_token
            )
            return exchange_response.access_token
        except Exception as e:
            print(f"Error exchanging public token: {e}")
            raise

    def get_transactions(self, access_token):
        try:
            return self.client.transactions_get(
                access_token=access_token,
                start_date="2024-01-01",
                end_date="2024-12-31"
            ).transactions
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            raise