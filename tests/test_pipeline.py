import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from ai.duplicate_detector import duplicate_engine
from ai.relationship_engine import relationship_engine
from ai.price_anomaly import price_engine
from ai.supplier_intelligence import supplier_engine
from ai.ranking_engine import ranking_engine
from ai.quality_enrichment import quality_engine
from ai.simulation_engine import simulation_engine
from ai.recommendation_engine import recommendation_engine
from services.ingestion import ingestion_service

def test_duplicate_detection_high_confidence():
    prod_a = {
        "product_type": "HOTEL",
        "name": "Grand Palace Hotel",
        "city": "Paris",
        "latitude": 48.860611,
        "longitude": 2.337644,
        "star_rating": 5.0,
        "room_category": "Deluxe King",
        "description": "Luxury 5-star hotel in central Paris with pool and spa."
    }
    prod_b = {
        "product_type": "HOTEL",
        "name": "The Grand Palace",
        "city": "Paris",
        "latitude": 48.860635,
        "longitude": 2.337612,
        "star_rating": 5.0,
        "room_category": "Deluxe Room",
        "description": "5-star luxury palace hotel in central Paris with wellness spa."
    }
    res = duplicate_engine.compare_pair(prod_a, prod_b)
    assert res["overall_confidence"] >= 0.80
    assert res["match_classification"] in ["HIGH_CONFIDENCE", "POSSIBLE_REVIEW"]
    assert res["geo_distance_meters"] is not None
    assert res["geo_distance_meters"] < 50.0

def test_relationship_different_room_category():
    prod_a = {
        "id": 1,
        "supplier_id": 1,
        "product_type": "HOTEL",
        "name": "Grand Palace Hotel",
        "city": "Paris",
        "latitude": 48.860611,
        "longitude": 2.337644,
        "room_category": "Deluxe King",
        "base_price": 120.0
    }
    prod_b = {
        "id": 2,
        "supplier_id": 1,
        "product_type": "HOTEL",
        "name": "Grand Palace Hotel",
        "city": "Paris",
        "latitude": 48.860611,
        "longitude": 2.337644,
        "room_category": "Presidential Royal Suite",
        "base_price": 420.0
    }
    rel = relationship_engine.classify_relationship(prod_a, prod_b)
    assert rel is not None
    assert rel["relationship_type"] == "DIFFERENT_ROOM_CATEGORY"

def test_price_anomaly_detection():
    products = [
        {"id": 1, "base_price": 98.0, "currency": "USD"},
        {"id": 2, "base_price": 120.0, "currency": "USD"},
        {"id": 3, "base_price": 145.0, "currency": "USD"},
        {"id": 4, "base_price": 350.0, "currency": "USD"}
    ]
    anomalies = price_engine.detect_group_anomalies(products)
    assert len(anomalies) > 0
    anom_ids = [a["product_id"] for a in anomalies]
    assert 4 in anom_ids
    outlier = next(a for a in anomalies if a["product_id"] == 4)
    assert outlier["anomaly_type"] == "HIGH_PRICE"

def test_supplier_trust_scoring():
    metrics = {
        "price_competitiveness": 90.0,
        "booking_success_rate": 96.0,
        "availability_accuracy": 92.0,
        "cancellation_reliability": 88.0,
        "data_completeness": 94.0,
        "response_time_ms": 210.0,
        "is_synthetic": True
    }
    eval_res = supplier_engine.compute_trust_score(metrics)
    assert eval_res["trust_score"] >= 85.0
    assert "Tier 1" in eval_res["tier"]
    assert len(eval_res["strengths"]) > 0

def test_ranking_engine_multi_criteria():
    products = [
        {
            "id": 1,
            "name": "Cheap Hotel Low Trust",
            "supplier_name": "Supplier Low",
            "base_price": 80.0,
            "supplier_trust_score": 60.0,
            "availability_status": "Limited",
            "data_completeness_score": 0.6,
            "cancellation_policy": "Non-refundable"
        },
        {
            "id": 2,
            "name": "Mid-Price Hotel High Trust",
            "supplier_name": "Supplier High",
            "base_price": 100.0,
            "supplier_trust_score": 95.0,
            "availability_status": "Available",
            "data_completeness_score": 0.95,
            "cancellation_policy": "Free Cancellation 24h"
        }
    ]
    weights = {
        "price_weight": 0.20,
        "trust_weight": 0.35,
        "availability_weight": 0.15,
        "quality_weight": 0.15,
        "cancellation_weight": 0.15
    }
    ranked = ranking_engine.rank_products(products, weights)
    assert ranked[0]["product_id"] == 2
    assert ranked[0]["rank"] == 1

def test_quality_and_grounded_enrichment():
    prod = {
        "id": 10,
        "product_type": "HOTEL",
        "name": "Eiffel River View Lodge",
        "description": "Lovely boutique lodge with complimentary high-speed Wi-Fi, swimming pool, and luxury spa.",
        "city": "Paris",
        "address": None,
        "latitude": None,
        "longitude": None,
        "amenities": [],
        "base_price": 95.0,
        "cancellation_policy": "Non-refundable"
    }
    q = quality_engine.evaluate_quality(prod)
    assert q["completeness_score"] < 0.75
    assert "coordinates (latitude/longitude)" in q["missing_fields"]
    assert len(q["enrichment_suggestions"]) > 0
    amenities_sugg = next((s for s in q["enrichment_suggestions"] if s["field"] == "amenities"), None)
    assert amenities_sugg is not None
    assert any("Wi-Fi" in a for a in amenities_sugg["suggested_value"])

def test_ingestion_column_mapping_and_validation():
    cols = ["hotel_name", "nightly_rate", "city_name", "lat", "lon", "room_type"]
    mapping = ingestion_service.suggest_column_mapping(cols)
    assert mapping.get("hotel_name") == "name"
    assert mapping.get("nightly_rate") == "base_price"
    assert mapping.get("city_name") == "city"

    row = {
        "hotel_name": "The Savoy London",
        "nightly_rate": "$450.00",
        "city_name": "London",
        "lat": 51.5103,
        "lon": -0.1205,
        "room_type": "Deluxe King"
    }
    norm, errors = ingestion_service.validate_and_normalize_row(row, mapping, "HOTEL")
    assert errors == []
    assert norm["name"] == "The Savoy London"
    assert norm["base_price"] == 450.0
    assert norm["city"] == "London"

def test_simulation_engine():
    products = [
        {
            "id": 1,
            "name": "Apex Hotel",
            "supplier_id": 1,
            "supplier_name": "Apex",
            "base_price": 120.0,
            "score_breakdown": {"trust_score": 92.0},
            "cancellation_policy": "Free Cancellation"
        },
        {
            "id": 2,
            "name": "Bedrock Hotel",
            "supplier_id": 2,
            "supplier_name": "Bedrock",
            "base_price": 98.0,
            "score_breakdown": {"trust_score": 87.0},
            "cancellation_policy": "Non-refundable"
        }
    ]
    res = simulation_engine.simulate_scenario(
        products=products,
        scenario_name="Test Simulation",
        excluded_supplier_ids=[2],
        require_free_cancellation=True
    )
    assert res["simulated_summary"]["eligible_products"] == 1
    assert res["projected_impact"]["inventory_reduction_pct"] == 50.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


