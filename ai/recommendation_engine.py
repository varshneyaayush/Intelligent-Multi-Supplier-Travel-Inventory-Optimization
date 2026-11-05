import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def generate_recommendations(
        self,
        duplicates: List[Dict[str, Any]],
        anomalies: List[Dict[str, Any]],
        suppliers: List[Dict[str, Any]],
        quality_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Synthesizes actual database findings into actionable, explainable inventory recommendations.
        """
        recs = []

        # 1. Duplicate Consolidation Recommendations
        high_conf_dups = [d for d in duplicates if d.get("match_classification") == "HIGH_CONFIDENCE" and d.get("status") == "PENDING"]
        if high_conf_dups:
            dup_pairs = len(high_conf_dups)
            sample_dup = high_conf_dups[0]
            name_a = sample_dup.get("product_a", {}).get("name", "Listing A")
            name_b = sample_dup.get("product_b", {}).get("name", "Listing B")
            supp_a = sample_dup.get("product_a", {}).get("supplier_name", "Supplier A")
            supp_b = sample_dup.get("product_b", {}).get("supplier_name", "Supplier B")
            
            recs.append({
                "category": "DUPLICATE_CONSOLIDATION",
                "title": f"Consolidate {dup_pairs} High-Confidence Duplicate Listing Groups",
                "recommendation": (
                    f"Approve automated mapping and canonical consolidation for identified duplicate pairs, "
                    f"such as '{name_a}' ({supp_a}) and '{name_b}' ({supp_b})."
                ),
                "why_recommended": (
                    f"Multi-modal AI detection verified {round(sample_dup.get('overall_confidence', 0.9)*100)}% identity alignment "
                    f"across exact geo-location and property naming conventions. Consolidating reduces customer confusion and double bookings."
                ),
                "supporting_evidence": {
                    "pending_high_confidence_pairs": dup_pairs,
                    "sample_lead_pair": f"{name_a} ↔ {name_b}",
                    "confidence_score": sample_dup.get("overall_confidence"),
                    "geo_distance_meters": sample_dup.get("geo_distance_meters")
                },
                "expected_benefit": "Eliminates duplicate inventory display on consumer frontends; unlocks cross-supplier price arbitrage.",
                "confidence_level": "High (Verified by multi-modal ensemble)",
                "status": "ACTIVE"
            })

        # 2. Price Disparity & Rate Parity Recommendations
        high_anomalies = [a for a in anomalies if a.get("severity") == "HIGH" and a.get("status") == "PENDING"]
        if high_anomalies:
            sample_anom = high_anomalies[0]
            prod = sample_anom.get("product", {})
            diff = sample_anom.get("price_diff_pct", 0)
            obs = sample_anom.get("observed_price", 0)
            base = sample_anom.get("baseline_price", 0)
            
            recs.append({
                "category": "PRICE_OPTIMIZATION",
                "title": f"Investigate {len(high_anomalies)} Severe Price Disparities Across Suppliers",
                "recommendation": (
                    f"Review supplier contract rates for '{prod.get('name', 'Hotel Listing')}' where rate of ${obs:.2f} "
                    f"diverges by {diff:+.1f}% from the cluster baseline of ${base:.2f}."
                ),
                "why_recommended": (
                    f"Statistical IQR and Z-Score outlier detection identified substantial cross-supplier price divergence. "
                    f"Could indicate unapplied promotional margin or missing mandatory taxes."
                ),
                "supporting_evidence": {
                    "total_severe_alerts": len(high_anomalies),
                    "product_name": prod.get("name"),
                    "observed_price": obs,
                    "baseline_price": base,
                    "variance_percentage": diff
                },
                "expected_benefit": "Prevents margin erosion on overpriced supplier listings and flags contractual under-pricing risks.",
                "confidence_level": "High (Confirmed by statistical variance models)",
                "status": "ACTIVE"
            })

        # 3. Supplier Trust Rebalancing Recommendations
        low_trust_suppliers = [
            s for s in suppliers 
            if s.get("metrics") and s["metrics"].get("trust_score", 100) < 75.0
        ]
        if low_trust_suppliers:
            target_sup = low_trust_suppliers[0]
            sup_name = target_sup.get("name", "Partner")
            trust = target_sup["metrics"].get("trust_score", 65.0)
            recs.append({
                "category": "SUPPLIER_REBALANCING",
                "title": f"Rebalance Order Allocation for {sup_name} (Trust Score: {trust}/100)",
                "recommendation": (
                    f"Temporarily depress priority ranking for {sup_name} or route bookings to higher-scoring alternate suppliers "
                    f"until fulfillment SLAs improve."
                ),
                "why_recommended": (
                    f"{sup_name} exhibits lower trust metrics due to availability drop-offs or higher cancellation dispute rates. "
                    f"Identified weak points: {', '.join(target_sup['metrics'].get('weaknesses', ['Operational latency'])[:2])}."
                ),
                "supporting_evidence": {
                    "supplier_code": target_sup.get("code"),
                    "trust_score": trust,
                    "weaknesses": target_sup["metrics"].get("weaknesses", [])
                },
                "expected_benefit": "Reduces downstream booking cancellation disputes and safeguards platform NPS.",
                "confidence_level": "High (Grounded in supplier metrics)",
                "status": "ACTIVE"
            })

        # 4. Content Enrichment Opportunities
        low_quality = [q for q in quality_issues if q.get("completeness_score", 1.0) < 0.70]
        if low_quality:
            sample_q = low_quality[0]
            recs.append({
                "category": "CONTENT_ENRICHMENT",
                "title": f"Enrich Metadata for {len(low_quality)} Incomplete Inventory Listings",
                "recommendation": (
                    f"Execute automated attribute extraction for incomplete listings missing geo-coordinates, "
                    f"amenities, or duration details."
                ),
                "why_recommended": (
                    f"Listings with missing attributes experience lower conversion and search visibility. "
                    f"{len(low_quality)} products have completeness scores below 70%."
                ),
                "supporting_evidence": {
                    "incomplete_records_count": len(low_quality),
                    "sample_missing_fields": sample_q.get("missing_fields", [])
                },
                "expected_benefit": "Boosts search discoverability, filters match rate, and traveler booking confidence.",
                "confidence_level": "High (Direct field audit)",
                "status": "ACTIVE"
            })

        # Fallback if inventory is pristine
        if not recs:
            recs.append({
                "category": "MONITORING",
                "title": "Inventory Optimization Baseline Stable",
                "recommendation": "Maintain continuous multi-supplier ingestion monitoring. No critical anomalies or unresolved duplicates detected.",
                "why_recommended": "All supplier feeds currently meet quality standards and match thresholds.",
                "supporting_evidence": {"status": "Nominal"},
                "expected_benefit": "Sustained booking conversion and high availability compliance.",
                "confidence_level": "High",
                "status": "ACTIVE"
            })

        return recs

recommendation_engine = RecommendationEngine()

