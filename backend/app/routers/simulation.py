from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InventoryProduct, SimulationScenario
from app.schemas import SimulationRequest, SimulationResult
from app.ai.simulation_engine import simulation_engine

router = APIRouter(prefix="/api/simulation", tags=["What-If Simulation Engine"])

@router.post("", response_model=SimulationResult)
def run_simulation(
    payload: SimulationRequest = Body(...),
    db: Session = Depends(get_db)
):
    products = db.query(InventoryProduct).all()
    prod_dicts = []
    for p in products:
        prod_dicts.append({
            "id": p.id,
            "name": p.name,
            "supplier_id": p.supplier_id,
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

    result = simulation_engine.simulate_scenario(
        products=prod_dicts,
        scenario_name=payload.scenario_name,
        excluded_supplier_ids=payload.excluded_supplier_ids,
        weight_adjustments=payload.weight_adjustments.dict(),
        max_price_cap=payload.max_price_cap,
        require_free_cancellation=payload.require_free_cancellation
    )

    # Save scenario record in database
    scenario_model = SimulationScenario(
        name=payload.scenario_name,
        description=f"Simulation with {len(payload.excluded_supplier_ids)} excluded suppliers and custom weights.",
        parameters=payload.dict(),
        baseline_metrics=result["baseline_summary"],
        simulated_metrics=result["simulated_summary"],
        trade_offs=result["trade_off_analysis"]
    )
    db.add(scenario_model)
    db.commit()

    return result

