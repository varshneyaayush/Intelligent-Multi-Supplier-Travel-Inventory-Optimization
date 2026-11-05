from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import InventoryProduct
from app.schemas import RankedProductItem, RankingWeights
from app.ai.ranking_engine import ranking_engine

router = APIRouter(prefix="/api/ranking", tags=["Supplier & Product Ranking"])

@router.post("", response_model=List[RankedProductItem])
def rank_inventory(
    weights: RankingWeights = Body(RankingWeights()),
    product_type: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(InventoryProduct)
    if product_type:
        query = query.filter(InventoryProduct.product_type == product_type.upper())
    if city:
        query = query.filter(InventoryProduct.city.ilike(f"%{city}%"))

    products = query.all()
    prod_dicts = []
    for p in products:
        prod_dicts.append({
            "id": p.id,
            "name": p.name,
            "product_type": p.product_type,
            "supplier_name": p.supplier.name if p.supplier else "Unknown",
            "supplier_code": p.supplier.code if p.supplier else "UNK",
            "supplier_trust_score": p.supplier.metrics.trust_score if (p.supplier and p.supplier.metrics) else 80.0,
            "base_price": p.base_price,
            "star_rating": p.star_rating,
            "room_category": p.room_category,
            "activity_type": p.activity_type,
            "cancellation_policy": p.cancellation_policy,
            "availability_status": p.availability_status,
            "data_completeness_score": p.data_completeness_score
        })

    ranked = ranking_engine.rank_products(prod_dicts, weights.dict())
    return ranked

