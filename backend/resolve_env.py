# backend/resolve_env.py
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# -----------------------------
# Firebase credentials
# -----------------------------
def get_firebase_creds() -> dict:
    """
    Returns Firebase service account credentials as a dict.
    Ensures the private key newline characters are correctly formatted.
    """
    private_key = os.getenv("FIREBASE_PRIVATE_KEY")
    if private_key is None:
        raise ValueError("FIREBASE_PRIVATE_KEY not set in environment variables")

    return {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": private_key.replace("\\n", "\n"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
        "universe_domain": os.getenv("FIREBASE_UNIVERSE_DOMAIN"),
    }

# -----------------------------
# Plaid credentials
# -----------------------------
def get_plaid_secrets():
    return {
        "client_id": os.getenv("PLAID_CLIENT_ID"),
        "sandbox_secret": os.getenv("PLAID_SANDBOX_SECRET"),
        "env": os.getenv("PLAID_ENV")
    }

def get_plaid_client_id():
    return os.getenv("PLAID_CLIENT_ID")

def get_plaid_sandbox_secret():
    return os.getenv("PLAID_SANDBOX_SECRET")
