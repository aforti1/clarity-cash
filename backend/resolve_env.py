# Helpers to resolve environment variables

from dotenv import load_dotenv
import os

def get_nessie_api_key() -> str:
    """Retrieve the Nessie API key from environment variables."""
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))  # Load environment variables from .env file
    return os.getenv("NESSIE_API_KEY")  # Defaulted to public demo key