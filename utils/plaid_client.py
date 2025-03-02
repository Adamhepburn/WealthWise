import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
import os
from datetime import datetime, timedelta

class PlaidClient:
    def __init__(self):
        configuration = plaid.Configuration(
            host=plaid.Environment.Sandbox,
            api_key={
                'clientId': os.getenv('PLAID_CLIENT_ID'),
                'secret': os.getenv('PLAID_SECRET')
            }
        )
        self.client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

    def create_link_token(self, user_id):
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="Personal Finance Dashboard",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=str(user_id)
            )
        )
        response = self.client.link_token_create(request)
        return response.link_token

    def exchange_public_token(self, public_token):
        response = self.client.item_public_token_exchange(
            {'public_token': public_token}
        )
        return response.access_token

    def get_transactions(self, access_token, start_date=None, end_date=None):
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.now().date()

        try:
            response = self.client.transactions_get(
                access_token,
                start_date=start_date,
                end_date=end_date
            )
            return response.transactions
        except plaid.ApiException as e:
            print(f"Error fetching transactions: {e}")
            return []
