import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import DuplicateCandidate, AuditLog
from app.schemas import DuplicateCandidateOut, ReviewActionRequest

router = APIRouter(prefix="/api/duplicates", tags=["Duplicate Detection"])

@router.get("", response_model=List[DuplicateCandidateOut])
def get_duplicates(
    classification: Optional[str] = Query(None, description="'HIGH_CONFIDENCE', 'POSSIBLE_REVIEW', 'UNLIKELY'"),
    status: Optional[str] = Query(None, description="'PENDING', 'APPROVED', 'REJECTED'"),
    db: Session = Depends(get_db)
):
    query = db.query(DuplicateCandidate)
    if classification:
        query = query.filter(DuplicateCandidate.match_classification == classification.upper())
    if status:
        query = query.filter(DuplicateCandidate.status == status.upper())

    candidates = query.order_by(DuplicateCandidate.overall_confidence.desc()).all()
    
    # Enrich product supplier names
    for c in candidates:
        if c.product_a:
            c.product_a.supplier_name = c.product_a.supplier.name
            c.product_a.supplier_code = c.product_a.supplier.code
        if c.product_b:
            c.product_b.supplier_name = c.product_b.supplier.name
            c.product_b.supplier_code = c.product_b.supplier.code

    return candidates

@router.post("/{candidate_id}/review")
def review_duplicate(
    candidate_id: int,
    action: ReviewActionRequest,
    db: Session = Depends(get_db)
):
    candidate = db.query(DuplicateCandidate).filter(DuplicateCandidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Duplicate candidate not found")

    decision = action.decision.upper()
    if decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be 'APPROVED' or 'REJECTED'")

    candidate.status = decision
    candidate.review_notes = action.notes
    candidate.reviewed_at = datetime.datetime.utcnow()

    # Log to audit trail
    audit = AuditLog(
        action=f"REVIEW_DUPLICATE_{decision}",
        entity_type="DUPLICATE",
        entity_id=candidate.id,
        decision=decision,
        notes=action.notes,
        details={
            "product_a": candidate.product_a.name if candidate.product_a else None,
            "product_b": candidate.product_b.name if candidate.product_b else None,
            "confidence": candidate.overall_confidence
        }
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "candidate_id": candidate.id,
        "status": candidate.status,
        "reviewed_at": candidate.reviewed_at
    }

