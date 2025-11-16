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

def get_firebase_creds() -> dict:
    """Retrieve the Firebase credentials from environment variables."""
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))  # Load environment variables from .env file
    firebase_creds = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
    }
    return firebase_creds