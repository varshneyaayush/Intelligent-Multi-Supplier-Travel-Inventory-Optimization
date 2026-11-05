import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import PriceAnomalyAlert, AuditLog
from app.schemas import PriceAnomalyOut, ReviewActionRequest

router = APIRouter(prefix="/api/anomalies", tags=["Price Anomaly Detection"])

@router.get("", response_model=List[PriceAnomalyOut])
def get_anomalies(
    severity: Optional[str] = Query(None, description="'HIGH', 'MEDIUM', 'LOW'"),
    status: Optional[str] = Query(None, description="'PENDING', 'DISMISSED', 'RESOLVED'"),
    anomaly_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(PriceAnomalyAlert)
    if severity:
        query = query.filter(PriceAnomalyAlert.severity == severity.upper())
    if status:
        query = query.filter(PriceAnomalyAlert.status == status.upper())
    if anomaly_type:
        query = query.filter(PriceAnomalyAlert.anomaly_type == anomaly_type.upper())

    alerts = query.order_by(PriceAnomalyAlert.price_diff_pct.desc()).all()
    for a in alerts:
        if a.product:
            a.product.supplier_name = a.product.supplier.name
            a.product.supplier_code = a.product.supplier.code
    return alerts

@router.post("/{alert_id}/review")
def review_anomaly(
    alert_id: int,
    action: ReviewActionRequest,
    db: Session = Depends(get_db)
):
    alert = db.query(PriceAnomalyAlert).filter(PriceAnomalyAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Price anomaly alert not found")

    decision = action.decision.upper()
    if decision not in ["RESOLVED", "DISMISSED"]:
        raise HTTPException(status_code=400, detail="Decision must be 'RESOLVED' or 'DISMISSED'")

    alert.status = decision
    alert.reviewed_at = datetime.datetime.utcnow()

    audit = AuditLog(
        action=f"REVIEW_ANOMALY_{decision}",
        entity_type="ANOMALY",
        entity_id=alert.id,
        decision=decision,
        notes=action.notes,
        details={
            "product_name": alert.product.name if alert.product else None,
            "observed_price": alert.observed_price,
            "baseline_price": alert.baseline_price,
            "diff_pct": alert.price_diff_pct
        }
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "alert_id": alert.id,
        "status": alert.status,
        "reviewed_at": alert.reviewed_at
    }

