import os
import plaid
from plaid.api import plaid_api
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / "env"
load_dotenv(env_path)

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SANDBOX_SECRET")

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET,
    },
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)