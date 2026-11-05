from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database import get_db
from app.models import ProductRelationship, InventoryProduct
from app.schemas import RelationshipOut

router = APIRouter(prefix="/api/relationships", tags=["Product Relationships"])

@router.get("", response_model=List[RelationshipOut])
def get_relationships(
    relationship_type: Optional[str] = Query(None),
    product_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ProductRelationship)
    if relationship_type:
        query = query.filter(ProductRelationship.relationship_type == relationship_type)
    if product_id:
        query = query.filter(
            (ProductRelationship.source_product_id == product_id) |
            (ProductRelationship.target_product_id == product_id)
        )

    rels = query.order_by(ProductRelationship.confidence_score.desc()).all()
    for r in rels:
        if r.source_product:
            r.source_product.supplier_name = r.source_product.supplier.name
            r.source_product.supplier_code = r.source_product.supplier.code
        if r.target_product:
            r.target_product.supplier_name = r.target_product.supplier.name
            r.target_product.supplier_code = r.target_product.supplier.code
    return rels

@router.get("/graph")
def get_relationship_graph(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Returns visual graph structure formatted with nodes and edges."""
    products = db.query(InventoryProduct).all()
    relationships = db.query(ProductRelationship).all()

    nodes = []
    for p in products:
        nodes.append({
            "id": str(p.id),
            "label": p.name,
            "type": p.product_type,
            "supplier": p.supplier.name if p.supplier else "Unknown",
            "supplier_code": p.supplier.code if p.supplier else "UNK",
            "price": p.base_price,
            "city": p.city,
            "room_or_activity": p.room_category or p.activity_type or "General"
        })

    links = []
    for r in relationships:
        links.append({
            "id": str(r.id),
            "source": str(r.source_product_id),
            "target": str(r.target_product_id),
            "relationship_type": r.relationship_type,
            "confidence": r.confidence_score,
            "evidence": r.evidence
        })

    return {
        "nodes": nodes,
        "links": links
    }

