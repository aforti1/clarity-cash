import pandas as pd
import numpy as np
from datetime import datetime


class TransactionScorer:
    RECOMMENDED_SAVINGS_RATE = 0.15

    def __init__(self, cfg):
        self.cfg = cfg

        self.cat_to_profile = dict(zip(cfg["CAT_ID"], cfg["SPEND_PROFILE"]))
        self.cat_to_scored = dict(zip(cfg["CAT_ID"], cfg["IS_SCORED"]))
        self.cat_to_context = dict(zip(cfg["CAT_ID"], cfg["CONTEXT_BUCKET"]))

    def calculate_financial_capacity(self, context_features):
        effective_income = context_features.get("effective_income", 0.0)

        structural = context_features.get("structural_share", 0.0) * effective_income
        core_flex = context_features.get("core_flex_share", 0.0) * effective_income
        other_flex = context_features.get("other_flex_share", 0.0) * effective_income
        necessary_spending = structural + core_flex + other_flex

        recommended_savings = effective_income * self.RECOMMENDED_SAVINGS_RATE

        safe_discretionary = max(
            0.0, effective_income - necessary_spending - recommended_savings
        )

        has_cash_advances = context_features.get("cash_adv_flag", 0) > 0
        fees_ratio = context_features.get("fees_ratio", 0.0)
        savings_rate = context_features.get("savings_rate", 0.0)

        buffer_ratio = (
            safe_discretionary / effective_income if effective_income > 0 else 0.0
        )

        in_distress = bool(has_cash_advances or fees_ratio > 0.02)

        return {
            "effective_income": effective_income,
            "necessary_spending": necessary_spending,
            "safe_discretionary": safe_discretionary,
            "buffer_ratio": buffer_ratio,
            "fees_ratio": fees_ratio,
            "savings_rate": savings_rate,
            "has_cash_advances": has_cash_advances,
            "in_distress": in_distress,
        }

    @staticmethod
    def _bounded(value, low=0.0, high=100.0):
        return max(low, min(high, value))

    def _decay_vs_ratio(self, ratio, mid, power):
        if ratio <= 0:
            return 1.0
        x = ratio / max(mid, 1e-9)
        return 1.0 / (1.0 + x**power)

    def score_discretionary(self, txn_amount, capacity, context_features, is_harmful):
        safe_budget = capacity["safe_discretionary"]

        if safe_budget <= 0:
            base = 5.0
            return {
                "score": base,
                "pct_of_safe_budget": None,
                "severity": self._classify_severity(base),
                "reason": "No safe discretionary budget available",
            }

        ratio = txn_amount / safe_budget
        decay = self._decay_vs_ratio(ratio, mid=0.25, power=1.4)
        base = 100.0 * decay

        harmful_share = context_features.get("avoidable_harmful_share", 0.0)
        neutral_share = context_features.get("avoidable_neutral_share", 0.0)

        if is_harmful:
            harm_factor = 1.0 - min(0.5, harmful_share * 2.0)
            base *= max(0.4, harm_factor)
        else:
            neutral_factor = 1.0 - min(0.15, neutral_share * 0.5)
            base *= neutral_factor

        if capacity["in_distress"]:
            distress_index = min(
                1.2,
                capacity["fees_ratio"] / 0.05
                + context_features.get("cash_adv_share", 0.0) * 2.0,
            )
            base *= (1.0 - 0.25 * distress_index)

        base = self._bounded(base, 0.0, 100.0)

        return {
            "score": base,
            "pct_of_safe_budget": ratio * 100.0,
            "severity": self._classify_severity(base),
        }

    def score_savings(self, txn_row, capacity, all_txns, context_features):
        income = capacity["effective_income"]
        if income <= 0:
            base = 50.0
            return {
                "score": base,
                "savings_pct": None,
                "severity": self._classify_severity(base),
            }

        tx_date = pd.to_datetime(txn_row["date"])
        frame = all_txns.copy()
        frame["date_parsed"] = pd.to_datetime(frame["date"])

        window_start = tx_date - pd.Timedelta(days=30)
        in_window = (frame["date_parsed"] >= window_start) & (
            frame["date_parsed"] <= tx_date
        )

        savings_cats = self.cfg[
            (self.cfg["SPEND_PROFILE"] == "SAVINGS_POSITIVE")
            & (self.cfg["IS_SCORED"] == 1)
        ]["CAT_ID"].values

        window_savings = frame[in_window & frame["CAT_ID"].isin(savings_cats)]["amount"].sum()
        window_savings = max(0.0, float(window_savings))

        savings_rate_30d = window_savings / income

        target = self.RECOMMENDED_SAVINGS_RATE

        if target <= 0:
            base = 50.0
        else:
            rel = savings_rate_30d / target
            base = 100.0 * np.exp(-((rel - 1.0) ** 2) / 0.6)

        if capacity["in_distress"]:
            cash_adv_share = context_features.get("cash_adv_share", 0.0)
            fees_ratio = capacity["fees_ratio"]

            distress_index = min(
                1.0,
                (cash_adv_share * 2.5) + (fees_ratio / 0.05),
            )

            base *= (1.0 - 0.7 * distress_index)

        base = self._bounded(base, 0.0, 100.0)

        savings_pct = savings_rate_30d * 100.0

        return {
            "score": base,
            "savings_pct": savings_pct,
            "severity": self._classify_severity(base),
        }

    def score_flex_essential(self, txn_amount, capacity, all_txns, cat_id):
        income = capacity["effective_income"]
        if income <= 0:
            base = 50.0
            return {
                "score": base,
                "pct_of_income": None,
                "severity": self._classify_severity(base),
            }

        same_category = all_txns[all_txns["CAT_ID"] == cat_id]
        total_cat_spend = same_category["amount"].sum()
        share = total_cat_spend / income

        sweet_high = 0.15

        if share <= 0:
            base = 100.0
        else:
            ratio = share / max(sweet_high, 1e-9)
            base = 100.0 / (1.0 + (ratio / 2.0) ** 2)

        if capacity["in_distress"]:
            base *= 0.9

        base = self._bounded(base, 0.0, 100.0)

        return {
            "score": base,
            "pct_of_income": share * 100.0,
            "severity": self._classify_severity(base),
        }


    def score_negative_event(self, txn_amount, capacity, all_txns, cat_id):
        income = capacity["effective_income"]
        if income <= 0:
            severity_pct = 100.0
        else:
            severity_pct = (txn_amount / income) * 100.0

        negative_cats = self.cfg[
            (self.cfg["SPEND_PROFILE"] == "NEGATIVE_EVENTS")
            & (self.cfg["IS_SCORED"] == 1)
        ]["CAT_ID"].values

        negative_txns = all_txns[all_txns["CAT_ID"].isin(negative_cats)]
        frequency = max(1, len(negative_txns))

        severity_index = severity_pct * np.sqrt(frequency)

        base = 100.0 / (1.0 + np.power(severity_index, 0.8))

        if capacity["in_distress"]:
            base *= 0.7

        base = self._bounded(base, 0.0, 100.0)

        return {
            "score": base,
            "severity_pct": severity_pct,
            "frequency": frequency,
            "severity_index": severity_index,
            "severity": self._classify_severity(base),
        }

    def score_transaction(self, txn_row, all_txns, context_features):
        cat_id = int(txn_row["CAT_ID"])
        is_scored = self.cat_to_scored.get(cat_id, 0)

        if not is_scored:
            return {
                "score": None,
                "is_scored": False,
                "reason": "Category not scoreable (income / structural / non-behavioral)",
            }

        capacity = self.calculate_financial_capacity(context_features)
        txn_amount = abs(float(txn_row["amount"]))
        profile = self.cat_to_profile.get(cat_id)
        context_bucket = self.cat_to_context.get(cat_id)

        if profile == "DISCRETIONARY_WANT":
            is_harmful = context_bucket == "AVOIDABLE_HARMFUL"
            result = self.score_discretionary(
                txn_amount, capacity, context_features, is_harmful
            )

        elif profile == "SAVINGS_POSITIVE":
            result = self.score_savings(txn_row, capacity, all_txns, context_features)

        elif profile == "FLEX_ESSENTIAL":
            result = self.score_flex_essential(
                txn_amount, capacity, all_txns, cat_id
            )

        elif profile == "NEGATIVE_EVENTS":
            result = self.score_negative_event(
                txn_amount, capacity, all_txns, cat_id
            )

        else:
            result = {
                "score": 50.0,
                "severity": "unknown",
                "reason": f"Unknown SPEND_PROFILE: {profile}",
            }

        pattern_penalty = self._calculate_pattern_penalty(
            txn_row, all_txns, profile
        )
        final_score = self._bounded(result["score"] - pattern_penalty, 0.0, 100.0)

        return {
            "score": round(final_score, 2),
            "is_scored": True,
            "profile": profile,
            "context_bucket": context_bucket,
            "base_score": round(result["score"], 2),
            "pattern_penalty": round(pattern_penalty, 2),
            "capacity_info": capacity,
            "details": result,
        }

    def _calculate_pattern_penalty(self, txn_row, all_txns, profile):
        if profile != "DISCRETIONARY_WANT":
            return 0.0

        cat_id = int(txn_row["CAT_ID"])
        same_cat = all_txns[all_txns["CAT_ID"] == cat_id]
        frequency = len(same_cat)

        excess = max(0, frequency - 3)
        if excess <= 0:
            return 0.0

        max_penalty = 20.0
        k = 0.3
        penalty = max_penalty * (1.0 - np.exp(-k * excess))

        return penalty

    def _classify_severity(self, score):
        if score >= 90:
            return "very_low"
        elif score >= 70:
            return "low"
        elif score >= 50:
            return "moderate"
        elif score >= 30:
            return "high"
        else:
            return "very_high"

    def score_all_transactions(self, txns, context_features):
        results = []
        for _, row in txns.iterrows():
            results.append(
                self.score_transaction(row, txns, context_features)
            )

        scored_df = txns.copy()
        scored_df["score"] = [r["score"] for r in results]
        scored_df["is_scored"] = [r["is_scored"] for r in results]
        scored_df["base_score"] = [r.get("base_score") for r in results]
        scored_df["pattern_penalty"] = [
            r.get("pattern_penalty", 0.0) for r in results
        ]
        scored_df["profile"] = [r.get("profile") for r in results]
        scored_df["severity"] = [
            r.get("details", {}).get("severity", "unknown") for r in results
        ]
        scored_df["score_details"] = results

        return scored_df

    def get_score_summary(self, scored_df):
        scoreable = scored_df[scored_df["is_scored"] == True]
        if len(scoreable) == 0:
            return {"error": "No scoreable transactions"}

        return {
            "total_transactions": int(len(scored_df)),
            "scoreable_transactions": int(len(scoreable)),
            "average_score": float(scoreable["score"].mean().round(2)),
            "median_score": float(scoreable["score"].median().round(2)),
            "min_score": float(scoreable["score"].min().round(2)),
            "max_score": float(scoreable["score"].max().round(2)),
            "score_std": float(scoreable["score"].std().round(2)),
            "scores_by_profile": scoreable.groupby("profile")["score"]
            .agg(["mean", "count"])
            .to_dict(),
            "severity_distribution": scoreable["severity"].value_counts().to_dict(),
        }
