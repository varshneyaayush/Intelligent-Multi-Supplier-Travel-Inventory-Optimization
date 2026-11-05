import streamlit as st
import datetime
from sqlalchemy.orm import Session
from core.models import PriceAnomalyAlert, AuditLog

def render_price_anomalies(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                ⚠️ Dynamic Price Anomaly Detection Engine
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Statistical anomaly detection utilizing IQR multipliers, Z-scores, and Scikit-learn Isolation Forests across supplier clusters.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">IQR &amp; Isolation Forest</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Filter Bar
    f_col1, f_col2, _ = st.columns([1.5, 1.5, 2])

    with f_col1:
        sev_options = ["ALL", "HIGH", "MEDIUM", "LOW"]
        sev_labels = ["All Severities", "🔴 High Severity", "🟡 Medium Severity", "⚪ Low Severity"]
        sev_idx = sev_options.index(st.session_state.get("anomaly_severity_filter", "ALL"))
        selected_sev = st.selectbox(
            "Anomaly Severity",
            options=sev_options,
            format_func=lambda x: sev_labels[sev_options.index(x)],
            index=sev_idx,
            key="anom_sev_select"
        )
        st.session_state["anomaly_severity_filter"] = selected_sev

    with f_col2:
        status_options = ["ALL", "PENDING", "RESOLVED", "DISMISSED"]
        status_labels = ["All Statuses", "⏳ Pending Investigation", "✅ Resolved Alerts", "🚫 Dismissed Alerts"]
        status_idx = status_options.index(st.session_state.get("anomaly_status_filter", "PENDING"))
        selected_status = st.selectbox(
            "Alert Status",
            options=status_options,
            format_func=lambda x: status_labels[status_options.index(x)],
            index=status_idx,
            key="anom_status_select"
        )
        st.session_state["anomaly_status_filter"] = selected_status

    # 2. Database Query
    query = db.query(PriceAnomalyAlert)
    if selected_sev != "ALL":
        query = query.filter(PriceAnomalyAlert.severity == selected_sev)
    if selected_status != "ALL":
        query = query.filter(PriceAnomalyAlert.status == selected_status)

    alerts = query.order_by(PriceAnomalyAlert.price_diff_pct.desc()).all()

    st.markdown(f"""
    <div style="margin: 10px 0 15px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Identified <strong>{len(alerts)}</strong> rate anomaly alerts
    </div>
    """, unsafe_allow_html=True)

    if not alerts:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2.5rem 1rem;">
            <p style="font-size: 1.5rem; margin-bottom: 8px;">✅</p>
            <h4 style="color: #590907; margin-bottom: 6px;">No price anomaly alerts match current filters</h4>
            <p style="font-size: 0.85rem; color: #5C5E55;">All supplier rates are within statistical baseline variance boundaries.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 3. Render Anomaly Cards
    for a in alerts:
        p = a.product
        if not p:
            continue

        supp_name = p.supplier.name if p.supplier else "Unknown Supplier"
        supp_code = p.supplier.code if p.supplier else "UNK"

        # Severity Pill
        if a.severity == "HIGH":
            sev_pill = '<span class="badge-pill badge-rose">HIGH SEVERITY</span>'
        elif a.severity == "MEDIUM":
            sev_pill = '<span class="badge-pill badge-amber">MEDIUM SEVERITY</span>'
        else:
            sev_pill = '<span class="badge-pill badge-sage">LOW SEVERITY</span>'

        status_pill = (
            '<span class="badge-pill badge-amber">PENDING</span>' if a.status == "PENDING"
            else ('<span class="badge-pill badge-emerald">RESOLVED</span>' if a.status == "RESOLVED"
            else '<span class="badge-pill badge-sage">DISMISSED</span>')
        )

        diff_sign = "+" if a.price_diff_pct > 0 else ""
        diff_color = "#9f1239" if a.price_diff_pct > 0 else "#b45309"

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(165,167,155,0.3); padding-bottom: 10px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {sev_pill}
                    {status_pill}
                    <span class="badge-pill badge-burgundy">{a.anomaly_type.replace('_', ' ')}</span>
                    <span style="font-size: 0.72rem; color: #75776C;">Alert #{a.id}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #75776C;">Variance:</span>
                    <strong style="font-size: 1.15rem; color: {diff_color}; margin-left: 6px;">
                        {diff_sign}{a.price_diff_pct:.1f}%
                    </strong>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr auto; gap: 16px; margin-bottom: 12px; align-items: center;">
                <div>
                    <h3 style="font-size: 1.1rem; margin: 0 0 4px 0; color: #590907; font-weight: 700;">
                        {p.name}
                    </h3>
                    <div style="font-size: 0.78rem; color: #5C5E55;">
                        Supplier: <strong>{supp_name}</strong> (<code>{supp_code}</code>) &bull; Location: {p.city}, {p.country} &bull; Policy: {p.cancellation_policy}
                    </div>
                </div>
                
                <!-- Price Comparison Pill -->
                <div style="background: rgba(232,210,181,0.45); border: 1px solid rgba(232,210,181,0.8); border-radius: 12px; padding: 10px 16px; text-align: center;">
                    <div style="font-size: 0.7rem; font-weight: 700; color: #75776C; text-transform: uppercase;">Observed vs Baseline</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #590907;">
                        ${a.observed_price:.2f} <span style="font-size: 0.8rem; font-weight: 500; color: #75776C;">vs ${a.baseline_price:.2f}</span>
                    </div>
                    <div style="font-size: 0.68rem; color: #5C5E55; margin-top: 2px;">
                        Method: {a.detection_method}
                    </div>
                </div>
            </div>
            
            <p style="margin: 0 0 10px 0; font-size: 0.8rem; color: #2A2B27; background: rgba(165,167,155,0.15); padding: 8px 12px; border-radius: 8px; line-height: 1.45;">
                🔍 <strong>Statistical Diagnostic:</strong> {a.explanation}
            </p>
        </div>
        """, unsafe_allow_html=True)

        if a.status == "PENDING":
            a_col1, a_col2, a_col3 = st.columns([3, 1, 1])
            with a_col1:
                notes = st.text_input(
                    "Resolution notes",
                    key=f"anom_note_{a.id}",
                    placeholder="Enter audit notes (e.g. rate parity verified)...",
                    label_visibility="collapsed"
                )
            with a_col2:
                if st.button("✅ Resolve Alert", key=f"res_{a.id}", use_container_width=True):
                    a.status = "RESOLVED"
                    a.reviewed_at = datetime.datetime.utcnow()
                    audit = AuditLog(
                        action="REVIEW_ANOMALY_RESOLVED",
                        entity_type="ANOMALY",
                        entity_id=a.id,
                        decision="RESOLVED",
                        notes=notes,
                        details={"product": p.name, "observed": a.observed_price, "baseline": a.baseline_price}
                    )
                    db.add(audit)
                    db.commit()
                    st.success(f"Alert #{a.id} resolved!")
                    st.rerun()
            with a_col3:
                if st.button("🚫 Dismiss Alert", key=f"dism_{a.id}", use_container_width=True):
                    a.status = "DISMISSED"
                    a.reviewed_at = datetime.datetime.utcnow()
                    audit = AuditLog(
                        action="REVIEW_ANOMALY_DISMISSED",
                        entity_type="ANOMALY",
                        entity_id=a.id,
                        decision="DISMISSED",
                        notes=notes,
                        details={"product": p.name, "observed": a.observed_price, "baseline": a.baseline_price}
                    )
                    db.add(audit)
                    db.commit()
                    st.info(f"Alert #{a.id} dismissed.")
                    st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

