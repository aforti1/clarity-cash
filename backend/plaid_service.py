from datetime import date
from typing import List, Dict
from pathlib import Path
import pandas as pd

from plaid_client import client
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

def fetch_plaid_transactions(access_token, start_date, end_date, count):
	request = TransactionsGetRequest(
		access_token=access_token,
		start_date=start_date,
		end_date=end_date,
		options=TransactionsGetRequestOptions(
			count=count,
			offset=0,
			include_personal_finance_category=True,
		),
	)

	response = client.transactions_get(request)
	data = response.to_dict()

	return data.get("transactions", [])

def load_pf_taxonomy_map():
	ROOT_DIR = Path(__file__).resolve().parent
	csv_path = ROOT_DIR / "data" / "transactions-personal-finance-category-taxonomy.csv"
	taxonomy = pd.read_csv(csv_path)
	taxonomy["CAT_ID"] = taxonomy["CAT_ID"].astype(int)

	mapping = {}
	for _, row in taxonomy.iterrows():
		key = (row["PRIMARY"], row["DETAILED"])
		mapping[key] = int(row["CAT_ID"])

	return mapping
	
def plaid_to_txns_df(plaid_txns, pf_map):
    rows = []

    for t in plaid_txns:
        date = t["date"]
        amount = t["amount"]

        pfc = t.get("personal_finance_category") or {}
        primary = pfc.get("primary")
        detailed = pfc.get("detailed")

        key = (primary, detailed)
        cat_id = pf_map.get(key)
        if cat_id is None:
            continue

        rows.append({
            "transaction_id": t["transaction_id"],
            "date": date,
            "amount": amount,
            "CAT_ID": cat_id,
        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["CAT_ID"] = df["CAT_ID"].astype(int)

    return df
