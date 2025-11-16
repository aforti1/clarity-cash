import pandas as pd
from datetime import datetime

def load_category_config(path):
	xlsx = pd.ExcelFile(path)

	cat_labels = pd.read_excel(xlsx, "CAT_LABELS")
	profile = pd.read_excel(xlsx, "PROFILE")
	spc = pd.read_excel(xlsx, "SPEND_PROF_CATEGORY")
	context = pd.read_excel(xlsx, "CONTEXT")
	cc = pd.read_excel(xlsx, "CONTEXT_CATEGORY")

	cfg = (cat_labels
		.merge(spc, on="CAT_ID", how="left")
		.merge(profile, on="PROF_ID", how="left"))
	
	cfg = (cfg
		.merge(cc, on="CAT_ID", how="left")
		.merge(context, on="CONTEXT_ID", how="left"))

	return cfg

def compute_context_features(txns, cfg, start_date, end_date):
	txns = txns.copy()
	txns['date'] = pd.to_datetime(txns['date'])

	mask = (txns['date'] >= start_date) & (txns['date'] <= end_date)
	period = txns.loc[mask].copy()

	merged = period.merge(cfg[['CAT_ID', 'CONTEXT_BUCKET']], on='CAT_ID', how='left')

	inc_mask = merged['CONTEXT_BUCKET'] == 'EFFECTIVE_INCOME'
	effective_income = (-merged.loc[inc_mask, 'amount']).sum()
	if effective_income <= 0:
		effective_income = 1e-6

	bucket_sums = merged.groupby('CONTEXT_BUCKET')['amount'].sum()

	savings_out = bucket_sums.get('SAVINGS_CONTENT', 0.0)
	savings_rate = max(0.0, savings_out) / effective_income

	cash_adv = bucket_sums.get('EMERGENCY_BORROWING', 0.0)
	cash_adv_share = max(0.0, -cash_adv) / effective_income
	cash_adv_flag = int(cash_adv_share > 0)

	fees_total = bucket_sums.get('FEES_CONTEXT', 0.0)
	fees_ratio = max(0.0, fees_total) / effective_income
	fees_penalty = min(1.0, fees_ratio / 0.05)

	structural_total = bucket_sums.get('STRUCTURAL_UNAVOIDABLE', 0.0)
	structural_share = max(0.0, structural_total) / effective_income

	core_flex_total = bucket_sums.get('FLEX_CORE_ESSENTIAL', 0.0)
	core_flex_share = max(0.0, core_flex_total) / effective_income

	other_flex_total = bucket_sums.get('FLEX_OTHER_ESSENTIAL', 0.0)
	other_flex_share = max(0.0, other_flex_total) / effective_income

	return {
		"effective_income": float(effective_income),
		"savings_rate": float(savings_rate),
		"cash_adv_share": float(cash_adv_share),
		"cash_adv_flag": cash_adv_flag,
		"fees_ratio": float(fees_ratio),
		"fees_penalty": float(fees_penalty),
		"structural_share": float(structural_share),
		"core_flex_share": float(core_flex_share),
		"other_flex_share": float(other_flex_share),
	}

#sample main
def main():
	config = load_category_config("C:/Users/anye forti/Desktop/Projects/clarity-cash/backend/data/category_scoring_config.xlsx")

	transactions = pd.DataFrame([
		{"date": "2025-10-01", "amount": -2000.00, "CAT_ID":  506},  # paycheck (income)
		{"date": "2025-10-02", "amount":  1000.00, "CAT_ID":  600},  # rent
		{"date": "2025-10-03", "amount":   120.50, "CAT_ID":  540},  # groceries
		{"date": "2025-10-04", "amount":    45.00, "CAT_ID":  588},  # gas
		{"date": "2025-10-05", "amount":    35.00, "CAT_ID":  525},  # bank fee
	])

	ctx = compute_context_features(transactions, config, pd.Timestamp("2025-10-01"), pd.Timestamp("2025-10-06"))

	print(ctx)

if __name__ == "__main__":
	main()