import streamlit as st
from sqlalchemy.orm import Session
from core.models import OptimizationRecommendation, AuditLog

def render_recommendations(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                💡 AI-Powered Inventory Optimization Recommendations
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Actionable operational recommendations synthesized directly from live inventory findings with explicit business rationale.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Actionable Insights</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Category Filter
    cat_options = ["ALL", "DUPLICATE_CONSOLIDATION", "PRICE_OPTIMIZATION", "SUPPLIER_REBALANCING", "CONTENT_ENRICHMENT"]
    cat_labels = [
        "All Optimization Categories",
        "👥 Duplicate Consolidation Directives",
        "💰 Price & Margin Optimization",
        "🛡️ Supplier Trust Rebalancing",
        "✨ Content Quality Enrichment"
    ]
    selected_cat = st.selectbox(
        "Recommendation Category",
        options=cat_options,
        format_func=lambda x: cat_labels[cat_options.index(x)],
        key="rec_cat_select"
    )

    # 2. Database Query
    query = db.query(OptimizationRecommendation).filter(OptimizationRecommendation.status == "ACTIVE")
    if selected_cat != "ALL":
        query = query.filter(OptimizationRecommendation.category == selected_cat)
    
    recommendations = query.order_by(OptimizationRecommendation.id.asc()).all()

    st.markdown(f"""
    <div style="margin: 10px 0 15px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Active Optimization Directives: <strong>{len(recommendations)}</strong>
    </div>
    """, unsafe_allow_html=True)

    if not recommendations:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2.5rem 1rem;">
            <p style="font-size: 1.5rem; margin-bottom: 8px;">🎉</p>
            <h4 style="color: #065f46; margin-bottom: 6px;">All Optimization Directives Addressed!</h4>
            <p style="font-size: 0.85rem; color: #5C5E55;">Platform inventory is currently performing at optimum efficiency.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 3. Render Cards
    for r in recommendations:
        cat_badge = r.category.replace("_", " ")
        if "DUPLICATE" in r.category:
            cat_cls = "badge-emerald"
        elif "PRICE" in r.category:
            cat_cls = "badge-rose"
        elif "SUPPLIER" in r.category:
            cat_cls = "badge-burgundy"
        else:
            cat_cls = "badge-cream"

        evidence = r.supporting_evidence or {}
        evidence_items = "".join([f'<li style="margin-bottom: 3px; font-size: 0.78rem;"><strong>{k.replace("_", " ").title()}:</strong> {v}</li>' for k, v in evidence.items()])

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(165,167,155,0.3); padding-bottom: 10px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="badge-pill {cat_cls}">{cat_badge}</span>
                    <span class="badge-pill badge-cream">Confidence: {r.confidence_level}</span>
                    <span style="font-size: 0.72rem; color: #75776C;">Directive #{r.id}</span>
                </div>
                <span class="badge-pill badge-emerald">ACTIVE DIRECTIVE</span>
            </div>
            
            <h3 style="font-size: 1.2rem; margin: 0 0 6px 0; color: #590907; font-weight: 700;">
                {r.title}
            </h3>
            
            <!-- Directive Recommendation Box -->
            <div style="background: rgba(232,210,181,0.45); border-left: 4px solid #590907; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; font-size: 0.88rem; color: #2A2B27; font-weight: 600;">
                🎯 Operational Action: {r.recommendation}
            </div>
            
            <div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 14px; margin-bottom: 12px;">
                <div style="background: rgba(165,167,155,0.12); padding: 10px 14px; border-radius: 10px;">
                    <div style="font-weight: 700; font-size: 0.8rem; color: #590907; margin-bottom: 4px;">
                        🔍 AI Analysis &amp; Rationale
                    </div>
                    <p style="margin: 0; font-size: 0.8rem; color: #43443E; line-height: 1.45;">
                        {r.why_recommended}
                    </p>
                </div>
                
                <div style="background: rgba(209, 250, 229, 0.35); border: 1px solid rgba(110, 231, 183, 0.6); padding: 10px 14px; border-radius: 10px;">
                    <div style="font-weight: 700; font-size: 0.8rem; color: #065f46; margin-bottom: 4px;">
                        📈 Projected Business Benefit
                    </div>
                    <p style="margin: 0; font-size: 0.8rem; color: #065f46; line-height: 1.45;">
                        {r.expected_benefit}
                    </p>
                </div>
            </div>
            
            <!-- Supporting Evidence -->
            <div style="background: rgba(253,252,249,0.9); border: 1px solid rgba(232,210,181,0.7); border-radius: 8px; padding: 8px 12px; margin-bottom: 12px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #75776C;">Supporting Evidence:</span>
                <ul style="margin: 4px 0 0 0; padding-left: 18px; color: #2A2B27;">
                    {evidence_items}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        btn_col1, btn_col2, _ = st.columns([1.5, 1.5, 3])
        with btn_col1:
            if st.button("🚀 Mark Applied", key=f"rec_app_{r.id}", use_container_width=True):
                r.status = "APPLIED"
                audit = AuditLog(
                    action="RECOMMENDATION_APPLIED",
                    entity_type="RECOMMENDATION",
                    entity_id=r.id,
                    decision="APPLIED",
                    details={"title": r.title}
                )
                db.add(audit)
                db.commit()
                st.success(f"Directive #{r.id} marked as applied!")
                st.rerun()
        with btn_col2:
            if st.button("🚫 Dismiss Directive", key=f"rec_dism_{r.id}", use_container_width=True):
                r.status = "DISMISSED"
                audit = AuditLog(
                    action="RECOMMENDATION_DISMISSED",
                    entity_type="RECOMMENDATION",
                    entity_id=r.id,
                    decision="DISMISSED",
                    details={"title": r.title}
                )
                db.add(audit)
                db.commit()
                st.info(f"Directive #{r.id} dismissed.")
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

