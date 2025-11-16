# backend/main.py - Holds our FastAPI backend endpoints, integrating with Firebase, Plaid, and LLMs
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
from datetime import date, datetime, timedelta
from collections import defaultdict

import pandas as pd
import numpy as np
from scoring_config import load_category_config, compute_context_features
from plaid_service import (
    fetch_plaid_transactions,
    load_pf_taxonomy_map,
    plaid_to_txns_df,
)

from transaction_scorer import TransactionScorer

# -----------------------------
# Hugging Face token check
# -----------------------------
# HF_API_TOKEN = get_hf_token()
# if not HF_API_TOKEN:
#     raise ValueError("HF_API_TOKEN not set in environment variables. Add it to your .env file.")

# --------- SCORING SETUP (GLOBAL SINGLETONS) ---------
ROOT_DIR = Path(__file__).resolve().parent

CATEGORY_CFG_PATH = ROOT_DIR / "data" / "category_scoring_config.xlsx"

# Load the full category config (merges CAT_LABELS, PROFILE, CONTEXT, etc.)
SCORING_CFG = load_category_config(CATEGORY_CFG_PATH)

# Load Plaid personal_finance_category → CAT_ID mapping
PF_MAP = load_pf_taxonomy_map()

# Create a single scorer instance
SCORER = TransactionScorer(SCORING_CFG)

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
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to get access token from uid from Firestore
def get_access_token_from_uid(uid: str) -> str:
    try:
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return user_data.get("access_token", "")
        else:
            raise ValueError("User not found in Firestore")
    except Exception as e:
        raise ValueError(f"Error fetching access token: {str(e)}")
    
# Helper to get date ranges in standardized format
def get_time_date_range(range_weeks: int = 10):
    end_date = date.today()
    start_date = end_date - timedelta(weeks=range_weeks)
    return end_date.strftime("%Y-%m-%d"), start_date.strftime("%Y-%m-%d")

