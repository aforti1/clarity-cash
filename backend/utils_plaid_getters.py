''' Getter functions for the plaid API '''

from backend.instantiate_plaid_user import default_plaid_client
from plaid.model.account_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

def get_accounts(access_token: str, plaid_client = default_plaid_client): -> dict:
    ''' Gets the accounts associated with a given access token '''
    request = AccountsGetRequest(
        access_token=access_token
    )
    response = plaid_client.accounts_get(request)
    return response['accounts']

def get_transactions(access_token: str, start_date: str, end_date: str, plaid_client = default_plaid_client) -> dict:
    ''' Gets the transactions associated with a given access token within a date range '''
    options = TransactionsGetRequestOptions(
        include_personal_finance_category=True
    )
    request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=options
    )
    response = plaid_client.transactions_get(request)
    return response['transactions']

# TODO - Any other getters needed for Plaid API interactions