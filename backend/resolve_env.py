# Helpers to resolve environment variables

from dotenv import load_dotenv
import os

def get_plaid_client_id() -> str:
    """Retrieve the Nessie API key from environment variables."""
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))  # Load environment variables from .env file
    return os.getenv("PLAID_CLIENT_ID")

def get_plaid_sandbox_secret() -> str:
    """Retrieve the Nessie API key from environment variables."""
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))  # Load environment variables from .env file
    return os.getenv("PLAID_SANDBOX_SECRET")