import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RankingEngine:
    def rank_products(
        self,
        products: List[Dict[str, Any]],
        weights: Dict[str, float] = None
    ) -> List[Dict[str, Any]]:
        """
        Ranks comparable products based on multi-criteria utility function.
        Weights:
        - price_weight: ~0.30
        - trust_weight: ~0.25
        - availability_weight: ~0.15
        - quality_weight: ~0.15
        - cancellation_weight: ~0.15
        """
        if not products:
            return []

        w = weights or {
            "price_weight": 0.30,
            "trust_weight": 0.25,
            "availability_weight": 0.15,
            "quality_weight": 0.15,
            "cancellation_weight": 0.15
        }

        # Normalize weights so they sum to 1.0
        total_w = sum(w.values()) or 1.0
        norm_w = {k: v / total_w for k, v in w.items()}

        # Find min and max prices for normalization
        prices = [float(p.get("base_price", 100.0)) for p in products]
        min_p = min(prices) if prices else 1.0
        max_p = max(prices) if prices else 1.0

        scored_items = []

        for p in products:
            price = float(p.get("base_price", 100.0))
            
            # 1. Price Score: Lower is better (inverted min-max, or 100 if price == min)
            if max_p == min_p:
                price_score = 100.0
            else:
                price_score = 100.0 - (((price - min_p) / (max_p - min_p)) * 70.0)
            price_score = max(10.0, min(100.0, price_score))

            # 2. Supplier Trust Score (from metrics or default 80.0)
            trust_score = float(p.get("supplier_trust_score", 80.0))

            # 3. Availability Score
            avail = (p.get("availability_status") or "").lower()
            if "available" in avail or "instant" in avail:
                avail_score = 95.0
            elif "limited" in avail:
                avail_score = 70.0
            else:
                avail_score = 40.0

            # 4. Product Quality Score (data completeness & star rating / review)
            quality_score = float(p.get("data_completeness_score", 0.85)) * 100.0
            if p.get("star_rating"):
                star_bonus = (float(p["star_rating"]) / 5.0) * 15.0
                quality_score = min(100.0, quality_score * 0.85 + star_bonus)

            # 5. Cancellation Flexibility Score
            policy = (p.get("cancellation_policy") or "").lower()
            if "free" in policy:
                cancel_score = 95.0
            elif "partial" in policy or "flexible" in policy:
                cancel_score = 75.0
            elif "moderate" in policy:
                cancel_score = 65.0
            else:
                cancel_score = 35.0 # Non-refundable

            # Calculate overall utility score
            overall = (
                price_score * norm_w.get("price_weight", 0.30) +
                trust_score * norm_w.get("trust_weight", 0.25) +
                avail_score * norm_w.get("availability_weight", 0.15) +
                quality_score * norm_w.get("quality_weight", 0.15) +
                cancel_score * norm_w.get("cancellation_weight", 0.15)
            )

            # Build human-explainable rationale & trade-offs
            trade_offs = []
            if price > min_p:
                diff = price - min_p
                trade_offs.append(f"${diff:.2f} premium over cheapest option")
            else:
                trade_offs.append("Lowest available baseline rate")

            if trust_score >= 88:
                trade_offs.append("Top-tier supplier reliability")
            elif trust_score < 75:
                trade_offs.append("Lower supplier trust rating")

            if cancel_score >= 90:
                trade_offs.append("Zero cancellation risk (Free Cancellation)")
            elif cancel_score <= 40:
                trade_offs.append("Non-refundable booking terms")

            explanation = (
                f"Ranked with overall optimization index of {overall:.1f}/100. "
                f"Balances a price index of {price_score:.0f}/100 with supplier trust of {trust_score:.0f}/100 "
                f"and cancellation flexibility score of {cancel_score:.0f}/100."
            )

            scored_items.append({
                "product_id": p.get("id"),
                "product_name": p.get("name"),
                "product_type": p.get("product_type"),
                "supplier_name": p.get("supplier_name", "Unknown"),
                "supplier_code": p.get("supplier_code", "UNK"),
                "supplier_trust_score": trust_score,
                "base_price": price,
                "star_rating": p.get("star_rating"),
                "room_or_activity": p.get("room_category") or p.get("activity_type") or "Standard",
                "cancellation_policy": p.get("cancellation_policy", "Standard"),
                "availability_status": p.get("availability_status", "Available"),
                "overall_score": round(overall, 1),
                "score_breakdown": {
                    "price_score": round(price_score, 1),
                    "trust_score": round(trust_score, 1),
                    "availability_score": round(avail_score, 1),
                    "quality_score": round(quality_score, 1),
                    "cancellation_score": round(cancel_score, 1),
                },
                "explanation": explanation,
                "trade_offs": trade_offs
            })

        # Sort descending by overall score
        scored_items.sort(key=lambda x: x["overall_score"], reverse=True)
        for idx, item in enumerate(scored_items):
            item["rank"] = idx + 1

        return scored_items

ranking_engine = RankingEngine()

