import numpy as np
import logging
from typing import List, Dict, Any, Optional
from sklearn.ensemble import IsolationForest

logger = logging.getLogger(__name__)

class PriceAnomalyEngine:
    def __init__(self, zscore_threshold: float = 2.0, iqr_multiplier: float = 1.5):
        self.zscore_threshold = zscore_threshold
        self.iqr_multiplier = iqr_multiplier

    def detect_group_anomalies(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes a group of comparable products (e.g. same hotel or same experience cluster across suppliers).
        Applies:
        - Baseline median & IQR thresholds
        - Z-Score standardization
        - Isolation Forest (when cluster size >= 4)
        """
        if not products or len(products) < 2:
            return []

        prices = [float(p["base_price"]) for p in products if p.get("base_price") is not None and p.get("base_price") > 0]
        if len(prices) < 2:
            return []

        arr = np.array(prices)
        median_price = float(np.median(arr))
        mean_price = float(np.mean(arr))
        std_price = float(np.std(arr)) if len(arr) > 1 else 0.0

        q25 = float(np.percentile(arr, 25))
        q75 = float(np.percentile(arr, 75))
        iqr = q75 - q25
        lower_bound = max(5.0, q25 - (self.iqr_multiplier * iqr))
        upper_bound = q75 + (self.iqr_multiplier * iqr)

        # Isolation forest model fit if enough sample points
        iso_forest = None
        if len(prices) >= 4:
            try:
                iso_forest = IsolationForest(contamination=0.25, random_state=42)
                iso_forest.fit(arr.reshape(-1, 1))
            except Exception as e:
                logger.warning(f"Isolation Forest initialization skipped: {e}")

        anomalies = []

        for p in products:
            p_price = float(p.get("base_price", 0.0))
            if p_price <= 0:
                continue

            diff_from_median_pct = ((p_price - median_price) / median_price) * 100.0 if median_price > 0 else 0.0
            z_score = abs((p_price - mean_price) / std_price) if std_price > 0.01 else 0.0

            # Determine anomaly triggers
            is_anomaly = False
            method_used = "IQR Statistical Analysis"
            anomaly_type = "NORMAL"
            severity = "LOW"
            explanation = ""

            # Check IQR bounds
            if p_price > upper_bound or diff_from_median_pct > 35.0:
                is_anomaly = True
                anomaly_type = "HIGH_PRICE"
                severity = "HIGH" if diff_from_median_pct > 60.0 else "MEDIUM"
                explanation = (
                    f"Observed price of ${p_price:.2f} is {diff_from_median_pct:+.1f}% above cluster median (${median_price:.2f}). "
                    f"Possible rate parity violation, erroneous currency conversion, or unbundled luxury markup."
                )
            elif p_price < lower_bound or diff_from_median_pct < -30.0:
                is_anomaly = True
                anomaly_type = "LOW_PRICE"
                severity = "HIGH" if diff_from_median_pct < -50.0 else "MEDIUM"
                explanation = (
                    f"Observed price of ${p_price:.2f} is {abs(diff_from_median_pct):.1f}% below cluster median (${median_price:.2f}). "
                    f"Potential bait pricing, missing mandatory resort fees/taxes, or erroneous contract entry."
                )

            # Cross-check Z-Score
            if z_score >= self.zscore_threshold and not is_anomaly:
                is_anomaly = True
                method_used = "Z-Score Standardization"
                anomaly_type = "HIGH_PRICE" if p_price > mean_price else "LOW_PRICE"
                severity = "HIGH" if z_score > 2.5 else "MEDIUM"
                explanation = f"Price deviates by {z_score:.2f} standard deviations from peer mean (${mean_price:.2f})."

            # Check Isolation Forest
            if iso_forest is not None and not is_anomaly:
                pred = iso_forest.predict([[p_price]])[0]
                if pred == -1: # Outlier detected by Isolation Forest
                    is_anomaly = True
                    method_used = "Isolation Forest Outlier Model"
                    anomaly_type = "SUPPLIER_DISPARITY"
                    severity = "MEDIUM"
                    explanation = f"Unsupervised Isolation Forest flagged rate ${p_price:.2f} as an outlier in the supplier distribution."

            # Check for currency mismatch or missing tax warning
            currency = p.get("currency", "USD")
            if currency != "USD" and not is_anomaly:
                is_anomaly = True
                anomaly_type = "CURRENCY_INCONSISTENCY"
                method_used = "Multi-Currency Rule Engine"
                severity = "LOW"
                explanation = f"Product is priced in {currency} while peer cluster is indexed in USD. Currency normalization advised."

            if is_anomaly:
                anomalies.append({
                    "product_id": p.get("id"),
                    "observed_price": round(p_price, 2),
                    "baseline_price": round(median_price, 2),
                    "price_diff_pct": round(diff_from_median_pct, 1),
                    "anomaly_type": anomaly_type,
                    "detection_method": method_used,
                    "severity": severity,
                    "explanation": explanation
                })

        return anomalies

price_engine = PriceAnomalyEngine()

