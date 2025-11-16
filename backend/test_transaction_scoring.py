import pandas as pd
from datetime import datetime, date
import sys
sys.path.append('/mnt/user-data/uploads')

from scoring_config import load_category_config, compute_context_features
from transaction_scorer import TransactionScorer


def create_comparison_scenarios():
    
    # Same transactions for both people
    common_transactions = [
        # Discretionary spending
        {'date': '2025-10-03', 'amount': 50.00, 'CAT_ID': 531},   # Restaurant
        {'date': '2025-10-07', 'amount': 75.00, 'CAT_ID': 531},   # Restaurant
        {'date': '2025-10-15', 'amount': 150.00, 'CAT_ID': 532},  # Entertainment
        
        # Essential spending
        {'date': '2025-10-05', 'amount': 120.00, 'CAT_ID': 540},  # Groceries
        {'date': '2025-10-19', 'amount': 125.00, 'CAT_ID': 540},  # Groceries
    ]
    
    # Person A: High income, healthy finances
    person_a = common_transactions.copy()
    person_a.extend([
        {'date': '2025-10-01', 'amount': -10000.00, 'CAT_ID': 506},  # Income: $10k
        {'date': '2025-10-01', 'amount': 1500.00, 'CAT_ID': 514},    # Invest $1.5k
        {'date': '2025-10-15', 'amount': 500.00, 'CAT_ID': 515},     # Save $500
    ])
    
    # Person B: Low income, financial stress
    person_b = common_transactions.copy()
    person_b.extend([
        {'date': '2025-10-01', 'amount': -3000.00, 'CAT_ID': 506},   # Income: $3k
        {'date': '2025-10-05', 'amount': 35.00, 'CAT_ID': 525},      # Overdraft fee
        {'date': '2025-10-20', 'amount': 12.00, 'CAT_ID': 526},      # ATM fee
        {'date': '2025-10-10', 'amount': 100.00, 'CAT_ID': 508},     # Cash advance
    ])
    
    df_a = pd.DataFrame(person_a)
    df_a['date'] = pd.to_datetime(df_a['date'])
    df_a['CAT_ID'] = df_a['CAT_ID'].astype(int)
    
    df_b = pd.DataFrame(person_b)
    df_b['date'] = pd.to_datetime(df_b['date'])
    df_b['CAT_ID'] = df_b['CAT_ID'].astype(int)
    
    return df_a, df_b


