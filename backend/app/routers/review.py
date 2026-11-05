from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.database import get_db
from app.models import DuplicateCandidate, PriceAnomalyAlert, InventoryQualityReport, AuditLog

router = APIRouter(prefix="/api/review", tags=["Human Review Center & Audit Trail"])

@router.get("/queue")
def get_unified_review_queue(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Returns all pending items needing human decision."""
    pending_duplicates = db.query(DuplicateCandidate).filter(DuplicateCandidate.status == "PENDING").all()
    pending_anomalies = db.query(PriceAnomalyAlert).filter(PriceAnomalyAlert.status == "PENDING").all()
    pending_quality = db.query(InventoryQualityReport).filter(InventoryQualityReport.status == "PENDING").all()

    dup_items = []
    for d in pending_duplicates:
        dup_items.append({
            "id": d.id,
            "type": "DUPLICATE",
            "title": f"Duplicate Match: {d.product_a.name} ↔ {d.product_b.name}",
            "supplier_a": d.product_a.supplier.name,
            "supplier_b": d.product_b.supplier.name,
            "confidence": d.overall_confidence,
            "classification": d.match_classification,
            "evidence": d.evidence_breakdown,
            "product_a": {
                "name": d.product_a.name,
                "price": d.product_a.base_price,
                "room_or_activity": d.product_a.room_category or d.product_a.activity_type
            },
            "product_b": {
                "name": d.product_b.name,
                "price": d.product_b.base_price,
                "room_or_activity": d.product_b.room_category or d.product_b.activity_type
            }
        })

    anom_items = []
    for a in pending_anomalies:
        anom_items.append({
            "id": a.id,
            "type": "ANOMALY",
            "title": f"Price Anomaly: {a.product.name}",
            "supplier": a.product.supplier.name,
            "observed_price": a.observed_price,
            "baseline_price": a.baseline_price,
            "diff_pct": a.price_diff_pct,
            "severity": a.severity,
            "explanation": a.explanation,
            "detection_method": a.detection_method
        })

    qual_items = []
    for q in pending_quality:
        if q.completeness_score < 0.80 or len(q.enrichment_suggestions) > 0:
            qual_items.append({
                "id": q.id,
                "type": "QUALITY",
                "title": f"Content Quality: {q.product.name}",
                "supplier": q.product.supplier.name,
                "completeness_score": q.completeness_score,
                "missing_fields": q.missing_fields,
                "suggestions": q.enrichment_suggestions
            })

    return {
        "pending_duplicates": dup_items,
        "pending_anomalies": anom_items,
        "pending_quality": qual_items,
        "total_pending_count": len(dup_items) + len(anom_items) + len(qual_items)
    }

@router.get("/audit-trail")
def get_audit_trail(
    limit: int = Query(50),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    results = []
    for log in logs:
        results.append({
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "decision": log.decision,
            "notes": log.notes,
            "details": log.details,
            "created_at": log.created_at.isoformat()
        })
    return results

