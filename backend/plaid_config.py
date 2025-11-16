# backend/plaid_config.py
import os
from plaid import Client
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

configuration = plaid_api.Configuration(
    host=plaid_api.Environment.Sandbox if PLAID_ENV == "sandbox" else plaid_api.Environment.Production,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET
    }
)

plaid_client = plaid_api.PlaidApi(configuration)
