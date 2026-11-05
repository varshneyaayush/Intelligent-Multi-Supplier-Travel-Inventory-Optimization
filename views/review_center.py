import streamlit as st
import datetime
from sqlalchemy.orm import Session
from core.models import DuplicateCandidate, PriceAnomalyAlert, InventoryQualityReport, AuditLog

def render_review_center(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                👤 Human-in-the-Loop Review Center &amp; Audit Trail
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Uncertain AI decisions require human oversight. Review pending items backed by an immutable audit trail.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Audit Guardrail</span>
    </div>
    """, unsafe_allow_html=True)

    pending_dups = db.query(DuplicateCandidate).filter(DuplicateCandidate.status == "PENDING").all()
    pending_anoms = db.query(PriceAnomalyAlert).filter(PriceAnomalyAlert.status == "PENDING").all()
    pending_qual = [
        q for q in db.query(InventoryQualityReport).filter(InventoryQualityReport.status == "PENDING").all()
        if len(q.enrichment_suggestions or []) > 0 or q.completeness_score < 0.80
    ]
    total_pending = len(pending_dups) + len(pending_anoms) + len(pending_qual)
    st.session_state["pending_reviews_count"] = total_pending

    audit_logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()

    tab_queue, tab_audit = st.tabs([
        f"⏳ Pending Review Queue ({total_pending})",
        f"📜 Immutable Audit Trail Log ({len(audit_logs)})"
    ])

    with tab_queue:
        if total_pending == 0:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 2.5rem 1rem;">
                <p style="font-size: 1.5rem; margin-bottom: 8px;">🎉</p>
                <h4 style="color: #065f46; margin-bottom: 6px;">Zero Pending Human Review Items!</h4>
                <p style="font-size: 0.85rem; color: #5C5E55;">All multi-modal duplicate candidates, rate anomalies, and quality reports are resolved.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 1. Pending Duplicates Section
            if pending_dups:
                st.markdown(f"""
                <div style="margin: 10px 0 8px 0; font-weight: 700; color: #590907; font-size: 0.95rem;">
                    👥 Pending Duplicate Candidates ({len(pending_dups)})
                </div>
                """, unsafe_allow_html=True)
                for d in pending_dups:
                    p_a = d.product_a
                    p_b = d.product_b
                    if not p_a or not p_b:
                        continue
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <strong>#{d.id} • {p_a.name} ({p_a.supplier.code if p_a.supplier else 'SUP'}) ⟷ {p_b.name} ({p_b.supplier.code if p_b.supplier else 'SUP'})</strong>
                            <span class="badge-pill badge-burgundy">{round(d.overall_confidence*100, 1)}% Match</span>
                        </div>
                        <div style="font-size: 0.78rem; color: #5C5E55; margin-bottom: 8px;">
                            Price Comparison: ${p_a.base_price:.2f} vs ${p_b.base_price:.2f} &bull; Geo Distance: {f"{d.geo_distance_meters:.1f}m" if d.geo_distance_meters else "Address Match"}
                        </div>
                    """, unsafe_allow_html=True)

                    d_col1, d_col2, d_col3 = st.columns([3, 1, 1])
                    with d_col1:
                        dup_note = st.text_input("Notes", key=f"rev_dup_note_{d.id}", placeholder="Reviewer rationale...", label_visibility="collapsed")
                    with d_col2:
                        if st.button("✅ Approve", key=f"rev_appr_{d.id}", use_container_width=True):
                            d.status = "APPROVED"
                            d.review_notes = dup_note
                            d.reviewed_at = datetime.datetime.utcnow()
                            audit = AuditLog(
                                action="REVIEW_DUPLICATE_APPROVED",
                                entity_type="DUPLICATE",
                                entity_id=d.id,
                                decision="APPROVED",
                                notes=dup_note,
                                details={"product_a": p_a.name, "product_b": p_b.name, "confidence": d.overall_confidence}
                            )
                            db.add(audit)
                            db.commit()
                            st.success(f"Candidate #{d.id} approved!")
                            st.rerun()
                    with d_col3:
                        if st.button("❌ Reject", key=f"rev_rej_{d.id}", use_container_width=True):
                            d.status = "REJECTED"
                            d.review_notes = dup_note
                            d.reviewed_at = datetime.datetime.utcnow()
                            audit = AuditLog(
                                action="REVIEW_DUPLICATE_REJECTED",
                                entity_type="DUPLICATE",
                                entity_id=d.id,
                                decision="REJECTED",
                                notes=dup_note,
                                details={"product_a": p_a.name, "product_b": p_b.name, "confidence": d.overall_confidence}
                            )
                            db.add(audit)
                            db.commit()
                            st.info(f"Candidate #{d.id} rejected!")
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # 2. Pending Anomalies Section
            if pending_anoms:
                st.markdown(f"""
                <div style="margin: 15px 0 8px 0; font-weight: 700; color: #590907; font-size: 0.95rem;">
                    ⚠️ Pending Price Anomaly Alerts ({len(pending_anoms)})
                </div>
                """, unsafe_allow_html=True)
                for a in pending_anoms:
                    prod = a.product
                    if not prod:
                        continue
                    diff_sign = "+" if a.price_diff_pct > 0 else ""
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <strong>#{a.id} • {prod.name} ({prod.supplier.code if prod.supplier else 'SUP'})</strong>
                            <span class="badge-pill badge-rose">{diff_sign}{a.price_diff_pct:.1f}% Variance</span>
                        </div>
                        <div style="font-size: 0.78rem; color: #5C5E55; margin-bottom: 8px;">
                            Observed: ${a.observed_price:.2f} vs Baseline: ${a.baseline_price:.2f} &bull; Diagnostic: {a.explanation}
                        </div>
                    """, unsafe_allow_html=True)

                    an_col1, an_col2, an_col3 = st.columns([3, 1, 1])
                    with an_col1:
                        anom_note = st.text_input("Notes", key=f"rev_anom_note_{a.id}", placeholder="Audit resolution rationale...", label_visibility="collapsed")
                    with an_col2:
                        if st.button("✅ Resolve", key=f"rev_res_{a.id}", use_container_width=True):
                            a.status = "RESOLVED"
                            a.reviewed_at = datetime.datetime.utcnow()
                            audit = AuditLog(
                                action="REVIEW_ANOMALY_RESOLVED",
                                entity_type="ANOMALY",
                                entity_id=a.id,
                                decision="RESOLVED",
                                notes=anom_note,
                                details={"product": prod.name, "observed": a.observed_price, "baseline": a.baseline_price}
                            )
                            db.add(audit)
                            db.commit()
                            st.success(f"Alert #{a.id} resolved!")
                            st.rerun()
                    with an_col3:
                        if st.button("🚫 Dismiss", key=f"rev_dism_{a.id}", use_container_width=True):
                            a.status = "DISMISSED"
                            a.reviewed_at = datetime.datetime.utcnow()
                            audit = AuditLog(
                                action="REVIEW_ANOMALY_DISMISSED",
                                entity_type="ANOMALY",
                                entity_id=a.id,
                                decision="DISMISSED",
                                notes=anom_note,
                                details={"product": prod.name, "observed": a.observed_price, "baseline": a.baseline_price}
                            )
                            db.add(audit)
                            db.commit()
                            st.info(f"Alert #{a.id} dismissed.")
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # 3. Pending Quality Reports
            if pending_qual:
                st.markdown(f"""
                <div style="margin: 15px 0 8px 0; font-weight: 700; color: #590907; font-size: 0.95rem;">
                    ✨ Content Quality Enrichment Queue ({len(pending_qual)})
                </div>
                """, unsafe_allow_html=True)
                for q in pending_qual:
                    prod = q.product
                    if not prod:
                        continue
                    sug_count = len(q.enrichment_suggestions or [])
                    st.markdown(f"""
                    <div class="glass-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <strong>#{q.id} • {prod.name}</strong>
                            <span class="badge-pill badge-cream">{round(q.completeness_score*100)}% Score &bull; {sug_count} Grounded Suggestions</span>
                        </div>
                        <div style="font-size: 0.78rem; color: #5C5E55; margin-bottom: 8px;">
                            Missing: {', '.join(q.missing_fields)}
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"✨ Apply Grounded Enrichment to '{prod.name}'", key=f"rev_qual_{q.id}"):
                        applied = []
                        for item in (q.enrichment_suggestions or []):
                            field = item.get("field")
                            val = item.get("suggested_value")
                            if field == "amenities" and isinstance(val, list):
                                prod.amenities = list(set((prod.amenities or []) + val))
                                applied.append("amenities")
                            elif field == "inclusions" and isinstance(val, list):
                                prod.inclusions = list(set((prod.inclusions or []) + val))
                                applied.append("inclusions")
                        q.completeness_score = min(1.0, q.completeness_score + 0.15)
                        prod.data_completeness_score = q.completeness_score
                        q.status = "ENRICHED"
                        q.reviewed_at = datetime.datetime.utcnow()
                        audit = AuditLog(
                            action="APPLY_CONTENT_ENRICHMENT",
                            entity_type="QUALITY",
                            entity_id=q.id,
                            decision="ENRICHED",
                            details={"product": prod.name, "applied": applied}
                        )
                        db.add(audit)
                        db.commit()
                        st.success(f"Enriched {prod.name}!")
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    with tab_audit:
        st.markdown("""
        <div class="glass-card">
            <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
                📜 Historical Audit Trail Log
            </h3>
            <p style="margin: 0 0 12px 0; font-size: 0.8rem; color: #5C5E55;">
                Every human approval, rejection, and AI enrichment action is recorded with an immutable timestamp.
            </p>
        """, unsafe_allow_html=True)

        if not audit_logs:
            st.info("No audit log events recorded yet. Action a pending review item above to generate audit entries.")
        else:
            table_rows = ""
            for log in audit_logs:
                dt_str = log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "N/A"
                dec_cls = "badge-emerald" if log.decision in ["APPROVED", "RESOLVED", "ENRICHED"] else "badge-rose"
                notes_str = log.notes or "—"
                table_rows += f"""
                <tr>
                    <td style="font-size: 0.75rem; color: #75776C;">{dt_str}</td>
                    <td><code>{log.action}</code></td>
                    <td><span class="badge-pill badge-sage">{log.entity_type} #{log.entity_id}</span></td>
                    <td><span class="badge-pill {dec_cls}">{log.decision}</span></td>
                    <td style="font-size: 0.78rem;">{notes_str}</td>
                </tr>
                """
            st.markdown(f"""
            <div style="overflow-x: auto;">
                <table class="custom-table">
                    <thead>
                        <tr>
                            <th>Timestamp (UTC)</th>
                            <th>Action</th>
                            <th>Entity</th>
                            <th>Decision</th>
                            <th>Reviewer Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

