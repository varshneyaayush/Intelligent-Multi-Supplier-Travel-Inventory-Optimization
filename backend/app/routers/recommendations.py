from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import OptimizationRecommendation, AuditLog
from app.schemas import RecommendationOut, ReviewActionRequest

router = APIRouter(prefix="/api/recommendations", tags=["Optimization Recommendations"])

@router.get("", response_model=List[RecommendationOut])
def get_recommendations(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(OptimizationRecommendation)
    if category:
        query = query.filter(OptimizationRecommendation.category == category.upper())
    if status:
        query = query.filter(OptimizationRecommendation.status == status.upper())

    return query.order_by(OptimizationRecommendation.id.asc()).all()

@router.post("/{rec_id}/action")
def update_recommendation(
    rec_id: int,
    action: ReviewActionRequest,
    db: Session = Depends(get_db)
):
    rec = db.query(OptimizationRecommendation).filter(OptimizationRecommendation.id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    decision = action.decision.upper()
    if decision not in ["APPLIED", "DISMISSED", "ACTIVE"]:
        raise HTTPException(status_code=400, detail="Decision must be 'APPLIED', 'DISMISSED', or 'ACTIVE'")

    rec.status = decision
    audit = AuditLog(
        action=f"RECOMMENDATION_{decision}",
        entity_type="RECOMMENDATION",
        entity_id=rec.id,
        decision=decision,
        notes=action.notes,
        details={"title": rec.title, "category": rec.category}
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "recommendation_id": rec.id,
        "status": rec.status
    }

