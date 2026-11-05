import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SupplierIntelligenceEngine:
    DEFAULT_WEIGHTS = {
        "price_competitiveness": 0.25,
        "booking_success_rate": 0.25,
        "availability_accuracy": 0.20,
        "cancellation_reliability": 0.15,
        "data_completeness": 0.15
    }

    def compute_trust_score(
        self,
        metrics: Dict[str, Any],
        custom_weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculates transparent, explainable supplier trust scores.
        Weights sum to 1.0.
        """
        weights = custom_weights or self.DEFAULT_WEIGHTS

        p_comp = float(metrics.get("price_competitiveness", 75.0))
        b_succ = float(metrics.get("booking_success_rate", 90.0))
        a_acc = float(metrics.get("availability_accuracy", 88.0))
        c_rel = float(metrics.get("cancellation_reliability", 85.0))
        d_comp = float(metrics.get("data_completeness", 80.0))
        r_time = float(metrics.get("response_time_ms", 300.0))

        # Trust score weighted linear sum
        trust_score = (
            p_comp * weights.get("price_competitiveness", 0.25) +
            b_succ * weights.get("booking_success_rate", 0.25) +
            a_acc * weights.get("availability_accuracy", 0.20) +
            c_rel * weights.get("cancellation_reliability", 0.15) +
            d_comp * weights.get("data_completeness", 0.15)
        )
        
        # Penalize if response time is exceptionally slow (> 1500ms)
        if r_time > 1500:
            trust_score = max(10.0, trust_score - 10.0)
        elif r_time > 800:
            trust_score = max(10.0, trust_score - 5.0)

        trust_score = round(trust_score, 1)

        # Generate strengths & weaknesses dynamically
        strengths = []
        weaknesses = []

        if p_comp >= 88:
            strengths.append(f"High price competitiveness ({p_comp:.0f}/100) provides strong margin potential.")
        elif p_comp < 70:
            weaknesses.append(f"Uncompetitive baseline pricing ({p_comp:.0f}/100) compared to peer suppliers.")

        if b_succ >= 95:
            strengths.append(f"Exceptional booking fulfillment rate ({b_succ:.1f}%).")
        elif b_succ < 85:
            weaknesses.append(f"Suboptimal booking confirmation success ({b_succ:.1f}%).")

        if a_acc >= 92:
            strengths.append(f"High real-time inventory availability accuracy ({a_acc:.1f}%).")
        elif a_acc < 80:
            weaknesses.append(f"Higher risk of stale inventory availability ({a_acc:.1f}%).")

        if c_rel >= 90:
            strengths.append("Favorable and reliable cancellation fulfillment policies.")
        elif c_rel < 75:
            weaknesses.append("Restrictive cancellation terms or higher dispute frequencies.")

        if d_comp >= 90:
            strengths.append("Rich product metadata with comprehensive descriptions and geo-coordinates.")
        elif d_comp < 75:
            weaknesses.append(f"Sparse inventory attributes ({d_comp:.0f}% completeness score).")

        if r_time <= 250:
            strengths.append(f"Ultra-fast API response times ({r_time:.0f}ms avg).")
        elif r_time >= 800:
            weaknesses.append(f"Elevated API latency ({r_time:.0f}ms avg) may impact checkout speed.")

        if not strengths:
            strengths.append("Balanced baseline performance across standard travel distribution metrics.")
        if not weaknesses:
            weaknesses.append("No critical operational defects detected in available benchmarks.")

        tier = "Tier 1 (Preferred)" if trust_score >= 85 else ("Tier 2 (Standard)" if trust_score >= 70 else "Tier 3 (Under Review)")

        return {
            "trust_score": trust_score,
            "tier": tier,
            "score_breakdown": {
                "price_competitiveness": p_comp,
                "booking_success_rate": b_succ,
                "availability_accuracy": a_acc,
                "cancellation_reliability": c_rel,
                "data_completeness": d_comp,
                "response_time_ms": r_time,
                "weights_applied": weights
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "is_synthetic": metrics.get("is_synthetic", True),
            "data_coverage_note": "Evaluated against multi-supplier benchmark indices. Clearly marked as synthetic simulation data for hackathon demonstration."
        }

supplier_engine = SupplierIntelligenceEngine()

