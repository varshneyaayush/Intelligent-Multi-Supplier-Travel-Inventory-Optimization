import logging
from typing import List, Dict, Any, Optional
from ai.ranking_engine import RankingEngine

logger = logging.getLogger(__name__)

class SimulationEngine:
    def __init__(self):
        self.ranking_engine = RankingEngine()

    def simulate_scenario(
        self,
        products: List[Dict[str, Any]],
        scenario_name: str,
        excluded_supplier_ids: List[int] = None,
        weight_adjustments: Dict[str, float] = None,
        max_price_cap: Optional[float] = None,
        require_free_cancellation: bool = False
    ) -> Dict[str, Any]:
        """
        Runs What-If scenario simulation on the current inventory universe.
        Labels all outcomes transparently as algorithmic projections.
        """
        excluded_suppliers = set(excluded_supplier_ids or [])
        
        # 1. Baseline Ranking (All active products with default weights)
        baseline_ranked = self.ranking_engine.rank_products(products)
        baseline_top10 = baseline_ranked[:10]
        baseline_avg_price = (
            sum(p["base_price"] for p in baseline_top10) / len(baseline_top10)
            if baseline_top10 else 0.0
        )
        baseline_avg_trust = (
            sum(p["score_breakdown"]["trust_score"] for p in baseline_top10) / len(baseline_top10)
            if baseline_top10 else 0.0
        )

        # 2. Filter products according to scenario rules
        simulated_universe = []
        for p in products:
            # Check excluded suppliers
            if p.get("supplier_id") in excluded_suppliers:
                continue

            # Check price cap
            if max_price_cap is not None and float(p.get("base_price", 0)) > max_price_cap:
                continue

            # Check cancellation policy requirement
            if require_free_cancellation:
                pol = str(p.get("cancellation_policy") or "").lower()
                if "free" not in pol:
                    continue

            simulated_universe.append(p)

        # 3. Simulated Ranking with adjusted weights
        simulated_ranked = self.ranking_engine.rank_products(
            simulated_universe,
            weights=weight_adjustments
        )
        simulated_top10 = simulated_ranked[:10]

        sim_avg_price = (
            sum(p["base_price"] for p in simulated_top10) / len(simulated_top10)
            if simulated_top10 else 0.0
        )
        sim_avg_trust = (
            sum(p["score_breakdown"]["trust_score"] for p in simulated_top10) / len(simulated_top10)
            if simulated_top10 else 0.0
        )

        # 4. Map Rank Shifts
        baseline_rank_map = {p["product_id"]: p["rank"] for p in baseline_ranked}
        rank_shifts = []

        for p in simulated_top10:
            pid = p["product_id"]
            base_rank = baseline_rank_map.get(pid)
            sim_rank = p["rank"]
            shift = (base_rank - sim_rank) if base_rank is not None else 99
            
            rank_shifts.append({
                "product_id": pid,
                "product_name": p["product_name"],
                "supplier_name": p["supplier_name"],
                "base_price": p["base_price"],
                "baseline_rank": base_rank,
                "simulated_rank": sim_rank,
                "rank_delta": shift,
                "status": "Advanced" if shift > 0 else ("Declined" if shift < 0 else "Unchanged")
            })

        # 5. Generate transparent trade-off analysis
        trade_offs = []
        price_diff = sim_avg_price - baseline_avg_price
        trust_diff = sim_avg_trust - baseline_avg_trust

        if excluded_suppliers:
            trade_offs.append(
                f"Excluding {len(excluded_suppliers)} supplier(s) reduced inventory pool from {len(products)} to {len(simulated_universe)} options."
            )

        if require_free_cancellation:
            trade_offs.append(
                "Restricting to Free Cancellation guarantees customer flexibility but filtered out restricted budget-saver rates."
            )

        if price_diff < 0:
            trade_offs.append(
                f"Simulated top selections achieve a projected ${abs(price_diff):.2f} average price reduction per booking."
            )
        elif price_diff > 0:
            trade_offs.append(
                f"Shift in parameters yields a +${price_diff:.2f} higher average booking rate in exchange for improved trust or flexibility."
            )

        if trust_diff > 0:
            trade_offs.append(
                f"Average supplier trust score improved by +{trust_diff:.1f} points among top recommendations."
            )
        elif trust_diff < 0:
            trade_offs.append(
                f"Trade-off: Average supplier trust rating dipped by {abs(trust_diff):.1f} points to capture price savings."
            )

        return {
            "scenario_name": scenario_name,
            "disclaimer": "All simulated metrics represent theoretical heuristic projections based on current inventory state. These projections do not constitute financial guarantees.",
            "baseline_summary": {
                "total_products": len(products),
                "top_avg_price": round(baseline_avg_price, 2),
                "top_avg_trust": round(baseline_avg_trust, 1),
                "top_10": baseline_top10
            },
            "simulated_summary": {
                "eligible_products": len(simulated_universe),
                "top_avg_price": round(sim_avg_price, 2),
                "top_avg_trust": round(sim_avg_trust, 1),
                "top_10": simulated_top10
            },
            "rank_shifts": rank_shifts,
            "trade_off_analysis": trade_offs,
            "projected_impact": {
                "price_delta": round(price_diff, 2),
                "trust_delta": round(trust_diff, 1),
                "inventory_reduction_pct": round(
                    ((len(products) - len(simulated_universe)) / len(products)) * 100.0, 1
                ) if len(products) > 0 else 0.0
            }
        }

simulation_engine = SimulationEngine()

