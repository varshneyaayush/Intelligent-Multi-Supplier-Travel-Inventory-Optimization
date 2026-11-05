import streamlit as st
from typing import Any, Dict

def init_session_state():
    """Initializes and preserves all required session state variables across Streamlit reruns."""
    defaults: Dict[str, Any] = {
        "active_tab": "overview",
        "pending_reviews_count": 0,
        "last_action_message": None,
        
        # Inventory filters
        "inventory_type_filter": "ALL",
        "inventory_search_query": "",
        "inventory_supplier_filter": "ALL",
        
        # Duplicate filters
        "dup_classification_filter": "ALL",
        "dup_status_filter": "PENDING",
        
        # Relationship filters
        "rel_type_filter": "ALL",
        
        # Anomaly filters
        "anomaly_severity_filter": "ALL",
        "anomaly_status_filter": "PENDING",
        
        # Ranking weights
        "ranking_weights": {
            "price_weight": 0.30,
            "trust_weight": 0.25,
            "availability_weight": 0.15,
            "quality_weight": 0.15,
            "cancellation_weight": 0.15
        },
        
        # Supplier trust weights
        "supplier_trust_weights": {
            "price_competitiveness": 0.25,
            "booking_success_rate": 0.25,
            "availability_accuracy": 0.20,
            "cancellation_reliability": 0.15,
            "data_completeness": 0.15
        },
        
        # Simulation parameters
        "sim_scenario_name": "Post-Peak Demand Optimization",
        "sim_excluded_suppliers": [],
        "sim_require_free_cancellation": False,
        "sim_max_price_cap": 500.0,
        "sim_weights": {
            "price_weight": 0.30,
            "trust_weight": 0.25,
            "availability_weight": 0.15,
            "quality_weight": 0.15,
            "cancellation_weight": 0.15
        },
        "simulation_result": None,
        
        # Upload / Ingestion state
        "upload_preview": None,
        "upload_filename": None,
        "upload_file_bytes": None,
        "column_mapping": {},
        "target_product_type": "HOTEL",
        "upload_supplier_code": "SUP_NEW",
        "upload_supplier_name": "New Global Partner DMC",
        
        # Settings state
        "threshold_high_confidence": 0.85,
        "threshold_review": 0.60,
        "geo_vicinity_radius": 500.0,
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def set_active_tab(tab_id: str):
    st.session_state["active_tab"] = tab_id

