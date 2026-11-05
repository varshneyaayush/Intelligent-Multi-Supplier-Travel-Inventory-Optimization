from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.database import get_db
from app.models import (
    InventoryProduct, Supplier, DuplicateCandidate, PriceAnomalyAlert,
    InventoryQualityReport, OptimizationRecommendation, SupplierMetric
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Insights"])

@router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    total_inventory = db.query(InventoryProduct).count()
    hotel_records = db.query(InventoryProduct).filter(InventoryProduct.product_type == "HOTEL").count()
    sightseeing_records = db.query(InventoryProduct).filter(InventoryProduct.product_type == "SIGHTSEEING").count()
    suppliers_count = db.query(Supplier).count()

    # Duplicates breakdown
    total_duplicates = db.query(DuplicateCandidate).count()
    high_conf_duplicates = db.query(DuplicateCandidate).filter(DuplicateCandidate.match_classification == "HIGH_CONFIDENCE").count()
    possible_review_duplicates = db.query(DuplicateCandidate).filter(DuplicateCandidate.match_classification == "POSSIBLE_REVIEW").count()
    pending_duplicates = db.query(DuplicateCandidate).filter(DuplicateCandidate.status == "PENDING").count()
    approved_duplicates = db.query(DuplicateCandidate).filter(DuplicateCandidate.status == "APPROVED").count()

    # Price Anomalies breakdown
    total_anomalies = db.query(PriceAnomalyAlert).count()
    pending_anomalies = db.query(PriceAnomalyAlert).filter(PriceAnomalyAlert.status == "PENDING").count()
    high_severity_anomalies = db.query(PriceAnomalyAlert).filter(PriceAnomalyAlert.severity == "HIGH").count()
    medium_severity_anomalies = db.query(PriceAnomalyAlert).filter(PriceAnomalyAlert.severity == "MEDIUM").count()

    # Quality completeness distribution
    quality_reports = db.query(InventoryQualityReport).all()
    quality_dist = {"90_100": 0, "75_89": 0, "50_74": 0, "below_50": 0}
    for q in quality_reports:
        score = q.completeness_score * 100.0
        if score >= 90:
            quality_dist["90_100"] += 1
        elif score >= 75:
            quality_dist["75_89"] += 1
        elif score >= 50:
            quality_dist["50_74"] += 1
        else:
            quality_dist["below_50"] += 1

    # Supplier Trust Leaderboard
    suppliers = db.query(Supplier).all()
    supplier_leaderboard = []
    for s in suppliers:
        metric = s.metrics
        supplier_leaderboard.append({
            "supplier_id": s.id,
            "supplier_name": s.name,
            "supplier_code": s.code,
            "trust_score": metric.trust_score if metric else 75.0,
            "price_competitiveness": metric.price_competitiveness if metric else 80.0,
            "booking_success_rate": metric.booking_success_rate if metric else 90.0,
            "availability_accuracy": metric.availability_accuracy if metric else 88.0,
            "data_completeness": metric.data_completeness if metric else 85.0,
            "product_count": len(s.products)
        })
    supplier_leaderboard.sort(key=lambda x: x["trust_score"], reverse=True)

    # Active Recommendations
    active_recs = db.query(OptimizationRecommendation).filter(OptimizationRecommendation.status == "ACTIVE").count()

    # Total pending human review tasks
    pending_human_reviews = pending_duplicates + pending_anomalies

    # Average price per product type
    avg_hotel_price = db.query(func.avg(InventoryProduct.base_price)).filter(InventoryProduct.product_type == "HOTEL").scalar() or 0.0
    avg_sightseeing_price = db.query(func.avg(InventoryProduct.base_price)).filter(InventoryProduct.product_type == "SIGHTSEEING").scalar() or 0.0

    return {
        "kpis": {
            "total_inventory": total_inventory,
            "hotel_records": hotel_records,
            "sightseeing_records": sightseeing_records,
            "suppliers_analyzed": suppliers_count,
            "potential_duplicate_groups": total_duplicates,
            "high_confidence_matches": high_conf_duplicates,
            "possible_review_matches": possible_review_duplicates,
            "pending_human_reviews": pending_human_reviews,
            "price_anomaly_alerts": total_anomalies,
            "active_recommendations": active_recs,
            "avg_hotel_price": round(float(avg_hotel_price), 2),
            "avg_sightseeing_price": round(float(avg_sightseeing_price), 2)
        },
        "quality_distribution": [
            {"tier": "Excellent (90-100%)", "count": quality_dist["90_100"], "fill": "#590907"},
            {"tier": "Good (75-89%)", "count": quality_dist["75_89"], "fill": "#8E9084"},
            {"tier": "Fair (50-74%)", "count": quality_dist["50_74"], "fill": "#D2AD7D"},
            {"tier": "Needs Attention (<50%)", "count": quality_dist["below_50"], "fill": "#CB4A47"},
        ],
        "anomaly_distribution": [
            {"name": "High Severity", "value": high_severity_anomalies, "color": "#590907"},
            {"name": "Medium Severity", "value": medium_severity_anomalies, "color": "#DEC099"},
            {"name": "Resolved / Normal", "value": total_anomalies - pending_anomalies, "color": "#A5A79B"},
        ],
        "supplier_leaderboard": supplier_leaderboard,
        "sample_indicator": "Sample Data Benchmark (VOYAGEHACK 4.0 Demonstration)"
    }

