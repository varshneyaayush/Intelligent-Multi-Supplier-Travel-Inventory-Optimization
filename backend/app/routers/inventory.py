import io
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import InventoryProduct, Supplier, AuditLog
from app.schemas import ProductOut, IngestionPreviewResponse, IngestionCommitRequest, IngestionCommitResponse
from app.services.ingestion import ingestion_service
from app.services.demo_data import seed_demo_data
from app.ai.quality_enrichment import quality_engine

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

@router.get("", response_model=List[ProductOut])
def get_inventory(
    product_type: Optional[str] = Query(None, description="'HOTEL' or 'SIGHTSEEING'"),
    supplier_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(InventoryProduct)
    if product_type:
        query = query.filter(InventoryProduct.product_type == product_type.upper())
    if supplier_id:
        query = query.filter(InventoryProduct.supplier_id == supplier_id)
    if city:
        query = query.filter(InventoryProduct.city.ilike(f"%{city}%"))
    if search:
        query = query.filter(
            (InventoryProduct.name.ilike(f"%{search}%")) |
            (InventoryProduct.description.ilike(f"%{search}%")) |
            (InventoryProduct.address.ilike(f"%{search}%"))
        )

    products = query.order_by(InventoryProduct.id.asc()).all()
    results = []
    for p in products:
        item = ProductOut(
            id=p.id,
            supplier_id=p.supplier_id,
            supplier_name=p.supplier.name if p.supplier else "Unknown",
            supplier_code=p.supplier.code if p.supplier else "UNK",
            external_id=p.external_id,
            product_type=p.product_type,
            name=p.name,
            description=p.description,
            city=p.city,
            country=p.country,
            address=p.address,
            latitude=p.latitude,
            longitude=p.longitude,
            image_url=p.image_url,
            star_rating=p.star_rating,
            room_category=p.room_category,
            amenities=p.amenities,
            duration_hours=p.duration_hours,
            inclusions=p.inclusions,
            exclusions=p.exclusions,
            meeting_point=p.meeting_point,
            activity_type=p.activity_type,
            currency=p.currency,
            base_price=p.base_price,
            tax_amount=p.tax_amount,
            cancellation_policy=p.cancellation_policy,
            availability_status=p.availability_status,
            data_completeness_score=p.data_completeness_score,
            created_at=p.created_at
        )
        results.append(item)
    return results

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(InventoryProduct).filter(InventoryProduct.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut(
        id=p.id,
        supplier_id=p.supplier_id,
        supplier_name=p.supplier.name if p.supplier else "Unknown",
        supplier_code=p.supplier.code if p.supplier else "UNK",
        external_id=p.external_id,
        product_type=p.product_type,
        name=p.name,
        description=p.description,
        city=p.city,
        country=p.country,
        address=p.address,
        latitude=p.latitude,
        longitude=p.longitude,
        image_url=p.image_url,
        star_rating=p.star_rating,
        room_category=p.room_category,
        amenities=p.amenities,
        duration_hours=p.duration_hours,
        inclusions=p.inclusions,
        exclusions=p.exclusions,
        meeting_point=p.meeting_point,
        activity_type=p.activity_type,
        currency=p.currency,
        base_price=p.base_price,
        tax_amount=p.tax_amount,
        cancellation_policy=p.cancellation_policy,
        availability_status=p.availability_status,
        data_completeness_score=p.data_completeness_score,
        created_at=p.created_at
    )

@router.post("/upload-preview", response_model=IngestionPreviewResponse)
async def upload_preview(file: UploadFile = File(...)):
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported.")
    
    content = await file.read()
    try:
        df = ingestion_service.parse_file(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    columns = list(df.columns)
    suggested = ingestion_service.suggest_column_mapping(columns)
    
    # Take first 5 sample rows as clean dictionaries
    sample_df = df.head(5).fillna("")
    sample_rows = sample_df.to_dict(orient="records")

    return IngestionPreviewResponse(
        filename=file.filename,
        total_rows=len(df),
        detected_columns=columns,
        suggested_mapping=suggested,
        sample_rows=sample_rows
    )

@router.post("/commit-import", response_model=IngestionCommitResponse)
def commit_import(payload: IngestionCommitRequest, db: Session = Depends(get_db)):
    # Find or create supplier
    supplier = db.query(Supplier).filter(Supplier.code == payload.supplier_code).first()
    if not supplier:
        supplier = Supplier(
            code=payload.supplier_code,
            name=payload.supplier_name or f"Supplier {payload.supplier_code}",
            country="Global",
            reliability_tier="Tier 2 (Standard)"
        )
        db.add(supplier)
        db.flush()

    imported_ids = []
    skipped_count = 0
    errors = []

    for idx, row in enumerate(payload.rows):
        normalized, row_errors = ingestion_service.validate_and_normalize_row(
            row, payload.column_mapping, payload.product_type
        )
        if row_errors:
            skipped_count += 1
            errors.append(f"Row {idx+1}: {', '.join(row_errors)}")
            continue

        # Prevent duplicate external_id from same supplier
        existing = db.query(InventoryProduct).filter(
            InventoryProduct.supplier_id == supplier.id,
            InventoryProduct.external_id == normalized["external_id"]
        ).first()
        if existing:
            skipped_count += 1
            errors.append(f"Row {idx+1}: Duplicate item ID '{normalized['external_id']}' already imported.")
            continue

        # Compute quality completeness score
        quality_eval = quality_engine.evaluate_quality(normalized)
        normalized["data_completeness_score"] = quality_eval["completeness_score"]

        product = InventoryProduct(
            supplier_id=supplier.id,
            **normalized
        )
        db.add(product)
        db.flush()
        imported_ids.append(product.id)

    db.commit()

    # Log audit event
    audit = AuditLog(
        action="IMPORT_INVENTORY",
        entity_type="INVENTORY",
        entity_id=supplier.id,
        decision="IMPORTED",
        details={"supplier_code": supplier.code, "imported": len(imported_ids), "skipped": skipped_count}
    )
    db.add(audit)
    db.commit()

    return IngestionCommitResponse(
        success=len(imported_ids) > 0,
        imported_count=len(imported_ids),
        skipped_count=skipped_count,
        errors=errors[:10], # Return top 10 errors for brevity
        sample_imported_ids=imported_ids[:5]
    )

@router.post("/reset-demo")
def reset_demo_data_endpoint(db: Session = Depends(get_db)):
    seed_demo_data(db, force_reset=True)
    return {"message": "Demonstration benchmark data successfully re-seeded and re-analyzed."}

