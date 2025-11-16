# backend/main.py
import os
from dotenv import load_dotenv

# -----------------------------
# Load environment variables first
# -----------------------------
load_dotenv()

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

import firebase_admin
from firebase_admin import credentials, auth, firestore

from .resolve_env import get_firebase_creds, get_plaid_secrets, get_hf_token
from .llm_module import generate_gemini_suggestion, generate_suggestion

import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.country_code import CountryCode

from pydantic import BaseModel

# -----------------------------
# Hugging Face token check
# -----------------------------
HF_API_TOKEN = get_hf_token()
if not HF_API_TOKEN:
    raise ValueError("HF_API_TOKEN not set in environment variables. Add it to your .env file.")

# -----------------------------
# Firebase setup
# -----------------------------
if not firebase_admin._apps:
    cred_dict = get_firebase_creds()
    private_key = cred_dict.get("private_key")
    if not private_key:
        raise ValueError("Firebase private key missing from credentials")
    cred_dict["private_key"] = private_key.replace("\\n", "\n")
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
        "clientId": plaid_secrets["PLAID_CLIENT_ID"],
        "secret": plaid_secrets["PLAID_SANDBOX_SECRET"]
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
    allow_origins=["*"],  # Adjust in production
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

# -----------------------------
# Gemini endpoint
# -----------------------------
class GeminiRequest(BaseModel):
    transaction_name: str
    transaction_amount: float
    category: str
    user_context: dict = None

@app.post("/gemini-suggestion")
def gemini_suggestion(request: GeminiRequest):
    try:
        suggestion = generate_gemini_suggestion(
            transaction_name=request.transaction_name,
            transaction_amount=request.transaction_amount,
            category=request.category,
            user_context=request.user_context
        )
        return {"suggestion": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# General LLM endpoint
# -----------------------------
class LLMRequest(BaseModel):
    prompt: str

@app.post("/llm-suggestion")
def llm_suggestion(request: LLMRequest):
    try:
        suggestion = generate_suggestion(request.prompt)
        return {"suggestion": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Class for populating paycheck spending graph
class paycheckSpending(BaseModel):
    last_paycheck_amount: float
    last_paycheck_date: str
    transactions: list
# TODO TODO TODO SAMPLE LOGIC FILL IN
@app.get("/plaid/paycheck-spending/{uid}")
def get_paycheck_spending(uid: str):
    """Fetch paycheck spending data for a user."""
    try:
        # Fetch user's access token from Firestore
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found in Firestore")
        
        access_token = user_doc.to_dict().get("access_token")
        if not access_token:
            raise HTTPException(status_code=404, detail="Access token not found for user")
        
        # Fetch transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Dummy logic to calculate paycheck spending (to be replaced with real logic)
        last_paycheck_amount = 2000.0  # Placeholder
        last_paycheck_date = "2023-09-15"  # Placeholder
        
        return {
            "last_paycheck_amount": last_paycheck_amount,
            "last_paycheck_date": last_paycheck_date,
            "spent_since_paycheck": transactions  # NOTE NOTE NOTE THIS SHOULD BE CALCULATED
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Class for each transaction
class Transaction(BaseModel):
    transaction_id: str,
    date: str,
    merchant: str,
    category: list,
    amount: float,
    score: float,
    pending: bool
# TODO TODO TODO SAMPLE LOGIC FILL IN
@app.get("/plaid/transactions/{uid}")
def get_user_transactions(uid: str):
    # Fetch the user's access token from Firestore
    try:
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found in Firestore")
        
        access_token = user_doc.to_dict().get("access_token")
        if not access_token:
            raise HTTPException(status_code=404, detail="Access token not found for user")
        
        # Fetch transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            # TODO change basic boilerplate
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        return {"transactions": transactions}

# Class for 7-day mean spending score over the past month
class SpendingScore(BaseModel):
    dates: list
    scores: list
# TODO TODO TODO SAMPLE LOGIC FILL IN
@app.get("/plaid/mean-spending-scores-month/{uid}")
def get_mean_spending_scores_month(uid: str):
    """Fetch 7-day mean spending scores over the past month for a user."""
    try:
        # Fetch user's access token from Firestore
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found in Firestore")
        
        access_token = user_doc.to_dict().get("access_token")
        if not access_token:
            raise HTTPException(status_code=404, detail="Access token not found for user")
        
        # Fetch transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Dummy logic to calculate mean spending scores (to be replaced with real logic)
        dates = ["2023-09-01", "2023-09-02", "2023-09-03"]  # Placeholder
        scores = [75.0, 80.0, 78.0]  # Placeholder
        
        return {
            "dates": dates,
            "scores": scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/plaid/transaction-score/")
def score_transaction(transaction: Transaction):
    """Score a single transaction based on custom logic."""
    try:
        # TODO TODO TODO Dummy scoring logic (to be replaced with real logic)
        score = 100.0 - (transaction.amount / 10.0)  # Placeholder logic
        
        # TODO LLM LOGIC HERE (Generating Description/Reccomendations)
        return {"transaction": transaction, "score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class TransactionDescription(BaseModel):
    transaction: Transaction
    score: float
    description: str  # LLM Generated
    recommendations: list  # LLM Generated

@app.get("/plaid/transaction-description/${uid}/{transaction_id}")
def get_transaction_description(uid: str, transaction_id: str):
    """Fetch score and LLM-generated description + recommendations for a transaction."""
    try:
        # Fetch user's access token from Firestore
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found in Firestore")
        
        access_token = user_doc.to_dict().get("access_token")
        if not access_token:
            raise HTTPException(status_code=404, detail="Access token not found for user")
        
        # Fetch transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Find the specific transaction
        transaction_data = next((tx for tx in transactions if tx["transaction_id"] == transaction_id), None)
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Dummy LLM-generated description and recommendations (to be replaced with real LLM calls)
        description = "This is a sample description generated by an LLM."
        recommendations = ["Consider reducing spending in this category.", "Look for discounts or alternatives."]
        
        return {
            "transaction": transaction_data,
            "score": 85.0,  # Placeholder score
            "description": description,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))