import streamlit as st
import datetime

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="OptiSupply AI — Multi-Supplier Travel Inventory Optimization",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Theme & Session Initialization
from core.theme import inject_custom_theme
from core.session import init_session_state, set_active_tab
from core.navigation import NAV_ITEMS, get_nav_item
from core.database import init_db, get_db_session
from core.models import DuplicateCandidate, PriceAnomalyAlert
from services.demo_data import seed_demo_data

# Inject styling and initialize state
inject_custom_theme()
init_session_state()

# 3. Database Initialization & Auto-Seed
init_db()
db = get_db_session()

try:
    seed_demo_data(db, force_reset=False)
    
    # Calculate live pending review count
    p_dups = db.query(DuplicateCandidate).filter(DuplicateCandidate.status == "PENDING").count()
    p_anoms = db.query(PriceAnomalyAlert).filter(PriceAnomalyAlert.status == "PENDING").count()
    pending_count = p_dups + p_anoms
    st.session_state["pending_reviews_count"] = pending_count
except Exception as e:
    st.error(f"Database initialization warning: {e}")
    pending_count = 0

active_tab = st.session_state.get("active_tab", "overview")
active_nav = get_nav_item(active_tab)

# 4. Render Brand Sidebar (Recreating React Frontend Sidebar)
with st.sidebar:
    # Brand Header
    st.markdown("""
    <div style="padding-bottom: 1rem; border-bottom: 1px solid rgba(165, 167, 155, 0.4); margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 42px; height: 42px; border-radius: 12px; background: #590907; color: #FFFFFF; display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 0 20px -3px rgba(89, 9, 7, 0.45);">
                ✨
            </div>
            <div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-weight: 800; font-size: 1.25rem; color: #590907; letter-spacing: -0.02em;">OptiSupply AI</span>
                    <span style="font-size: 0.65rem; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; background: #590907; color: #E8D2B5;">v1.0</span>
                </div>
                <div style="font-size: 0.72rem; color: #43443E; font-weight: 600; letter-spacing: 0.04em;">
                    TEAM <strong style="color: #590907;">ASTRA</strong> &bull; VOYAGEHACK 4.0
                </div>
            </div>
        </div>
        <div style="margin-top: 10px; padding: 8px 10px; background: rgba(165, 167, 155, 0.25); border-radius: 8px; border: 1px solid rgba(165, 167, 155, 0.4);">
            <p style="margin: 0; font-size: 0.72rem; color: #2A2B27; font-style: italic; font-family: 'Playfair Display', Georgia, serif; line-height: 1.35;">
                &ldquo;Transforming Fragmented Travel Inventory into Intelligent Decisions.&rdquo;
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #5C5E55; margin-bottom: 8px; padding-left: 4px;'>Platform Capabilities</div>", unsafe_allow_html=True)

    # Render Nav Items
    for item in NAV_ITEMS:
        is_active = (active_tab == item.id)
        btn_label = f"{item.icon}  {item.label}"
        
        # Badge on Human Review Center
        if item.has_badge and pending_count > 0:
            btn_label = f"{item.icon}  {item.label}  ({pending_count})"

        # Button rendering with styling hooks
        btn_type = "primary" if is_active else "secondary"
        if st.button(btn_label, key=f"nav_btn_{item.id}", type=btn_type, use_container_width=True):
            set_active_tab(item.id)
            st.rerun()

    # Sidebar Brand Footer
    st.markdown("""
    <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(165, 167, 155, 0.4);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 0.78rem; font-weight: 700; color: #2A2B27;">Team ASTRA</div>
                <div style="font-size: 0.7rem; color: #5C5E55;">Sonali &amp; Aayush</div>
            </div>
            <span class="badge-pill badge-emerald" style="font-size: 0.65rem;">
                AI Online
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. Top Header Navigation Bar (Recreating React Header)
top_h_col1, top_h_col2 = st.columns([2.5, 2])

with top_h_col1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: #5C5E55; font-weight: 600;">
        <span>OptiSupply AI</span>
        <span>/</span>
        <span style="color: #590907; font-weight: 700;">{active_nav.label}</span>
    </div>
    <h1 style="font-size: 1.55rem; margin: 2px 0 16px 0; font-weight: 800; color: #590907; letter-spacing: -0.02em;">
        {active_nav.icon} {active_nav.label}
    </h1>
    """, unsafe_allow_html=True)

with top_h_col2:
    st.markdown("""
    <div style="display: flex; justify-content: flex-end; align-items: center; gap: 12px; margin-top: 6px;">
        <div style="display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 9999px; background: rgba(165, 167, 155, 0.35); border: 1px solid rgba(165, 167, 155, 0.6); font-size: 0.72rem; font-weight: 600; color: #2A2B27;">
            <span>🛡️</span>
            <span>Sample Benchmark</span>
            <span style="width: 7px; height: 7px; border-radius: 50%; background: #10b981; display: inline-block;"></span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; padding-left: 10px; border-left: 1px solid rgba(165, 167, 155, 0.5);">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: #590907; color: #E8D2B5; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 13px;">
                A
            </div>
            <div style="text-align: left;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #2A2B27; line-height: 1.2;">Sonali &amp; Aayush</div>
                <div style="font-size: 0.68rem; color: #5C5E55;">Team ASTRA Leads</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 6. Dynamic View Dispatching
from views.overview import render_overview
from views.inventory import render_inventory
from views.upload import render_upload
from views.duplicate_detection import render_duplicates
from views.relationships import render_relationships
from views.supplier_intelligence import render_supplier_intelligence
from views.price_anomalies import render_price_anomalies
from views.ranking import render_ranking
from views.quality_enrichment import render_quality_enrichment
from views.review_center import render_review_center
from views.recommendations import render_recommendations
from views.simulation import render_simulation
from views.analytics import render_analytics
from views.settings import render_settings

try:
    if active_tab == "overview":
        render_overview(db)
    elif active_tab == "inventory":
        render_inventory(db)
    elif active_tab == "upload":
        render_upload(db)
    elif active_tab == "duplicates":
        render_duplicates(db)
    elif active_tab == "relationships":
        render_relationships(db)
    elif active_tab == "suppliers":
        render_supplier_intelligence(db)
    elif active_tab == "anomalies":
        render_price_anomalies(db)
    elif active_tab == "ranking":
        render_ranking(db)
    elif active_tab == "quality":
        render_quality_enrichment(db)
    elif active_tab == "review":
        render_review_center(db)
    elif active_tab == "recommendations":
        render_recommendations(db)
    elif active_tab == "simulation":
        render_simulation(db)
    elif active_tab == "analytics":
        render_analytics(db)
    elif active_tab == "settings":
        render_settings(db)
    else:
        render_overview(db)
finally:
    db.close()

