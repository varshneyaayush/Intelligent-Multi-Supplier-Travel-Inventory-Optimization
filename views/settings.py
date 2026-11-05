import streamlit as st
from sqlalchemy.orm import Session
from core.config import settings
from services.demo_data import seed_demo_data
from core.models import InventoryProduct, Supplier, DuplicateCandidate, PriceAnomalyAlert

def render_settings(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                ⚙️ Platform Settings &amp; AI Calibration
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Adjust multi-modal match thresholds, inspect database engine health, or re-seed demonstration benchmarks.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">System Settings</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. AI Threshold Calibration Card
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
            1. Multi-Modal Duplicate Detection Thresholds
        </h3>
        <p style="margin: 0 0 14px 0; font-size: 0.8rem; color: #5C5E55;">
            Configure sensitivity for candidate pair routing. Matches between the review and high confidence thresholds route to the Human Review Center.
        </p>
    """, unsafe_allow_html=True)

    t_high = st.slider(
        f"High Confidence Match Threshold: {int(st.session_state.get('threshold_high_confidence', 0.85)*100)}%",
        min_value=70,
        max_value=99,
        value=int(st.session_state.get("threshold_high_confidence", 0.85)*100),
        step=1,
        help="Matches above this threshold qualify for automated mapping recommendations."
    )
    st.session_state["threshold_high_confidence"] = t_high / 100.0

    t_rev = st.slider(
        f"Human Review Threshold: {int(st.session_state.get('threshold_review', 0.60)*100)}%",
        min_value=40,
        max_value=80,
        value=int(st.session_state.get("threshold_review", 0.60)*100),
        step=1,
        help="Matches between this threshold and high confidence route to the Human Review Center queue."
    )
    st.session_state["threshold_review"] = t_rev / 100.0

    t_geo = st.slider(
        f"Geographic Proximity Radius: {int(st.session_state.get('geo_vicinity_radius', 500))} meters",
        min_value=50,
        max_value=2500,
        value=int(st.session_state.get("geo_vicinity_radius", 500)),
        step=50,
        help="Maximum distance in meters to classify properties within the same immediate neighborhood."
    )
    st.session_state["geo_vicinity_radius"] = float(t_geo)

    if st.button("💾 Save Calibrated Thresholds"):
        st.success("AI detection thresholds saved to session configuration.")

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Database & Platform Engine Status
    db_url = settings.DATABASE_URL
    is_sqlite = db_url.startswith("sqlite")
    engine_name = "SQLite 3 (Embedded Local ORM)" if is_sqlite else "PostgreSQL (Enterprise Managed DB)"

    tot_prods = db.query(InventoryProduct).count()
    tot_sups = db.query(Supplier).count()
    tot_dups = db.query(DuplicateCandidate).count()
    tot_anoms = db.query(PriceAnomalyAlert).count()

    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h3 style="font-size: 0.95rem; margin: 0; color: #590907; font-weight: 700;">
                2. Database Engine &amp; Connectivity Status
            </h3>
            <span class="badge-pill badge-emerald">Online &bull; Connected</span>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 0.8rem;">
            <div style="background: rgba(253,252,249,0.7); border: 1px solid rgba(232,210,181,0.7); border-radius: 8px; padding: 10px;">
                <div style="color: #75776C; font-weight: 600;">Engine Type:</div>
                <div style="font-weight: 700; color: #590907; font-size: 0.9rem;">{engine_name}</div>
                <div style="font-size: 0.72rem; color: #5C5E55; margin-top: 2px;">
                    Connection: <code>{db_url.split('@')[-1] if '@' in db_url else db_url}</code>
                </div>
            </div>
            
            <div style="background: rgba(253,252,249,0.7); border: 1px solid rgba(232,210,181,0.7); border-radius: 8px; padding: 10px;">
                <div style="color: #75776C; font-weight: 600;">Live Catalog Population:</div>
                <div style="font-weight: 700; color: #2A2B27; font-size: 0.85rem;">
                    {tot_prods} Products &bull; {tot_sups} Suppliers &bull; {tot_dups} Duplicates &bull; {tot_anoms} Anomalies
                </div>
                <div style="font-size: 0.72rem; color: #065f46; margin-top: 2px;">
                    Status: Nominal operation
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Benchmark Data Reset
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 8px 0; color: #590907; font-weight: 700;">
            3. Benchmark Demonstration Reset
        </h3>
        <p style="margin: 0 0 14px 0; font-size: 0.8rem; color: #5C5E55;">
            Restore the pristine benchmark demonstration dataset: Grand Palace Hotel multi-supplier scenario, Louvre Museum tours, Dubai desert safaris, and supplier metrics.
        </p>
    """, unsafe_allow_html=True)

    if st.button("🔄 Reset to Baseline Demonstration Benchmark (Grand Palace Scenario)", type="primary"):
        with st.spinner("Re-seeding database and re-executing AI intelligence pipelines..."):
            seed_demo_data(db, force_reset=True)
            st.success("Demonstration benchmark data successfully re-seeded and re-analyzed!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

