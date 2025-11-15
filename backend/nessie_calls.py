''' Defines and exports functions to call Nessie API endpoints '''

import os
import requests
from resolve_env import get_nessie_api_key

NESSIE_API_URL = get_nessie_api_key()
BASE_URL = "https://api.nessieisreal.com"  # Base URL for all Nessie API requests

# TESTING ONLY
print(f"Nessie API Key: {NESSIE_API_URL}")

def get_all_accounts():
    """Fetch all accounts from Nessie API"""
    url = f"{BASE_URL}/accounts?key={NESSIE_API_URL}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_account_by_id(account_id: str):
    """Fetch a specific account by ID from Nessie API"""
    url = f"{BASE_URL}/accounts/{account_id}?key={NESSIE_API_URL}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_account_balances(account_id: str):
    """Fetch balances for a specific account from Nessie API"""
    url = f"{BASE_URL}/accounts/{account_id}/balances?key={NESSIE_API_URL}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_account_transactions(account_id: str, limit: int = 10):
    """Fetch transactions for a specific account from Nessie API"""
    url = f"{BASE_URL}/accounts/{account_id}/transactions?key={NESSIE_API_URL}&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def create_account(account_data: dict):
    """Create a new account in Nessie API"""
    url = f"{BASE_URL}/accounts?key={NESSIE_API_URL}"
    response = requests.post(url, json=account_data)
    response.raise_for_status()
    return response.json()

def create_transaction(account_id: str, transaction_data: dict):
    """Create a new transaction for a specific account in Nessie API"""
    url = f"{BASE_URL}/accounts/{account_id}/transactions?key={NESSIE_API_URL}"
    response = requests.post(url, json=transaction_data)
    response.raise_for_status()
    return response.json()

def get_customer_info(customer_id: str):
    """Fetch customer information from Nessie API"""
    url = f"{BASE_URL}/customers/{customer_id}?key={NESSIE_API_URL}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_merchants(limit: int = 10):
    """Fetch merchants from Nessie API"""
    url = f"{BASE_URL}/merchants?key={NESSIE_API_URL}&limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_merchant_by_id(merchant_id: str):
    """Fetch a specific merchant by ID from Nessie API"""
    url = f"{BASE_URL}/merchants/{merchant_id}?key={NESSIE_API_URL}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_purchases_by_customer_id(customer_id: str):
    """Fetch all purchases from a specififed customer ID from Nessie API"""
    url = f"{BASE_URL}/accounts/{customer_id}/purchases?key={NESSIE_API_URL}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def create_purchase(account_id: str, purchase_data: dict):
    """Create a new purchase for a specific account in Nessie API"""
    url = f"{BASE_URL}/accounts/{account_id}/purchases?key={NESSIE_API_URL}"
    response = requests.post(url, json=purchase_data)
    response.raise_for_status()
    return response.json()

get_all_accounts()