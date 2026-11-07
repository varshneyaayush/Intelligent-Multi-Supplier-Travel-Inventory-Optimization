import streamlit as st
import datetime
from sqlalchemy.orm import Session
from core.models import DuplicateCandidate, AuditLog

def render_duplicates(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                👥 Multimodal Duplicate Detection Engine
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Ensemble pipeline combining token distance, Haversine geospatial proximity, and Sentence-Transformers semantic embeddings.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Active Ensembling</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Filter Bar
    f_col1, f_col2, _ = st.columns([1.5, 1.5, 2])

    with f_col1:
        class_options = ["ALL", "HIGH_CONFIDENCE", "POSSIBLE_REVIEW", "UNLIKELY"]
        class_labels = [
            "All Confidence Levels",
            "🟢 High Confidence (≥85%)",
            "🟡 Possible Review (60-84%)",
            "⚪ Unlikely (<60%)"
        ]
        class_idx = class_options.index(st.session_state.get("dup_classification_filter", "ALL"))
        selected_class = st.selectbox(
            "Match Classification",
            options=class_options,
            format_func=lambda x: class_labels[class_options.index(x)],
            index=class_idx,
            key="dup_class_select"
        )
        st.session_state["dup_classification_filter"] = selected_class

    with f_col2:
        status_options = ["ALL", "PENDING", "APPROVED", "REJECTED"]
        status_labels = ["All Statuses", "⏳ Pending Review", "✅ Approved Matches", "❌ Rejected Matches"]
        status_idx = status_options.index(st.session_state.get("dup_status_filter", "PENDING"))
        selected_status = st.selectbox(
            "Review Status",
            options=status_options,
            format_func=lambda x: status_labels[status_options.index(x)],
            index=status_idx,
            key="dup_status_select"
        )
        st.session_state["dup_status_filter"] = selected_status

    # 2. Database Query
    query = db.query(DuplicateCandidate)
    if selected_class != "ALL":
        query = query.filter(DuplicateCandidate.match_classification == selected_class)
    if selected_status != "ALL":
        query = query.filter(DuplicateCandidate.status == selected_status)

    candidates = query.order_by(DuplicateCandidate.overall_confidence.desc()).all()

    st.markdown(f"""
    <div style="margin: 10px 0 15px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Found <strong>{len(candidates)}</strong> candidate duplicate pairs
    </div>
    """, unsafe_allow_html=True)

    if not candidates:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2.5rem 1rem;">
            <p style="font-size: 1.5rem; margin-bottom: 8px;">✨</p>
            <h4 style="color: #590907; margin-bottom: 6px;">No duplicate candidate pairs found</h4>
            <p style="font-size: 0.85rem; color: #5C5E55;">Try selecting a different confidence level or review status.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 3. Render Duplicate Comparison Pairs
    for c in candidates:
        prod_a = c.product_a
        prod_b = c.product_b
        if not prod_a or not prod_b:
            continue

        supp_a = prod_a.supplier.name if prod_a.supplier else "Supplier A"
        supp_b = prod_b.supplier.name if prod_b.supplier else "Supplier B"
        supp_code_a = prod_a.supplier.code if prod_a.supplier else "SUP_A"
        supp_code_b = prod_b.supplier.code if prod_b.supplier else "SUP_B"

        conf_pct = round(c.overall_confidence * 100, 1)
        
        # Classification pill
        if c.match_classification == "HIGH_CONFIDENCE":
            class_pill = '<span class="badge-pill badge-emerald">HIGH CONFIDENCE MATCH</span>'
        elif c.match_classification == "POSSIBLE_REVIEW":
            class_pill = '<span class="badge-pill badge-amber">POSSIBLE DUPLICATE (REVIEW REQUIRED)</span>'
        else:
            class_pill = '<span class="badge-pill badge-sage">UNLIKELY MATCH</span>'

        status_pill = (
            '<span class="badge-pill badge-amber">PENDING</span>' if c.status == "PENDING"
            else ('<span class="badge-pill badge-emerald">APPROVED</span>' if c.status == "APPROVED"
            else '<span class="badge-pill badge-rose">REJECTED</span>')
        )

        evidence = c.evidence_breakdown or {}
        geo_notes = evidence.get("geo_proximity_notes", "Geo coordinates evaluated")
        sem_model = evidence.get("semantic_model", "Sentence Transformers / TF-IDF")

        coords_a = f"({prod_a.latitude:.4f}, {prod_a.longitude:.4f})" if (prod_a.latitude is not None and prod_a.longitude is not None) else "Coordinates Missing"
        coords_b = f"({prod_b.latitude:.4f}, {prod_b.longitude:.4f})" if (prod_b.latitude is not None and prod_b.longitude is not None) else "Coordinates Missing"
        price_str_a = f"${prod_a.base_price:.2f}" if prod_a.base_price is not None else "Price N/A"
        price_str_b = f"${prod_b.base_price:.2f}" if prod_b.base_price is not None else "Price N/A"

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(165,167,155,0.3); padding-bottom: 10px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    {class_pill}
                    {status_pill}
                    <span style="font-size: 0.72rem; color: #75776C;">Candidate Pair #{c.id}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #75776C;">Match Confidence:</span>
                    <strong style="font-size: 1.15rem; color: #590907; margin-left: 6px;">{conf_pct}%</strong>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 14px;">
                <!-- Product A -->
                <div style="background: rgba(253,252,249,0.7); border: 1px solid rgba(232,210,181,0.7); border-radius: 12px; padding: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span class="badge-pill badge-burgundy">{supp_code_a} &bull; {supp_a}</span>
                        <strong style="font-size: 1.1rem; color: #590907;">{price_str_a}</strong>
                    </div>
                    <h4 style="margin: 4px 0 6px 0; color: #2A2B27; font-size: 0.95rem; font-weight: 700;">
                        {prod_a.name}
                    </h4>
                    <p style="margin: 0 0 4px 0; font-size: 0.75rem; color: #5C5E55;">
                        📍 {prod_a.address or 'Address not given'}, {prod_a.city} &bull; {coords_a}
                    </p>
                    <p style="margin: 0; font-size: 0.75rem; color: #75776C;">
                        <strong>Detail:</strong> {prod_a.room_category or prod_a.activity_type or 'Standard'} &bull; <strong>Policy:</strong> {prod_a.cancellation_policy}
                    </p>
                </div>
                
                <!-- Product B -->
                <div style="background: rgba(253,252,249,0.7); border: 1px solid rgba(232,210,181,0.7); border-radius: 12px; padding: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span class="badge-pill badge-burgundy">{supp_code_b} &bull; {supp_b}</span>
                        <strong style="font-size: 1.1rem; color: #590907;">{price_str_b}</strong>
                    </div>
                    <h4 style="margin: 4px 0 6px 0; color: #2A2B27; font-size: 0.95rem; font-weight: 700;">
                        {prod_b.name}
                    </h4>
                    <p style="margin: 0 0 4px 0; font-size: 0.75rem; color: #5C5E55;">
                        📍 {prod_b.address or 'Address not given'}, {prod_b.city} &bull; {coords_b}
                    </p>
                    <p style="margin: 0; font-size: 0.75rem; color: #75776C;">
                        <strong>Detail:</strong> {prod_b.room_category or prod_b.activity_type or 'Standard'} &bull; <strong>Policy:</strong> {prod_b.cancellation_policy}
                    </p>
                </div>
            </div>
            
            <!-- Multi-modal score progress bar cards -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 12px; font-size: 0.75rem;">
                <div style="background: rgba(232,210,181,0.3); padding: 8px 10px; border-radius: 8px;">
                    <div style="color: #75776C; font-weight: 600;">Name Similarity</div>
                    <div style="font-weight: 800; font-size: 0.95rem; color: #590907;">{evidence.get('name_similarity_pct', 0)}%</div>
                </div>
                <div style="background: rgba(232,210,181,0.3); padding: 8px 10px; border-radius: 8px;">
                    <div style="color: #75776C; font-weight: 600;">Geo Proximity</div>
                    <div style="font-weight: 800; font-size: 0.85rem; color: #065f46;">{geo_notes}</div>
                </div>
                <div style="background: rgba(232,210,181,0.3); padding: 8px 10px; border-radius: 8px;">
                    <div style="color: #75776C; font-weight: 600;">Semantic Match</div>
                    <div style="font-weight: 800; font-size: 0.95rem; color: #590907;">{evidence.get('semantic_similarity_pct', 0)}%</div>
                </div>
                <div style="background: rgba(232,210,181,0.3); padding: 8px 10px; border-radius: 8px;">
                    <div style="color: #75776C; font-weight: 600;">Attribute Match</div>
                    <div style="font-weight: 800; font-size: 0.95rem; color: #590907;">{evidence.get('attribute_similarity_pct', 0)}%</div>
                </div>
            </div>
            
            <p style="margin: 0 0 10px 0; font-size: 0.78rem; color: #43443E; background: rgba(165,167,155,0.15); padding: 8px 12px; border-radius: 8px;">
                💡 <strong>AI Rationale:</strong> {evidence.get('summary_explanation', 'High multi-modal alignment across naming, geo proximity, and content.')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Human Review Action Section
        if c.status == "PENDING":
            r_col1, r_col2, r_col3 = st.columns([3, 1, 1])
            with r_col1:
                notes = st.text_input(
                    "Reviewer Notes",
                    key=f"dup_note_{c.id}",
                    placeholder="Enter verification notes (optional)...",
                    label_visibility="collapsed"
                )
            with r_col2:
                if st.button("✅ Approve Match", key=f"appr_{c.id}", use_container_width=True):
                    c.status = "APPROVED"
                    c.review_notes = notes
                    c.reviewed_at = datetime.datetime.utcnow()
                    audit = AuditLog(
                        action="REVIEW_DUPLICATE_APPROVED",
                        entity_type="DUPLICATE",
                        entity_id=c.id,
                        decision="APPROVED",
                        notes=notes,
                        details={"product_a": prod_a.name, "product_b": prod_b.name, "confidence": c.overall_confidence}
                    )
                    db.add(audit)
                    db.commit()
                    st.success(f"Candidate #{c.id} approved!")
                    st.rerun()
            with r_col3:
                if st.button("❌ Reject Match", key=f"rej_{c.id}", use_container_width=True):
                    c.status = "REJECTED"
                    c.review_notes = notes
                    c.reviewed_at = datetime.datetime.utcnow()
                    audit = AuditLog(
                        action="REVIEW_DUPLICATE_REJECTED",
                        entity_type="DUPLICATE",
                        entity_id=c.id,
                        decision="REJECTED",
                        notes=notes,
                        details={"product_a": prod_a.name, "product_b": prod_b.name, "confidence": c.overall_confidence}
                    )
                    db.add(audit)
                    db.commit()
                    st.info(f"Candidate #{c.id} rejected!")
                    st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

