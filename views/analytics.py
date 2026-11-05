import streamlit as st
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from services.analytics import get_analytics_overview
from core.models import InventoryProduct

def render_analytics(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                📈 Executive Analytics &amp; Intelligence Insights
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Real-time analytics computed across normalized multi-supplier feeds. Provides transparent oversight of inventory health.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Live DB Metrics</span>
    </div>
    """, unsafe_allow_html=True)

    data = get_analytics_overview(db)
    kpis = data["kpis"]
    quality_dist = data["quality_distribution"]
    anomaly_dist = data["anomaly_distribution"]

    # 1. Four Executive KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Products</div>
            <div class="kpi-value">{kpis['total_inventory']}</div>
            <div class="kpi-subtitle">{kpis['suppliers_analyzed']} active suppliers</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        dup_rate = round((kpis['high_confidence_matches'] / max(1, kpis['total_inventory'])) * 100, 1)
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Duplicate Match Rate</div>
            <div class="kpi-value" style="color: #065f46;">{dup_rate}%</div>
            <div class="kpi-subtitle">{kpis['high_confidence_matches']} verified high confidence</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Hotel Baseline</div>
            <div class="kpi-value">${kpis['avg_hotel_price']:.2f}</div>
            <div class="kpi-subtitle">{kpis['hotel_records']} hotel properties indexed</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Sightseeing Rate</div>
            <div class="kpi-value">${kpis['avg_sightseeing_price']:.2f}</div>
            <div class="kpi-subtitle">{kpis['sightseeing_records']} experience tickets indexed</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # 2. Price Distribution & Supplier Price Comparison
    all_products = db.query(InventoryProduct).all()

    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
            📊 Multi-Supplier Price Dispersion Analysis
        </h3>
    """, unsafe_allow_html=True)

    # Box plot of prices by supplier
    supp_names = [p.supplier.code if p.supplier else "UNK" for p in all_products]
    prices = [p.base_price for p in all_products]
    types = [p.product_type for p in all_products]

    fig_box = go.Figure()
    fig_box.add_trace(go.Box(
        x=supp_names,
        y=prices,
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8,
        marker_color='#590907',
        line_color='#590907',
        fillcolor='rgba(232, 210, 181, 0.45)',
        name="Rate Distribution ($)"
    ))
    fig_box.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#2A2B27"),
        yaxis=dict(gridcolor="rgba(165, 167, 155, 0.3)", zeroline=False, title="Base Price ($)"),
        xaxis=dict(showgrid=False, title="Supplier Feeds")
    )
    st.plotly_chart(fig_box, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Two side-by-side charts: Completeness Tiers & Anomaly Distributions
    c_col1, c_col2 = st.columns(2)

    with c_col1:
        st.markdown("""
        <div class="glass-card">
            <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
                ✨ Content Quality Completeness Tiers
            </h3>
        """, unsafe_allow_html=True)
        q_tiers = [q["tier"] for q in quality_dist]
        q_counts = [q["count"] for q in quality_dist]
        q_colors = [q["fill"] for q in quality_dist]

        fig_q = go.Figure(data=[
            go.Bar(
                x=q_tiers,
                y=q_counts,
                marker_color=q_colors,
                text=q_counts,
                textposition='auto'
            )
        ])
        fig_q.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#2A2B27"),
            yaxis=dict(gridcolor="rgba(165,167,155,0.3)"),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_q, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c_col2:
        st.markdown("""
        <div class="glass-card">
            <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
                ⚠️ Statistical Outlier Severity Distribution
            </h3>
        """, unsafe_allow_html=True)
        anom_labels = [a["name"] for a in anomaly_dist if a["value"] > 0]
        anom_vals = [a["value"] for a in anomaly_dist if a["value"] > 0]
        anom_cols = [a["color"] for a in anomaly_dist if a["value"] > 0]

        if not anom_vals:
            anom_labels = ["No Anomalies"]
            anom_vals = [1]
            anom_cols = ["#A5A79B"]

        fig_anom = go.Figure(data=[
            go.Pie(
                labels=anom_labels,
                values=anom_vals,
                hole=0.55,
                marker_colors=anom_cols,
                textinfo='label+value',
                marker_line_color='rgba(255,255,255,0.8)',
                marker_line_width=2
            )
        ])
        fig_anom.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#2A2B27"),
            showlegend=False
        )
        st.plotly_chart(fig_anom, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

