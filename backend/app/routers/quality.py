import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import InventoryQualityReport, InventoryProduct, AuditLog
from app.schemas import QualityReportOut

router = APIRouter(prefix="/api/quality", tags=["Inventory Quality & Enrichment"])

@router.get("", response_model=List[QualityReportOut])
def get_quality_reports(
    status: Optional[str] = Query(None),
    min_completeness: Optional[float] = Query(None),
    max_completeness: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(InventoryQualityReport)
    if status:
        query = query.filter(InventoryQualityReport.status == status.upper())
    if min_completeness is not None:
        query = query.filter(InventoryQualityReport.completeness_score >= min_completeness)
    if max_completeness is not None:
        query = query.filter(InventoryQualityReport.completeness_score <= max_completeness)

    reports = query.order_by(InventoryQualityReport.completeness_score.asc()).all()
    for r in reports:
        if r.product:
            r.product.supplier_name = r.product.supplier.name
            r.product.supplier_code = r.product.supplier.code
    return reports

@router.post("/{report_id}/apply-enrichment")
def apply_enrichment(report_id: int, db: Session = Depends(get_db)):
    report = db.query(InventoryQualityReport).filter(InventoryQualityReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Quality report not found")
    
    product = report.product
    if not product:
        raise HTTPException(status_code=404, detail="Associated product not found")

    applied_fields = []
    # Grounded enrichment update
    for item in report.enrichment_suggestions:
        field = item.get("field")
        val = item.get("suggested_value")
        if field == "amenities" and isinstance(val, list):
            existing = product.amenities or []
            combined = list(set(existing + val))
            product.amenities = combined
            applied_fields.append("amenities")
        elif field == "inclusions" and isinstance(val, list):
            existing = product.inclusions or []
            combined = list(set(existing + val))
            product.inclusions = combined
            applied_fields.append("inclusions")

    # Recalculate completeness score
    report.completeness_score = min(1.0, report.completeness_score + 0.15)
    product.data_completeness_score = report.completeness_score
    report.status = "ENRICHED"
    report.reviewed_at = datetime.datetime.utcnow()

    audit = AuditLog(
        action="APPLY_CONTENT_ENRICHMENT",
        entity_type="QUALITY",
        entity_id=report.id,
        decision="ENRICHED",
        details={"product_name": product.name, "applied_fields": applied_fields}
    )
    db.add(audit)
    db.commit()

    return {
        "success": True,
        "product_id": product.id,
        "new_completeness_score": report.completeness_score,
        "applied_fields": applied_fields,
        "status": report.status
    }

