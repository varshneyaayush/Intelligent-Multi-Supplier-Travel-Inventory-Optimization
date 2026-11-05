import streamlit as st
import plotly.graph_objects as go
from sqlalchemy.orm import Session
from core.models import Supplier, SupplierMetric
from ai.supplier_intelligence import supplier_engine

def render_supplier_intelligence(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                🛡️ Supplier Intelligence &amp; Trust Scoring Engine
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Multi-dimensional supplier reliability index calculated from fulfillment rates, price competitiveness, and data completeness.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Explainable AI Model</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Interactive Trust Weight Customizer
    with st.expander("⚙️ Customize Supplier Trust Scoring Weights", expanded=False):
        st.markdown("<p style='font-size: 0.82rem; color: #5C5E55;'>Adjust the relative importance of fulfillment metrics. Weights will be normalized to sum to 100%.</p>", unsafe_allow_html=True)
        w_cols = st.columns(5)
        with w_cols[0]:
            w_price = st.slider("Price Competitiveness", 0, 50, int(st.session_state["supplier_trust_weights"]["price_competitiveness"]*100), step=5, key="slider_sup_price")
        with w_cols[1]:
            w_succ = st.slider("Booking Success", 0, 50, int(st.session_state["supplier_trust_weights"]["booking_success_rate"]*100), step=5, key="slider_sup_succ")
        with w_cols[2]:
            w_avail = st.slider("Availability Acc.", 0, 50, int(st.session_state["supplier_trust_weights"]["availability_accuracy"]*100), step=5, key="slider_sup_avail")
        with w_cols[3]:
            w_cancel = st.slider("Cancellation Rel.", 0, 50, int(st.session_state["supplier_trust_weights"]["cancellation_reliability"]*100), step=5, key="slider_sup_cancel")
        with w_cols[4]:
            w_data = st.slider("Data Completeness", 0, 50, int(st.session_state["supplier_trust_weights"]["data_completeness"]*100), step=5, key="slider_sup_data")

        total_sum = (w_price + w_succ + w_avail + w_cancel + w_data) or 100
        new_weights = {
            "price_competitiveness": w_price / total_sum,
            "booking_success_rate": w_succ / total_sum,
            "availability_accuracy": w_avail / total_sum,
            "cancellation_reliability": w_cancel / total_sum,
            "data_completeness": w_data / total_sum
        }
        st.session_state["supplier_trust_weights"] = new_weights

        if st.button("🔄 Recalculate All Supplier Scores with Custom Weights"):
            suppliers_all = db.query(Supplier).all()
            for s in suppliers_all:
                if s.metrics:
                    m_dict = {
                        "price_competitiveness": s.metrics.price_competitiveness,
                        "booking_success_rate": s.metrics.booking_success_rate,
                        "availability_accuracy": s.metrics.availability_accuracy,
                        "cancellation_reliability": s.metrics.cancellation_reliability,
                        "data_completeness": s.metrics.data_completeness,
                        "response_time_ms": s.metrics.response_time_ms,
                        "is_synthetic": s.metrics.is_synthetic
                    }
                    eval_res = supplier_engine.compute_trust_score(m_dict, new_weights)
                    s.metrics.trust_score = eval_res["trust_score"]
                    s.metrics.strengths = eval_res["strengths"]
                    s.metrics.weaknesses = eval_res["weaknesses"]
                    s.reliability_tier = eval_res["tier"]
            db.commit()
            st.success("Supplier trust scores updated with custom weights!")
            st.rerun()

    # 2. Database Query
    suppliers = db.query(Supplier).all()
    if not suppliers:
        st.warning("No suppliers registered in the database.")
        return

    # 3. Radar Chart Comparing Suppliers
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
            📊 Multi-Supplier Performance Dimension Radar
        </h3>
    """, unsafe_allow_html=True)

    categories = ['Price Comp.', 'Booking Success', 'Availability Acc.', 'Cancellation Rel.', 'Data Completeness']
    radar_colors = ['#590907', '#A5A79B', '#DEC099', '#75776C']
    fig_radar = go.Figure()

    for idx, s in enumerate(suppliers):
        if not s.metrics:
            continue
        vals = [
            s.metrics.price_competitiveness,
            s.metrics.booking_success_rate,
            s.metrics.availability_accuracy,
            s.metrics.cancellation_reliability,
            s.metrics.data_completeness
        ]
        vals.append(vals[0]) # close radar polygon
        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories + [categories[0]],
            fill='toself',
            name=f"{s.code} ({s.name[:18]})",
            line_color=radar_colors[idx % len(radar_colors)]
        ))

    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[50, 100], gridcolor="rgba(165,167,155,0.3)"),
            bgcolor='rgba(0,0,0,0)'
        ),
        height=320,
        margin=dict(l=30, r=30, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans, sans-serif", size=10, color="#2A2B27"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Supplier Intelligence Detail Cards
    st.markdown(f"""
    <div style="margin: 15px 0 10px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Detailed Profiles for <strong>{len(suppliers)}</strong> Active Supplier Partners
    </div>
    """, unsafe_allow_html=True)

    for s in suppliers:
        m = s.metrics
        if not m:
            continue

        score = m.trust_score
        tier_cls = "badge-emerald" if score >= 85 else ("badge-amber" if score >= 70 else "badge-rose")
        code_short = s.code.replace("SUP_", "")

        strengths_html = "".join([f'<li style="margin-bottom: 4px; font-size: 0.78rem; color: #065f46;">✔ {str(item)}</li>' for item in (m.strengths or [])])
        weaknesses_html = "".join([f'<li style="margin-bottom: 4px; font-size: 0.78rem; color: #9f1239;">⚠ {str(item)}</li>' for item in (m.weaknesses or [])])

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid rgba(165,167,155,0.3); padding-bottom: 10px; margin-bottom: 12px; flex-wrap: wrap;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: #590907; color: #E8D2B5; border-radius: 8px; font-weight: 800; font-size: 13px;">
                            {code_short}
                        </span>
                        <h3 style="margin: 0; font-size: 1.15rem; color: #590907; font-weight: 700;">
                            {s.name}
                        </h3>
                    </div>
                    <div style="font-size: 0.75rem; color: #5C5E55; margin-top: 4px;">
                        Code: <code>{s.code}</code> &bull; Country: <strong>{s.country}</strong> &bull; Contact: <em>{s.contact_email or 'N/A'}</em>
                    </div>
                </div>
                
                <div style="text-align: right;">
                    <span class="badge-pill {tier_cls}" style="margin-bottom: 4px; display: inline-block;">
                        {s.reliability_tier}
                    </span>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #590907;">
                        {score:.1f} <span style="font-size: 0.8rem; color: #75776C;">/ 100</span>
                    </div>
                </div>
            </div>
            
            <!-- Metrics 6-pack -->
            <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 14px; text-align: center;">
                <div style="background: rgba(232,210,181,0.35); padding: 8px 6px; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #75776C; font-weight: 600;">Price Comp.</div>
                    <div style="font-size: 1rem; font-weight: 800; color: #590907;">{m.price_competitiveness:.0f}%</div>
                </div>
                <div style="background: rgba(232,210,181,0.35); padding: 8px 6px; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #75776C; font-weight: 600;">Booking Success</div>
                    <div style="font-size: 1rem; font-weight: 800; color: #065f46;">{m.booking_success_rate:.1f}%</div>
                </div>
                <div style="background: rgba(232,210,181,0.35); padding: 8px 6px; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #75776C; font-weight: 600;">Avail. Accuracy</div>
                    <div style="font-size: 1rem; font-weight: 800; color: #590907;">{m.availability_accuracy:.1f}%</div>
                </div>
                <div style="background: rgba(232,210,181,0.35); padding: 8px 6px; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #75776C; font-weight: 600;">Cancel Reliability</div>
                    <div style="font-size: 1rem; font-weight: 800; color: #590907;">{m.cancellation_reliability:.1f}%</div>
                </div>
                <div style="background: rgba(232,210,181,0.35); padding: 8px 6px; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #75776C; font-weight: 600;">Completeness</div>
                    <div style="font-size: 1rem; font-weight: 800; color: #590907;">{m.data_completeness:.1f}%</div>
                </div>
                <div style="background: rgba(232,210,181,0.35); padding: 8px 6px; border-radius: 8px;">
                    <div style="font-size: 0.7rem; color: #75776C; font-weight: 600;">API Latency</div>
                    <div style="font-size: 1rem; font-weight: 800; color: {'#065f46' if m.response_time_ms < 250 else ('#d97706' if m.response_time_ms < 400 else '#9f1239')};">{m.response_time_ms:.0f}ms</div>
                </div>
            </div>
            
            <!-- Strengths and Weaknesses -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div style="background: rgba(209, 250, 229, 0.35); border: 1px solid rgba(110, 231, 183, 0.5); border-radius: 10px; padding: 10px;">
                    <div style="font-weight: 700; font-size: 0.82rem; color: #065f46; margin-bottom: 6px;">
                        🌟 Verified Strengths
                    </div>
                    <ul style="margin: 0; padding-left: 14px; list-style: none;">
                        {strengths_html or '<li style=\"font-size: 0.75rem; color: #75776C;\">No standout advantages documented.</li>'}
                    </ul>
                </div>
                
                <div style="background: rgba(254, 242, 242, 0.5); border: 1px solid rgba(254, 205, 211, 0.6); border-radius: 10px; padding: 10px;">
                    <div style="font-weight: 700; font-size: 0.82rem; color: #9f1239; margin-bottom: 6px;">
                        ⚠️ Operational Vulnerabilities
                    </div>
                    <ul style="margin: 0; padding-left: 14px; list-style: none;">
                        {weaknesses_html or '<li style=\"font-size: 0.75rem; color: #75776C;\">No critical defects detected.</li>'}
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

