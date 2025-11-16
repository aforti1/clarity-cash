<<<<<<< Updated upstream
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore
from .resolve_env import get_firebase_creds, get_plaid_secrets, get_hf_token

import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.country_code import CountryCode

from pydantic import BaseModel
from .llm_module import generate_gemini_suggestion, generate_suggestion
=======
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_module import generate_gemini_suggestion, generate_suggestion
from resolve_env import get_firebase_creds, get_plaid_client_id, get_plaid_sandbox_secret

app = FastAPI(title="Clarity Cash LLM API")


>>>>>>> Stashed changes

hf_token = get_hf_token()



# -----------------------------
# Firebase setup
# -----------------------------
if not firebase_admin._apps:
    cred_dict = get_firebase_creds()
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# -----------------------------
# Plaid client setup
# -----------------------------
plaid_secrets = get_plaid_secrets()
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        "clientId": plaid_secrets["client_id"],
        "secret": plaid_secrets["sandbox_secret"]
    }
)
plaid_client = plaid_api.PlaidApi(plaid.ApiClient(configuration))

# -----------------------------
# FastAPI setup
# -----------------------------
app = FastAPI(title="Clarity Cash Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Basic routes
# -----------------------------
@app.get("/")
def root():
    return {"message": "FastAPI + Firebase + Plaid backend running!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# -----------------------------
# Firebase user endpoint
# -----------------------------
@app.get("/users/{uid}")
def get_user(uid: str):
    try:
        user = auth.get_user(uid)
        return {"uid": user.uid, "email": user.email, "display_name": user.display_name}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# -----------------------------
# Plaid endpoints
# -----------------------------
@app.get("/plaid/link-token")
def create_sandbox_link_token():
    try:
        request = LinkTokenCreateRequest(
            user={"client_user_id": "test_user"},
            client_name="Clarity Cash App",
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
    try:
        request = ItemPublicTokenExchangeRequest(public_token=req.public_token)
        response_as_dict = plaid_client.item_public_token_exchange(request).to_dict()
        access_token = response_as_dict.get("access_token")

        # Store in Firestore
        try:
            user_ref = db.collection("users").document(req.uid)
            user_ref.set({"uid": req.uid, "access_token": access_token}, merge=True)
        except Exception as firestore_error:
            print(f"[ERROR] Firestore write failed: {firestore_error}")

        return {"success": True, "access_token": access_token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plaid/accounts/{access_token}")
def get_plaid_accounts(access_token: str):
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = plaid_client.accounts_get(request)
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

<<<<<<< Updated upstream
# -----------------------------
# Gemini endpoint (hosted LLM)
# -----------------------------
=======

# Request body for Gemini
>>>>>>> Stashed changes
class GeminiRequest(BaseModel):
    transaction_name: str
    transaction_amount: float
    category: str
    user_context: dict = None

@app.post("/gemini-suggestion")
def gemini_suggestion(request: GeminiRequest):
    try:
<<<<<<< Updated upstream
        print(f"[LLM] Generating Gemini suggestion for {request.transaction_name} (${request.transaction_amount})")
=======
>>>>>>> Stashed changes
        suggestion = generate_gemini_suggestion(
            transaction_name=request.transaction_name,
            transaction_amount=request.transaction_amount,
            category=request.category,
            user_context=request.user_context
        )
        return {"suggestion": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

<<<<<<< Updated upstream
# -----------------------------
# General LLM endpoint
# -----------------------------
=======
# General LLM endpoint
>>>>>>> Stashed changes
class LLMRequest(BaseModel):
    prompt: str

@app.post("/llm-suggestion")
def llm_suggestion(request: LLMRequest):
    try:
<<<<<<< Updated upstream
        print(f"[LLM] Generating general suggestion for prompt: {request.prompt[:50]}...")
        suggestion = generate_suggestion(request.prompt)
        return {"suggestion": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

private_key = os.getenv("FIREBASE_PRIVATE_KEY")
if private_key is None:
    raise ValueError("FIREBASE_PRIVATE_KEY is not set in environment variables")
private_key = private_key.replace("\\n", "\n")  # Move this after the None check
print("Firebase private key loaded successfully.")
=======
        suggestion = generate_suggestion(request.prompt)
        return {"suggestion": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
>>>>>>> Stashed changes
