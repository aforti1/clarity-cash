 
import pandas as pd
from datetime import date

from scoring_config import load_category_config, compute_context_features
from plaid_service import fetch_plaid_transactions, load_pf_taxonomy_map, plaid_to_txns_df

def main():
	access_token = "access-sandbox-4afc0645-08e7-4d24-bb29-7be040408725"

	cfg = load_category_config("data/category_scoring_config.xlsx")
	pf_map = load_pf_taxonomy_map()

	start_date = date(2025, 10, 1)
	end_date = date(2025, 10, 31)

	plaid_txns = fetch_plaid_transactions(access_token, start_date, end_date, 500)
	txns = plaid_to_txns_df(plaid_txns, pf_map)

	ctx = compute_context_features(txns, cfg, pd.to_datetime(start_date), pd.to_datetime(end_date))

	print("Context for period: ", start_date, " to ", end_date)
	print(ctx)

if __name__ == "__main__":
	main()