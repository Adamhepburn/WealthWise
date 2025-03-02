# plaid_client.py
import os
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.country_code import CountryCode  # Add this import


class PlaidClient:

    def __init__(self):
        client_id = os.getenv('PLAID_CLIENT_ID')
        secret = os.getenv('PLAID_SECRET')
        print(f"Debug - Client ID: {client_id}, Secret: {secret}")
        if not client_id or not secret:
            raise ValueError(
                "Plaid API keys (PLAID_CLIENT_ID or PLAID_SECRET) are missing or invalid"
            )
        configuration = plaid.Configuration(host=plaid.Environment.Sandbox,
                                            api_key={
                                                'clientId': client_id,
                                                'secret': secret,
                                            })
        self.client = plaid_api.PlaidApi(configuration)

    def create_link_token(self, user_id):
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                client_name='WealthWise',
                products=['auth', 'transactions'],
                country_codes=[CountryCode('US')],  # Fix: Use CountryCode enum
                language='en')
            response = self.client.link_token_create(request)
            return response['link_token']
        except plaid.exceptions.ApiException as e:
            print(f"Plaid API Error: {e}")
            raise
        except Exception as e:
            print(f"Unexpected Error: {e}")
            raise