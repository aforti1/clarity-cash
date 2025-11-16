from fastapi import FastAPI, HTTPException, Body 
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from backend.resolve_env import get_firebase_creds, get_plaid_client_id, get_plaid_sandbox_secret
import firebase_admin
from firebase_admin import credentials, auth, firestore
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.country_code import CountryCode
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# ---------------------
# Firebase Firestore setup
# ---------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(get_firebase_creds())
    firebase_admin.initialize_app(cred)
db = firestore.client()

# ---------------------
# Plaid setup (sandbox)
# ---------------------
PLAID_CLIENT_ID = get_plaid_client_id()
PLAID_SECRET = get_plaid_sandbox_secret()
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")  # Safe default to sandbox

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox if PLAID_ENV == "sandbox" else plaid_api.Environment.Development,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET
    }
)
api_client = plaid.ApiClient(configuration=configuration)
plaid_client = plaid_api.PlaidApi(api_client)

# ---------------------
# FastAPI app
# ---------------------
app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this frontend URL in prod
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

@app.get("/plaid/link-token")
def create_sandbox_link_token():
    """ Return the Plaid link token for the frontend to initialize Plaid Link """  
    print("Creating Plaid link token...")
    try:
        request = plaid_api.LinkTokenCreateRequest(
            user={"client_user_id": "test_user"},
            client_name="Hackathon App",
            products=[Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en"
        )
        response = plaid_client.link_token_create(request)
        return {"link_token": response.link_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TokenExchangeRequest(BaseModel):
    uid: str
    public_token: str

@app.post("/plaid/sandbox-exchange-token")
def exchange_sandbox_public_token(req: TokenExchangeRequest = Body(...)):
    """Exchange a Plaid public token for an access token and store it under the user's Firestore doc."""
    try:
        request = ItemPublicTokenExchangeRequest(public_token=req.public_token)
        response_as_dict = plaid_client.item_public_token_exchange(request).to_dict()
        access_token = response_as_dict.get("access_token")
        payload = {"uid": str(req.uid), "access_token": access_token}  # Payload to store in Firestore
        # Store the access token in Firestore under the user's document
        try:
            user_ref = db.collection("users").document(req.uid)
            user_ref.set(payload, merge=True)
        except Exception as firestore_error:
            print(f"[ERROR] Firestore write failed: {str(firestore_error)}")
            # Continue anyway - token exchange succeeded
        
        # Return a sanitized response
        return {"success": True, "access_token": access_token}
    except Exception as e:
        print(f"[ERROR] Token exchange failed: {str(e)}")
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
