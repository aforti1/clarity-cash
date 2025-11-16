# backend/resolve_env.py
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def get_env_var(key: str, required=True):
    """
    Get environment variable safely.
    If required and missing, raises an error.
    """
    value = os.getenv(key)
    if required and not value:
        raise ValueError(f"Environment variable '{key}' not found!")
    return value

def get_firebase_creds():
    """
    Returns a dict with Firebase credentials for service account.
    """
    private_key = get_env_var("FIREBASE_PRIVATE_KEY")
    
    # If the private key is in single-line form with \n, convert to real newlines
    if "\\n" in private_key:
        private_key = private_key.replace("\\n", "\n")
    
    return {
        "type": get_env_var("FIREBASE_TYPE"),
        "project_id": get_env_var("FIREBASE_PROJECT_ID"),
        "private_key_id": get_env_var("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": private_key,
        "client_email": get_env_var("FIREBASE_CLIENT_EMAIL"),
        "client_id": get_env_var("FIREBASE_CLIENT_ID"),
        "auth_uri": get_env_var("FIREBASE_AUTH_URI"),
        "token_uri": get_env_var("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": get_env_var("FIREBASE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": get_env_var("FIREBASE_CLIENT_CERT_URL"),
    }

def get_plaid_secrets():
    return {
        "client_id": get_env_var("PLAID_CLIENT_ID"),
        "sandbox_secret": get_env_var("PLAID_SANDBOX_SECRET"),
        "env": get_env_var("PLAID_ENV"),
    }

def get_hf_token():
    return get_env_var("HF_API_TOKEN")