def main():
    print("=" * 80)
    print("RISK-BASED TRANSACTION SCORING - COMPARISON TEST")
    print("=" * 80)
    print("\nThis demonstrates how the SAME transactions get DIFFERENT scores")
    print("based on each person's financial capacity.\n")
    
    print("Loading configuration...")
    cfg = load_category_config("data/category_scoring_config.xlsx")
    
    print("Creating comparison scenarios...\n")
    txns_a, txns_b = create_comparison_scenarios()
    
    start_date = pd.to_datetime('2025-10-01')
    end_date = pd.to_datetime('2025-10-31')
    
    print("=" * 80)
    print("PERSON A: High Income, Healthy Finances")
    print("=" * 80)
    context_a = compute_context_features(txns_a, cfg, start_date, end_date)
    print(f"\nIncome: ${context_a['effective_income']:,.2f}")
    print(f"Savings Rate: {context_a['savings_rate']*100:.1f}%")
    print(f"Fees: ${context_a['fees_ratio']*context_a['effective_income']:.2f}")
    print(f"Cash Advances: {'Yes' if context_a['cash_adv_flag'] else 'No'}")
    
    scorer = TransactionScorer(cfg)
    scored_a = scorer.score_all_transactions(txns_a, context_a)
    
    print("\nScored Transactions:")
    print(f"{'Date':<12} {'Amount':>10} {'Category':<20} {'Score':>7}")
    print("-" * 60)
    for _, row in scored_a[scored_a['is_scored'] == True].iterrows():
        cat = row.get('profile', 'Unknown')
        print(f"{str(row['date'].date()):<12} ${row['amount']:>9.2f} {cat:<20} {row['score']:>7.1f}")
    
    print("\n\n" + "=" * 80)
    print("PERSON B: Low Income, Financial Stress")
    print("=" * 80)
    context_b = compute_context_features(txns_b, cfg, start_date, end_date)
    print(f"\nIncome: ${context_b['effective_income']:,.2f}")
    print(f"Savings Rate: {context_b['savings_rate']*100:.1f}%")
    print(f"Fees: ${context_b['fees_ratio']*context_b['effective_income']:.2f}")
    print(f"Cash Advances: {'Yes' if context_b['cash_adv_flag'] else 'No'}")
    
    scored_b = scorer.score_all_transactions(txns_b, context_b)
    
    print("\nScored Transactions:")
    print(f"{'Date':<12} {'Amount':>10} {'Category':<20} {'Score':>7}")
    print("-" * 60)
    for _, row in scored_b[scored_b['is_scored'] == True].iterrows():
        cat = row.get('profile', 'Unknown')
        print(f"{str(row['date'].date()):<12} ${row['amount']:>9.2f} {cat:<20} {row['score']:>7.1f}")
    
    print("\n\n" + "=" * 80)
    print("SIDE-BY-SIDE COMPARISON: Same Transactions, Different Scores")
    print("=" * 80)
    print(f"\n{'Transaction':<25} {'Amount':>10} {'Person A':>12} {'Person B':>12} {'Difference':>12}")
    print("-" * 80)
    
    common_cats = [531, 532, 540]
    
    for cat in common_cats:
        txns_in_cat_a = scored_a[scored_a['CAT_ID'] == cat]
        txns_in_cat_b = scored_b[scored_b['CAT_ID'] == cat]
        
        for (_, row_a), (_, row_b) in zip(txns_in_cat_a.iterrows(), txns_in_cat_b.iterrows()):
            cat_name = row_a.get('profile', 'Unknown')
            score_a = row_a['score']
            score_b = row_b['score']
            diff = score_a - score_b
            
            print(f"{cat_name:<25} ${row_a['amount']:>9.2f} "
                  f"{score_a:>12.1f} {score_b:>12.1f} {diff:>+12.1f}")
    
    print("\n\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    
    print("\n1. FINANCIAL CAPACITY MATTERS")
    capacity_a = scorer.calculate_financial_capacity(context_a)
    capacity_b = scorer.calculate_financial_capacity(context_b)
    print(f"   Person A safe discretionary: ${capacity_a['safe_discretionary']:,.2f}")
    print(f"   Person B safe discretionary: ${capacity_b['safe_discretionary']:,.2f}")
    print(f"   → Same $50 restaurant is {capacity_a['safe_discretionary']/capacity_b['safe_discretionary']:.1f}x less risky for Person A")
    
    print("\n2. SAME AMOUNT = DIFFERENT RISK")
    print("   $75 restaurant for Person A: High score (easily affordable)")
    print("   $75 restaurant for Person B: Low score (consumes large % of safe budget)")
    
    print("\n3. CONTEXT COMPOUNDS RISK")
    print("   Person B already has fees and cash advances")
    print("   → Every discretionary purchase becomes riskier")
    
    print("\n4. NEGATIVE EVENTS SCALED BY INCOME")
    neg_a = scored_a[scored_a['profile'] == 'NEGATIVE_EVENTS']
    neg_b = scored_b[scored_b['profile'] == 'NEGATIVE_EVENTS']
    
    if len(neg_b) > 0:
        avg_neg_score_b = neg_b['score'].mean()
        print(f"   Person B's fees average score: {avg_neg_score_b:.1f}")
        print(f"   → $35 overdraft on $3k income = {35/3000*100:.2f}% of income")
        print(f"   → High severity = low score")
    
    print("\n\n" + "=" * 80)
    print("SAVING OUTPUTS")
    print("=" * 80)
    
    scored_a.to_csv('C:/Users/anye forti/Desktop/person_a_scored.csv', index=False)
    scored_b.to_csv('C:/Users/anye forti/Desktop/person_b_scored.csv', index=False)
    
    print("\n" + "=" * 80)
    print("Risk-based scoring complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()