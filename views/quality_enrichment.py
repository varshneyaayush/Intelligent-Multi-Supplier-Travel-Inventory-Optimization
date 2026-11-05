import streamlit as st
import datetime
from sqlalchemy.orm import Session
from core.models import InventoryQualityReport, AuditLog

def render_quality_enrichment(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                ✨ AI-Powered Inventory Quality &amp; Content Enrichment
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Audits field completeness and generates non-hallucinatory enrichments strictly extracted from verified descriptions.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Grounded AI</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Filters
    f_col1, f_col2, _ = st.columns([1.5, 1.5, 2])
    with f_col1:
        tier_filter = st.selectbox(
            "Completeness Tier",
            options=["ALL", "NEEDS_ATTENTION", "FAIR", "GOOD", "EXCELLENT"],
            format_func=lambda x: {
                "ALL": "All Quality Tiers",
                "NEEDS_ATTENTION": "🔴 Needs Attention (<50%)",
                "FAIR": "🟡 Fair (50-74%)",
                "GOOD": "🟢 Good (75-89%)",
                "EXCELLENT": "⭐ Excellent (≥90%)"
            }[x],
            key="qual_tier_select"
        )
    with f_col2:
        status_filter = st.selectbox(
            "Enrichment Status",
            options=["ALL", "PENDING", "ENRICHED"],
            format_func=lambda x: {"ALL": "All Records", "PENDING": "⏳ Pending Enrichment", "ENRICHED": "✅ Enriched"}[x],
            key="qual_status_select"
        )

    # 2. Database Query
    query = db.query(InventoryQualityReport)
    if status_filter != "ALL":
        query = query.filter(InventoryQualityReport.status == status_filter)

    reports = query.order_by(InventoryQualityReport.completeness_score.asc()).all()

    # Filter tier in memory for clean range mapping
    filtered_reports = []
    for r in reports:
        score = r.completeness_score
        if tier_filter == "NEEDS_ATTENTION" and score >= 0.50:
            continue
        if tier_filter == "FAIR" and not (0.50 <= score < 0.75):
            continue
        if tier_filter == "GOOD" and not (0.75 <= score < 0.90):
            continue
        if tier_filter == "EXCELLENT" and score < 0.90:
            continue
        filtered_reports.append(r)

    st.markdown(f"""
    <div style="margin: 10px 0 15px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Audited <strong>{len(filtered_reports)}</strong> inventory quality reports
    </div>
    """, unsafe_allow_html=True)

    if not filtered_reports:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2.5rem 1rem;">
            <p style="font-size: 1.5rem; margin-bottom: 8px;">✨</p>
            <h4 style="color: #590907; margin-bottom: 6px;">All inventory items meet quality standards</h4>
            <p style="font-size: 0.85rem; color: #5C5E55;">No records match the selected filtering tier.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 3. Render Quality Cards
    for r in filtered_reports:
        p = r.product
        if not p:
            continue

        score_pct = round(r.completeness_score * 100)
        if score_pct >= 90:
            tier_badge = '<span class="badge-pill badge-emerald">EXCELLENT (90-100%)</span>'
            bar_color = "#065f46"
        elif score_pct >= 75:
            tier_badge = '<span class="badge-pill badge-cream">GOOD (75-89%)</span>'
            bar_color = "#8E9084"
        elif score_pct >= 50:
            tier_badge = '<span class="badge-pill badge-amber">FAIR (50-74%)</span>'
            bar_color = "#d97706"
        else:
            tier_badge = '<span class="badge-pill badge-rose">NEEDS ATTENTION (&lt;50%)</span>'
            bar_color = "#b91c1c"

        status_badge = (
            '<span class="badge-pill badge-amber">PENDING</span>' if r.status == "PENDING"
            else '<span class="badge-pill badge-emerald">ENRICHED</span>'
        )

        missing_tags = "".join([f'<span class="badge-pill badge-rose" style="margin-right: 4px; margin-bottom: 4px; font-size: 0.7rem;">Missing: {f}</span>' for f in r.missing_fields])
        suggestions = r.enrichment_suggestions or []

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(165,167,155,0.3); padding-bottom: 10px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {tier_badge}
                    {status_badge}
                    <span class="badge-pill badge-sage">{p.supplier.code if p.supplier else 'SUP'} &bull; {p.supplier.name if p.supplier else 'Supplier'}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #75776C;">Completeness:</span>
                    <strong style="font-size: 1.2rem; color: {bar_color}; margin-left: 6px;">{score_pct}%</strong>
                </div>
            </div>
            
            <h3 style="font-size: 1.15rem; margin: 0 0 4px 0; color: #590907; font-weight: 700;">
                {p.name}
            </h3>
            <div style="font-size: 0.8rem; color: #5C5E55; margin-bottom: 10px;">
                📍 {p.city or 'City unknown'}, {p.country or 'Country'} &bull; Type: <strong>{p.product_type}</strong> &bull; Price: <strong>${p.base_price:.2f}</strong>
            </div>
            
            <!-- Progress Bar -->
            <div style="background: rgba(165,167,155,0.3); height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 12px;">
                <div style="background: {bar_color}; width: {score_pct}%; height: 100%; border-radius: 4px;"></div>
            </div>
            
            <!-- Missing Fields -->
            <div style="margin-bottom: 12px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #75776C; margin-right: 6px;">Audited Deficiencies:</span>
                {missing_tags or '<span class="badge-pill badge-emerald" style="font-size: 0.7rem;">None Detected</span>'}
            </div>
            
            <p style="margin: 0 0 10px 0; font-size: 0.78rem; color: #43443E; background: rgba(165,167,155,0.12); padding: 8px 12px; border-radius: 8px;">
                <strong>Property Description:</strong> {p.description or 'No property description provided in supplier payload.'}
            </p>
        """, unsafe_allow_html=True)

        # Grounded suggestions
        if suggestions:
            for s_idx, sug in enumerate(suggestions):
                sug_field = sug.get("field", "Attribute")
                sug_val = sug.get("suggested_value", [])
                val_str = ", ".join(sug_val) if isinstance(sug_val, list) else str(sug_val)
                grounding = sug.get("grounding_source", "Extracted from description")
                conf = sug.get("confidence", "High")

                st.markdown(f"""
                <div style="background: rgba(209, 250, 229, 0.4); border: 1px solid rgba(110, 231, 183, 0.6); border-radius: 10px; padding: 10px 14px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <strong style="color: #065f46; font-size: 0.85rem;">💡 Grounded AI Enrichment: {sug_field.upper()}</strong>
                        <span class="badge-pill badge-emerald" style="font-size: 0.68rem;">{conf}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #065f46; margin-bottom: 4px;">
                        Suggested Values: <strong>{val_str}</strong>
                    </div>
                    <div style="font-size: 0.72rem; color: #047857; font-style: italic;">
                        Source: {grounding}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if r.status == "PENDING":
                if st.button(f"✨ Apply Grounded Enrichment to '{p.name}'", key=f"apply_sug_{r.id}"):
                    applied_fields = []
                    for item in suggestions:
                        field = item.get("field")
                        val = item.get("suggested_value")
                        if field == "amenities" and isinstance(val, list):
                            existing = p.amenities or []
                            p.amenities = list(set(existing + val))
                            applied_fields.append("amenities")
                        elif field == "inclusions" and isinstance(val, list):
                            existing = p.inclusions or []
                            p.inclusions = list(set(existing + val))
                            applied_fields.append("inclusions")

                    r.completeness_score = min(1.0, r.completeness_score + 0.15)
                    p.data_completeness_score = r.completeness_score
                    r.status = "ENRICHED"
                    r.reviewed_at = datetime.datetime.utcnow()

                    audit = AuditLog(
                        action="APPLY_CONTENT_ENRICHMENT",
                        entity_type="QUALITY",
                        entity_id=r.id,
                        decision="ENRICHED",
                        details={"product_name": p.name, "applied_fields": applied_fields}
                    )
                    db.add(audit)
                    db.commit()
                    st.success(f"Enrichment applied! Completeness score elevated to {round(r.completeness_score*100)}%.")
                    st.rerun()

        st.markdown("</div><div style='height: 10px;'></div>", unsafe_allow_html=True)

