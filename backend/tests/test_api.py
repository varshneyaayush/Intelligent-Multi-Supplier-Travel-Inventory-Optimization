from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "OptiSupply AI"
    assert data["team"] == "ASTRA"

def test_api_inventory_list():
    response = client.get("/api/inventory")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    # Verify Grand Palace is present
    names = [p["name"] for p in items]
    assert any("Grand Palace" in n for n in names)

def test_api_duplicates_list():
    response = client.get("/api/duplicates")
    assert response.status_code == 200
    dups = response.json()
    assert len(dups) > 0
    # Verify evidence structure
    first = dups[0]
    assert "overall_confidence" in first
    assert "evidence_breakdown" in first

def test_api_price_anomalies():
    response = client.get("/api/anomalies")
    assert response.status_code == 200
    anomalies = response.json()
    assert len(anomalies) > 0

def test_api_ranking():
    payload = {
        "price_weight": 0.40,
        "trust_weight": 0.30,
        "availability_weight": 0.10,
        "quality_weight": 0.10,
        "cancellation_weight": 0.10
    }
    response = client.post("/api/ranking", json=payload)
    assert response.status_code == 200
    ranked = response.json()
    assert len(ranked) > 0
    assert ranked[0]["rank"] == 1
    assert "overall_score" in ranked[0]

def test_api_analytics_overview():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert data["kpis"]["total_inventory"] > 0
    assert data["kpis"]["hotel_records"] > 0
    assert data["kpis"]["suppliers_analyzed"] > 0

def test_api_simulation():
    payload = {
        "scenario_name": "Test Simulation - Exclude Supplier C",
        "excluded_supplier_ids": [3],
        "weight_adjustments": {
            "price_weight": 0.50,
            "trust_weight": 0.20,
            "availability_weight": 0.10,
            "quality_weight": 0.10,
            "cancellation_weight": 0.10
        },
        "require_free_cancellation": False
    }
    response = client.post("/api/simulation", json=payload)
    assert response.status_code == 200
    sim = response.json()
    assert "baseline_summary" in sim
    assert "simulated_summary" in sim
    assert "rank_shifts" in sim

