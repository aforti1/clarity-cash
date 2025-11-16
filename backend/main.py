<<<<<<< Updated upstream
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
=======
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from .utils import auth, db, plaid_client, verify_firebase_token
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest

>>>>>>> Stashed changes
app = FastAPI()

# Allow frontend CORS
app.add_middleware(
    CORSMiddleware,
<<<<<<< Updated upstream
    allow_origins=["*"],  # Change this frontend URL in prod
=======
    allow_origins=["*"],  # Change to your frontend URL in production
>>>>>>> Stashed changes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< Updated upstream
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
    public_token: str
    uid: str
@app.post("/plaid/sandbox-exchange-token")
def exchange_sandbox_public_token(req: TokenExchangeRequest = Body(...)):
    """Exchange a Plaid public token for an access token and store it under the user's Firestore doc."""
    try:
        request = plaid_api.ItemPublicTokenExchangeRequest(public_token=req.public_token)
        response_as_dict = plaid_client.item_public_token_exchange(request).to_dict()
        access_token = response_as_dict.get("access_token")
        item_id = response_as_dict.get("item_id")

        # Save Plaid credentials to Firestore under the user's document (merges with existing fields)
        user_doc = db.collection("users").document(req.uid)
        user_doc.set({"plaid": {"access_token": access_token, "item_id": item_id}}, merge=True)

        # Return a sanitized response
        return {"success": True, "item_id": item_id}
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
=======
# Helper function to extract token from Authorization header
def get_token_from_header(request: Request):
    """Extract Firebase token from Authorization header."""
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(status_code=403, detail="Authorization token is missing")
    return token.split(" ")[1]  # Assuming token is sent as "Bearer <id_token>"

@app.get("/plaid/link-token/{uid}")
def create_link_token(uid: str, request: Request):
    """Generate a Plaid Link token for a specific user."""
    # Verify the Firebase ID token (you can pass token from frontend here)
    id_token = get_token_from_header(request)  # Get token from header
    user_uid = verify_firebase_token(id_token)  # Verify and get Firebase UID
    
    # Now, proceed with creating a link token for the specific user
    if user_uid != uid:
        raise HTTPException(status_code=403, detail="Unauthorized: Firebase UID does not match")

    try:
        request = LinkTokenCreateRequest(
            user={"client_user_id": uid},  # Use the Firebase UID as the client_user_id
            client_name="Hackathon App",  # Name of your app
            products=[Products.TRANSACTIONS],  # You can add other products if needed
            country_codes=[CountryCode.US],  # Assuming US is the target country
            language="en"  # Default language for the link interface
        )
        
        # Send request to Plaid API
        response = plaid_client.link_token_create(request)
        
        # Return the link token to the frontend
        return response.to_dict()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating link token: {str(e)}")

@app.post("/plaid/exchange-public-token")
def exchange_public_token(public_token: str, uid: str, request: Request):
    """Exchange the public token for an access token and store it in Firebase."""
    # Verify the Firebase ID token (you can pass token from frontend here)
    id_token = get_token_from_header(request)  # Get token from header
    user_uid = verify_firebase_token(id_token)  # Verify and get Firebase UID
    
    # Ensure the user making the request is authorized
    if user_uid != uid:
        raise HTTPException(status_code=403, detail="Unauthorized: Firebase UID does not match")

    try:
        # Exchange the public token for an access token
        exchange_response = plaid_client.item_public_token_exchange(public_token)
        access_token = exchange_response['access_token']

        # Store the access token in Firebase Firestore under the user's document
        db.collection('users').document(uid).set({
            'plaid_access_token': access_token  # Store the access token securely in Firebase
        }, merge=True)

        return {"message": "Access token saved successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exchanging public token: {str(e)}")
>>>>>>> Stashed changes
