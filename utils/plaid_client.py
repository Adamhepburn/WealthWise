import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode
from plaid.model.products import Products

class PlaidClient:
    def __init__(self):
        # Get credentials from environment
        self.client_id = os.getenv('PLAID_CLIENT_ID')
        self.secret = os.getenv('PLAID_SECRET')

        if not self.client_id or not self.secret:
            raise ValueError("Missing required Plaid API credentials")

        try:
            # Configure API client
            configuration = plaid.Configuration(
                host=plaid.Environment.Sandbox,
                api_key={
                    'clientId': self.client_id,
                    'secret': self.secret,
                    'plaidVersion': '2020-09-14'
                }
            )

            # Initialize API client
            self.api_client = plaid.ApiClient(configuration)
            self.client = plaid_api.PlaidApi(self.api_client)

        except Exception as e:
            print(f"Error initializing Plaid client: {str(e)}")
            raise

    def create_link_token(self, user_id):
        try:
            # Create link token request
            request = LinkTokenCreateRequest(
                products=[Products("transactions")],
                client_name="WealthWise",
                country_codes=[CountryCode("US")],
                language="en",
                user=LinkTokenCreateRequestUser(
                    client_user_id=user_id
                )
            )

            # Create link token
            response = self.client.link_token_create(request)
            return response.link_token

        except plaid.ApiException as e:
            print(f"Plaid API Error: {e.body}")
            raise
        except Exception as e:
            print(f"Error creating link token: {str(e)}")
            raise

    def exchange_public_token(self, public_token):
        try:
            exchange_response = self.client.item_public_token_exchange(
                public_token=public_token
            )
            return exchange_response.access_token
        except Exception as e:
            print(f"Error exchanging public token: {str(e)}")
            raise

    def get_transactions(self, access_token):
        try:
            return self.client.transactions_get(
                access_token=access_token,
                start_date="2024-01-01",
                end_date="2024-12-31"
            ).transactions
        except Exception as e:
            print(f"Error fetching transactions: {str(e)}")
            raise