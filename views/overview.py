import streamlit as st
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from services.analytics import get_analytics_overview
from core.session import set_active_tab

def render_overview(db: Session):
    data = get_analytics_overview(db)
    kpis = data["kpis"]
    quality_dist = data["quality_distribution"]
    anomaly_dist = data["anomaly_distribution"]
    leaderboard = data["supplier_leaderboard"]

    # 1. Active Demonstration Scenario Spotlight Banner (Grand Palace Hotel Benchmark)
    st.markdown(f"""
    <div class="banner-burgundy">
        <div style="display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; border-radius: 9999px; background: rgba(232, 210, 181, 0.2); border: 1px solid rgba(232, 210, 181, 0.35); font-size: 0.725rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #E8D2B5; margin-bottom: 12px;">
            <span>✨</span> Active Demonstration Scenario • Grand Palace Hotel Benchmark
        </div>
        <h2 style="font-size: 1.65rem; margin-top: 0; margin-bottom: 8px; font-weight: 800; color: #FDFCF9;">
            Multi-Supplier Travel Inventory Optimization
        </h2>
        <p style="margin: 0; font-size: 0.95rem; color: #E8D2B5; line-height: 1.6; max-width: 900px;">
            Consolidating fragmented hotel & sightseeing records across <strong style="color: #FFFFFF;">Apex Wholesale</strong>, <strong style="color: #FFFFFF;">Bedrock Network</strong>, and <strong style="color: #FFFFFF;">Continental DMC</strong>. Automated multi-modal matching identified identical properties with price variations from <strong style="color: #FFFFFF;">$98.00</strong> to <strong style="color: #FFFFFF;">$145.00</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons under banner
    btn_col1, btn_col2, _ = st.columns([1.5, 1.8, 3])
    with btn_col1:
        if st.button(f"🔍 Inspect Duplicate Pairs ({kpis['potential_duplicate_groups']})", key="btn_inspect_dups"):
            set_active_tab("duplicates")
            st.rerun()
    with btn_col2:
        if st.button("⚖️ Explore Multi-Criteria Ranking", key="btn_explore_ranking"):
            set_active_tab("ranking")
            st.rerun()

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 2. Four High-Level KPI Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Inventory</div>
            <div class="kpi-value">{kpis['total_inventory']} <span style="font-size: 0.9rem; font-weight: 500; color: #75776C;">records</span></div>
            <div class="kpi-subtitle" style="border-top: 1px solid rgba(165,167,155,0.3); padding-top: 8px; margin-top: 8px;">
                {kpis['hotel_records']} Hotels &bull; {kpis['sightseeing_records']} Experiences
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Duplicates Detected</div>
            <div class="kpi-value" style="color: #065f46;">{kpis['potential_duplicate_groups']} <span style="font-size: 0.9rem; font-weight: 500; color: #75776C;">pairs</span></div>
            <div class="kpi-subtitle" style="border-top: 1px solid rgba(165,167,155,0.3); padding-top: 8px; margin-top: 8px;">
                {kpis['high_confidence_matches']} High Conf &bull; {kpis['possible_review_matches']} Review
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Price Anomalies</div>
            <div class="kpi-value" style="color: #9f1239;">{kpis['price_anomaly_alerts']} <span style="font-size: 0.9rem; font-weight: 500; color: #75776C;">alerts</span></div>
            <div class="kpi-subtitle" style="border-top: 1px solid rgba(165,167,155,0.3); padding-top: 8px; margin-top: 8px;">
                IQR & Z-Score Multi-Supplier Outliers
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Human Reviews</div>
            <div class="kpi-value" style="color: #590907;">{kpis['pending_human_reviews']} <span style="font-size: 0.9rem; font-weight: 500; color: #75776C;">tasks</span></div>
            <div class="kpi-subtitle" style="border-top: 1px solid rgba(165,167,155,0.3); padding-top: 8px; margin-top: 8px;">
                Human-in-the-Loop Decisions Pending
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # 3. Two Charts: Quality Completeness + Price Anomaly Breakdown
    chart_col1, chart_col2 = st.columns([1.2, 1])

    with chart_col1:
        st.markdown("""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="font-size: 0.95rem; margin: 0; font-weight: 700; color: #590907;">
                    📊 Inventory Quality Completeness Distribution
                </h3>
                <span class="badge-pill badge-cream">Measurable Quality</span>
            </div>
        """, unsafe_allow_html=True)

        tiers = [q["tier"] for q in quality_dist]
        counts = [q["count"] for q in quality_dist]
        colors = [q["fill"] for q in quality_dist]

        fig_bar = go.Figure(data=[
            go.Bar(
                x=tiers,
                y=counts,
                marker_color=colors,
                text=counts,
                textposition='auto',
                marker_line_color='rgba(89, 9, 7, 0.2)',
                marker_line_width=1,
            )
        ])
        fig_bar.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#2A2B27"),
            yaxis=dict(gridcolor="rgba(165, 167, 155, 0.3)", zeroline=False),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown("""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="font-size: 0.95rem; margin: 0; font-weight: 700; color: #590907;">
                    ⚠️ Price Anomaly Severity Breakdown
                </h3>
                <span class="badge-pill badge-burgundy">IQR & Z-Score</span>
            </div>
        """, unsafe_allow_html=True)

        anom_labels = [a["name"] for a in anomaly_dist if a["value"] > 0]
        anom_values = [a["value"] for a in anomaly_dist if a["value"] > 0]
        anom_colors = [a["color"] for a in anomaly_dist if a["value"] > 0]

        if not anom_values:
            anom_labels = ["No Anomalies"]
            anom_values = [1]
            anom_colors = ["#A5A79B"]

        fig_pie = go.Figure(data=[
            go.Pie(
                labels=anom_labels,
                values=anom_values,
                hole=0.55,
                marker_colors=anom_colors,
                textinfo='label+value',
                insidetextorientation='horizontal',
                marker_line_color='rgba(255, 255, 255, 0.8)',
                marker_line_width=2
            )
        ])
        fig_pie.update_layout(
            height=260,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif", size=11, color="#2A2B27"),
            showlegend=False
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Supplier Trust Leaderboard
    st.markdown("""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
                <h3 style="font-size: 1rem; margin: 0; font-weight: 700; color: #590907;">
                    🛡️ Multi-Supplier Trust & Performance Benchmark Leaderboard
                </h3>
                <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #5C5E55;">
                    Ranked by explainable multi-metric trust scores computed from pricing, availability, and fulfillment rates.
                </p>
            </div>
            <span class="badge-pill badge-sage">Synthetic Benchmark</span>
        </div>
    """, unsafe_allow_html=True)

    # Render table
    table_rows = ""
    for s in leaderboard:
        code_short = s['supplier_code'].replace("SUP_", "")
        table_rows += f"""
        <tr>
            <td style="font-weight: 600;">
                <span style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: #590907; color: #E8D2B5; border-radius: 6px; font-weight: 700; font-size: 11px; margin-right: 8px;">
                    {code_short}
                </span>
                {s['supplier_name']}
            </td>
            <td>
                <span class="badge-pill badge-burgundy" style="font-size: 0.8rem;">
                    {s['trust_score']:.1f} / 100
                </span>
            </td>
            <td style="font-weight: 600; color: #2A2B27;">{s['price_competitiveness']:.0f}%</td>
            <td style="font-weight: 600; color: #065f46;">{s['booking_success_rate']:.1f}%</td>
            <td style="font-weight: 600; color: #2A2B27;">{s['availability_accuracy']:.1f}%</td>
            <td style="font-weight: 700; color: #590907;">{s['product_count']} items</td>
        </tr>
        """

    st.markdown(f"""
    <div style="overflow-x: auto;">
        <table class="custom-table">
            <thead>
                <tr>
                    <th>Supplier Partner</th>
                    <th>Trust Score</th>
                    <th>Price Competitiveness</th>
                    <th>Booking Success</th>
                    <th>Availability Acc.</th>
                    <th>Active Feed Items</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
    </div>
    """, unsafe_allow_html=True)

