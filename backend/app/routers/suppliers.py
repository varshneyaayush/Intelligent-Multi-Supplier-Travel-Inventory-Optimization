from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models import Supplier, SupplierMetric
from app.schemas import SupplierOut
from app.ai.supplier_intelligence import supplier_engine

router = APIRouter(prefix="/api/suppliers", tags=["Supplier Intelligence"])

@router.get("", response_model=List[SupplierOut])
def get_suppliers(db: Session = Depends(get_db)):
    suppliers = db.query(Supplier).all()
    return suppliers

@router.post("/{supplier_id}/recalculate-trust")
def recalculate_trust(
    supplier_id: int,
    custom_weights: Dict[str, float] = Body(None),
    db: Session = Depends(get_db)
):
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier or not supplier.metrics:
        raise HTTPException(status_code=404, detail="Supplier metrics not found")

    metric_dict = {
        "price_competitiveness": supplier.metrics.price_competitiveness,
        "booking_success_rate": supplier.metrics.booking_success_rate,
        "availability_accuracy": supplier.metrics.availability_accuracy,
        "cancellation_reliability": supplier.metrics.cancellation_reliability,
        "data_completeness": supplier.metrics.data_completeness,
        "response_time_ms": supplier.metrics.response_time_ms,
        "is_synthetic": supplier.metrics.is_synthetic
    }

    eval_result = supplier_engine.compute_trust_score(metric_dict, custom_weights)
    supplier.metrics.trust_score = eval_result["trust_score"]
    supplier.metrics.score_breakdown = eval_result["score_breakdown"]
    supplier.metrics.strengths = eval_result["strengths"]
    supplier.metrics.weaknesses = eval_result["weaknesses"]
    db.commit()

    return {
        "supplier_id": supplier.id,
        "supplier_name": supplier.name,
        "trust_score": eval_result["trust_score"],
        "tier": eval_result["tier"],
        "score_breakdown": eval_result["score_breakdown"],
        "strengths": eval_result["strengths"],
        "weaknesses": eval_result["weaknesses"]
    }