def get_scored_plaid_transactions(access_token: str, start_date, end_date, count: int = 500):
    # 1) Fetch raw Plaid transactions for the window
    plaid_txns = fetch_plaid_transactions(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        count=count,
    )

    if not plaid_txns:
        return []

    # 2) Convert Plaid → internal txns DataFrame with CAT_IDs
    txns_df = plaid_to_txns_df(plaid_txns, PF_MAP)
    if txns_df.empty:
        # Nothing we can score, just return original with no scores
        for t in plaid_txns:
            t["score"] = None
            t["profile"] = None
            t["severity"] = None
        return plaid_txns

    # 3) Compute context features from actual transaction mix
    #    Uses your CONTEXT_BUCKET logic: EFFECTIVE_INCOME, FEES_CONTEXT, etc.
    context_features = compute_context_features(
        txns_df,
        SCORING_CFG,
        start_date,
        end_date,
    )

    # 4) Run the scorer
    scored_df = SCORER.score_all_transactions(txns_df, context_features)

    # 5) Build lookup tables by transaction_id
    score_by_tid = dict(zip(scored_df["transaction_id"], scored_df["score"]))
    profile_by_tid = dict(zip(scored_df["transaction_id"], scored_df["profile"]))
    severity_by_tid = dict(zip(scored_df["transaction_id"], scored_df["severity"]))

    # 6) Attach scores back to the original Plaid transaction dicts
    for t in plaid_txns:
        tid = t["transaction_id"]
        if tid in score_by_tid:
            t["score"] = float(score_by_tid[tid])  # 0..100
            t["profile"] = profile_by_tid.get(tid)  # DISCRETIONARY_WANT, etc.
            t["severity"] = severity_by_tid.get(tid)  # very_low..very_high
        else:
            t["score"] = None
            t["profile"] = None
            t["severity"] = None

    return plaid_txns


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
        
        # Observe the last 6 weeks of transactions
        end_date_today, start_date = get_time_date_range(range_weeks=6)
        
        # Fetch transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date_today
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Retreive the last deposit made to the account as the last paycheck
        sorted_transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        last_paycheck = None
        for tx in sorted_transactions:
            if tx['amount'] < 0:  # Assuming negative amount means deposit/inflow
                last_paycheck = tx
                break  # Break at first instance
        
        # Calculate spent since last paycheck
        if last_paycheck:
            last_paycheck_amount = abs(last_paycheck['amount'])
            last_paycheck_date = last_paycheck['date']
            # Calculate spent since paycheck (sum of outflows since that date)
            spent_since_paycheck = sum(tx['amount'] for tx in transactions if tx['date'] >= last_paycheck_date and tx['amount'] > 0)
        else:
            # Handle case where no deposit found
            last_paycheck_amount = 0.0
            last_paycheck_date = "N/A"
            spent_since_paycheck = 0.0

        return {
            "last_paycheck_amount": last_paycheck_amount,
            "last_paycheck_date": last_paycheck_date,
            "spent_since_paycheck": spent_since_paycheck
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Class for each transaction
class Transaction(BaseModel):
    transaction_id: str
    date: str
    merchant: str
    category: list
    amount: float
    score: float
    pending: bool

@app.get("/plaid/transactions/{uid}")
def get_user_transactions(uid: str):
    try:
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found in Firestore")
        
        access_token = user_doc.to_dict().get("access_token")
        if not access_token:
            raise HTTPException(status_code=404, detail="Access token not found for user")
        
        end_date_today, start_date = get_time_date_range(range_weeks=10)

        scored_txns = get_scored_plaid_transactions(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date_today,
            count=500,
        )

        return {"transactions": scored_txns}
    
    except ApiException as e:
        raise HTTPException(status_code=500, detail=str(e))

# Class for 7-day mean spending score over the past month
class SpendingScore(BaseModel):
    dates: list
    scores: list

@app.get("/plaid/mean-spending-scores-month/{uid}")
def get_mean_spending_scores_month(uid: str):
    """Fetch 7-day mean spending scores over the past month for a user."""
    try:
        # Fetch user's access token from Firestore
        access_token = get_access_token_from_uid(uid)
        
        if not access_token:
            raise HTTPException(status_code=404, detail="Access token not found for user")
        
        end_date_today, start_date = get_time_date_range(range_weeks=10)
        
        # Fetch transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date_today
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Convert start_date string to datetime for calculations
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        
        # Group transactions by week and calculate scores
        weekly_data = defaultdict(lambda: {"total_amount": 0, "count": 0})
        
        for txn in transactions:
            txn_date = datetime.strptime(txn["date"], "%Y-%m-%d")
            # Calculate week number (0-9) from start_date
            days_from_start = (txn_date - start_date_dt).days
            week_num = days_from_start // 7
            
            if 0 <= week_num < 10:  # Only include transactions within 10 weeks
                # Only count positive amounts (spending, not income)
                amount = txn["amount"]
                if amount > 0:
                    weekly_data[week_num]["total_amount"] += amount
                    weekly_data[week_num]["count"] += 1
        
        # Calculate mean scores for each week
        dates = []
        scores = []
        
        for week in range(10):
            week_start_date = start_date_dt + timedelta(weeks=week)
            dates.append(week_start_date.strftime("%Y-%m-%d"))
            
            # TODO TODO TODO RESOLVE THIS WITH REAL SCORES
            if week in weekly_data and weekly_data[week]["count"] > 0:
                # Calculate a score: higher spending = lower score
                avg_spending = weekly_data[week]["total_amount"] / weekly_data[week]["count"]
                # Score formula: 100 - (avg_spending / 10), clamped between 0-100
                score = max(0, min(100, 100 - (avg_spending / 10)))
                scores.append(round(score, 2))
            else:
                # No transactions this week, assign neutral score
                scores.append(50.0)
        
        return {
            "dates": dates,
            "mean_scores": scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/plaid/transaction-score/")
def score_transaction(transaction: Transaction):
    """Score a single transaction based on custom logic."""
    try:
        # TODO TODO TODO FIX Dummy scoring logic (to be replaced with real logic)
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

@app.get("/plaid/transaction-description/{uid}/{transaction_id}")
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
        
        # Fetch ALL transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date="1900-01-01",
            end_date=date.today().strftime("%Y-%m-%d")
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Find the specific transaction
        transaction_data = next((tx for tx in transactions if tx["transaction_id"] == transaction_id), None)
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # TODO TODO TODO NOTE NOTE NOTE Get score and dummy LLM-generated description and recommendations
        
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
# backend/main.py - Holds our FastAPI backend endpoints, integrating with Firebase, Plaid, and LLMs
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
from datetime import date, datetime, timedelta
from collections import defaultdict

# -----------------------------
# Hugging Face token check
# -----------------------------
# HF_API_TOKEN = get_hf_token()
# if not HF_API_TOKEN:
#     raise ValueError("HF_API_TOKEN not set in environment variables. Add it to your .env file.")

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
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper to get access token from uid from Firestore
def get_access_token_from_uid(uid: str) -> str:
    try:
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return user_data.get("access_token", "")
        else:
            raise ValueError("User not found in Firestore")
    except Exception as e:
        raise ValueError(f"Error fetching access token: {str(e)}")
    
# Helper to get date ranges in standardized format
def get_time_date_range(range_weeks: int = 10):
    """
    Returns (end_date, start_date) as datetime.date objects.
    end_date = today, start_date = end_date - range_weeks
    """
    end_date = date.today()
    start_date = end_date - timedelta(weeks=range_weeks)
    return end_date, start_date

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
        
        # Observe the last 6 weeks of transactions
        end_date_today, start_date = get_time_date_range(range_weeks=6)
        
        # Fetch transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,          # pass date object
            end_date=end_date_today         # pass date object
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Retrieve the last deposit made to the account as the last paycheck
        sorted_transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
        last_paycheck = None
        for tx in sorted_transactions:
            if tx['amount'] < 0:  # Assuming negative amount means deposit/inflow
                last_paycheck = tx
                break  # Break at first instance
        
        # Calculate spent since last paycheck
        if last_paycheck:
            last_paycheck_amount = abs(last_paycheck['amount'])
            last_paycheck_date = last_paycheck['date']
            # Calculate spent since paycheck (sum of outflows since that date)
            spent_since_paycheck = sum(
                tx['amount']
                for tx in transactions
                if tx['date'] >= last_paycheck_date and tx['amount'] > 0
            )
            # Cap at 100
            spent_since_paycheck = min(spent_since_paycheck, 100)
        else:
            # Handle case where no deposit found
            last_paycheck_amount = 0.0
            last_paycheck_date = "N/A"
            spent_since_paycheck = 0.0

        return {
            "last_paycheck_amount": last_paycheck_amount,
            "last_paycheck_date": last_paycheck_date,
            "spent_since_paycheck": spent_since_paycheck
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Class for each transaction
class Transaction(BaseModel):
    transaction_id: str
    date: str
    merchant: str
    category: list
    amount: float
    score: float
    pending: bool

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
        
        end_date_today, start_date = get_time_date_range(range_weeks=10)
        
        # Fetch transactions from Plaid (last 10 weeks as example)
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,          # pass date object
            end_date=end_date_today         # pass date object
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # TODO FIX WITH REAL SCORES - Add placeholder scores to transactions
        for txn in transactions:
            # TODO FIX Placeholder scoring logic: higher amounts get lower scores
            amount = abs(txn.get("amount", 0))
            score = max(0, min(100, 100 - (amount / 10)))
            txn["score"] = round(score, 2)
        
        return {"transactions": transactions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Class for 7-day mean spending score over the past month
class SpendingScore(BaseModel):
    dates: list
    scores: list

@app.get("/plaid/mean-spending-scores-month/{uid}")
def get_mean_spending_scores_month(uid: str):
    """Fetch 7-day mean spending scores over the past month for a user."""
    try:
        # Fetch user's access token from Firestore
        access_token = get_access_token_from_uid(uid)
        
        if not access_token:
            raise HTTPException(status_code=404, detail="Access token not found for user")
        
        end_date_today, start_date = get_time_date_range(range_weeks=10)
        
        # Fetch transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,          # pass date object
            end_date=end_date_today         # pass date object
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Group transactions by week and calculate scores
        weekly_data = defaultdict(lambda: {"total_amount": 0, "count": 0})
        
        for txn in transactions:
            # Parse transaction date string to date object
            if isinstance(txn["date"], str):
                txn_date = datetime.strptime(txn["date"], "%Y-%m-%d").date()
            else:
                txn_date = txn["date"]
            # Calculate week number (0-9) from start_date
            days_from_start = (txn_date - start_date).days
            week_num = days_from_start // 7
            
            if 0 <= week_num < 10:  # Only include transactions within 10 weeks
                # Only count positive amounts (spending, not income)
                amount = txn["amount"]
                if amount > 0:
                    weekly_data[week_num]["total_amount"] += amount
                    weekly_data[week_num]["count"] += 1
        
        # Calculate mean scores for each week
        dates = []
        scores = []
        
        for week in range(10):
            week_start_date = start_date + timedelta(weeks=week)
            dates.append(week_start_date.strftime("%Y-%m-%d"))
            
            # TODO TODO TODO RESOLVE THIS WITH REAL SCORES
            if weekly_data[week]["count"] > 0:
                # Calculate a score: higher spending = lower score
                avg_spending = weekly_data[week]["total_amount"] / weekly_data[week]["count"]
                # Score formula: 100 - (avg_spending / 10), clamped between 0-100
                score = max(0, min(100, 100 - (avg_spending / 10)))
                scores.append(round(score, 2))
            else:
                # No transactions this week, assign neutral score
                scores.append(50.0)
        
        return {
            "dates": dates,
            "mean_scores": scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/plaid/transaction-score/")
def score_transaction(transaction: Transaction):
    """Score a single transaction based on custom logic."""
    try:
        # TODO TODO TODO FIX Dummy scoring logic (to be replaced with real logic)
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

@app.get("/plaid/transaction-description/{uid}/{transaction_id}")
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
        
        # Fetch ALL transactions from Plaid
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=date(1900, 1, 1),   # use date object, not string
            end_date=date.today()          # use date object, not string
        )
        response = plaid_client.transactions_get(request)
        transactions = response.to_dict().get("transactions", [])
        
        # Find the specific transaction
        transaction_data = next((tx for tx in transactions if tx["transaction_id"] == transaction_id), None)
        if not transaction_data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # TODO TODO TODO NOTE NOTE NOTE Get score and dummy LLM-generated description and recommendations
        
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
