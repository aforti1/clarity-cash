''' Instantiates a Plaid client to use throughout the backend '''
import plaid
from plaid.api import plaid_api
import os
from backend.resolve_env import get_plaid_client_id, get_plaid_sandbox_secret
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

def instantiate_plaid_client() -> Client:
    ''' Instantiates and returns a Plaid client'''
    config = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': get_plaid_client_id(),
            'secret': get_plaid_sandbox_secret()
        }
    )

    api_client = plaid.ApiClient(configuration=config)
    return plaid_api.PlaidApi(client)

default_plaid_client = instantiate_plaid_client()  # Create a default Plaid client instance

def exchange_public_token(public_token: str, plaid_client = default_plaid_client) -> str:
    ''' Exchanges a Plaid public token for an access token '''
    request = ItemPublicTokenExchangeRequest(public_token=public_token)
    response = plaid_client.item_public_token_exchange(request)
    return response['access_token']

def create_link_token_for_user(user_id: str, plaid_client = default_plaid_client) -> str:
    ''' Creates a Plaid link token for a given user ID '''
    request = LinkTokenCreateRequest(
        user={'client_user_id': user_id},
        client_name='Clarity Cash',
        products=['transactions'],
        country_codes=['US'],
        language='en'
    )
    response = plaid_client.link_token_create(request)
    return response['link_token']