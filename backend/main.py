from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore
from plaid import Client
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# Load environment variables
load_dotenv()

# ---------------------
# Firebase setup
# ---------------------
FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_JSON")  # path to your Firebase JSON
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------------
# Plaid setup (sandbox)
# ---------------------
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

# ---------------------
# FastAPI app
# ---------------------
app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------
# Routes
# ---------------------

@app.get("/")
def root():
    return {"message": "FastAPI + Firebase + Plaid backend running!"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/users/{uid}")
def get_user(uid: str):
    """Fetch user info from Firebase Auth."""
    try:
        user = auth.get_user(uid)
        return {"uid": user.uid, "email": user.email, "display_name": user.display_name}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/plaid/sandbox-link-token")
def create_sandbox_link_token():
    """Generate a Plaid Link token for testing."""
    try:
        request = plaid_api.LinkTokenCreateRequest(
            user={"client_user_id": "test_user"},
            client_name="Hackathon App",
            products=[Products.TRANSACTIONS],
            country_codes=[CountryCode.US],
            language="en"
        )
        response = plaid_client.link_token_create(request)
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plaid/sandbox-exchange-token/{public_token}")
def exchange_sandbox_public_token(public_token: str):
    """Exchange a Plaid public token for an access token."""
    try:
        request = plaid_api.ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(request)
        return response.to_dict()  # Return as a JSON response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/plaid/accounts/{access_token}")
def get_plaid_accounts(access_token: str):
    """Fetch accounts associated with a given Plaid access token."""
    try:
        request = plaid_api.AccountsGetRequest(access_token=access_token)
        response = plaid_client.accounts_get(request)
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
