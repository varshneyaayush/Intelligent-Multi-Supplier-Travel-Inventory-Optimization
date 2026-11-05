import streamlit as st
import json
from sqlalchemy.orm import Session
from core.models import InventoryProduct, Supplier

def render_inventory(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                📦 Multi-Supplier Travel Inventory Repository
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Normalized catalog of hotel accommodations and sightseeing experiences across connected suppliers.
            </p>
        </div>
        <span class="badge-pill badge-cream">Normalized Schema</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Filter Bar Controls
    f_col1, f_col2, f_col3 = st.columns([1.5, 1.5, 2])

    with f_col1:
        cat_options = ["ALL", "HOTEL", "SIGHTSEEING"]
        cat_labels = ["All Inventory", "🏨 Hotels Only", "🎟️ Sightseeing / Experiences"]
        cat_idx = cat_options.index(st.session_state.get("inventory_type_filter", "ALL"))
        selected_cat = st.selectbox(
            "Product Category",
            options=cat_options,
            format_func=lambda x: cat_labels[cat_options.index(x)],
            index=cat_idx,
            key="inv_cat_select"
        )
        st.session_state["inventory_type_filter"] = selected_cat

    with f_col2:
        suppliers = db.query(Supplier).all()
        supp_options = [0] + [s.id for s in suppliers]
        supp_labels = ["All Suppliers"] + [f"{s.code} - {s.name}" for s in suppliers]
        selected_supp = st.selectbox(
            "Supplier Feed",
            options=supp_options,
            format_func=lambda x: supp_labels[supp_options.index(x)],
            key="inv_supp_select"
        )

    with f_col3:
        search_query = st.text_input(
            "Search inventory...",
            value=st.session_state.get("inventory_search_query", ""),
            placeholder="Search hotel name, landmark, address, city...",
            key="inv_search_input"
        )
        st.session_state["inventory_search_query"] = search_query

    # 2. Database Query
    query = db.query(InventoryProduct)
    if selected_cat != "ALL":
        query = query.filter(InventoryProduct.product_type == selected_cat)
    if selected_supp != 0:
        query = query.filter(InventoryProduct.supplier_id == selected_supp)
    if search_query.strip():
        term = f"%{search_query.strip()}%"
        query = query.filter(
            (InventoryProduct.name.ilike(term)) |
            (InventoryProduct.description.ilike(term)) |
            (InventoryProduct.address.ilike(term)) |
            (InventoryProduct.city.ilike(term))
        )

    products = query.order_by(InventoryProduct.id.asc()).all()

    st.markdown(f"""
    <div style="margin: 10px 0 15px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Showing <strong>{len(products)}</strong> matching inventory items
    </div>
    """, unsafe_allow_html=True)

    if not products:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2.5rem 1rem;">
            <p style="font-size: 1.5rem; margin-bottom: 8px;">🔍</p>
            <h4 style="color: #590907; margin-bottom: 6px;">No inventory records match your criteria</h4>
            <p style="font-size: 0.85rem; color: #5C5E55;">Try clearing your search terms or upload a new supplier feed.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 3. Product Cards
    for p in products:
        is_hotel = (p.product_type == "HOTEL")
        type_badge = "🏨 HOTEL" if is_hotel else "🎟️ SIGHTSEEING"
        type_badge_cls = "badge-burgundy" if is_hotel else "badge-cream"
        supp_name = p.supplier.name if p.supplier else "Unknown Supplier"
        supp_code = p.supplier.code if p.supplier else "UNK"
        
        # Tags formatting
        if is_hotel:
            tags = p.amenities or []
            details_line = f"<strong>Room:</strong> {p.room_category or 'Standard'} &bull; <strong>Stars:</strong> {'⭐' * int(p.star_rating or 4)}"
        else:
            tags = p.inclusions or []
            dur_str = f"{p.duration_hours:.1f}h" if p.duration_hours else "Flexible"
            details_line = f"<strong>Category:</strong> {p.activity_type or 'Guided Tour'} &bull; <strong>Duration:</strong> {dur_str} &bull; <strong>Meeting:</strong> {p.meeting_point or 'Varies'}"

        tags_html = "".join([f'<span class="badge-pill badge-sage" style="margin-right: 4px; margin-bottom: 4px; font-size: 0.68rem;">{t}</span>' for t in tags[:6]])
        if len(tags) > 6:
            tags_html += f'<span class="badge-pill badge-cream" style="font-size: 0.68rem;">+{len(tags)-6} more</span>'

        coords_str = f"({p.latitude:.4f}, {p.longitude:.4f})" if (p.latitude is not None and p.longitude is not None) else "Coordinates Missing"
        comp_pct = round((p.data_completeness_score or 1.0) * 100)
        comp_color = "#065f46" if comp_pct >= 85 else ("#d97706" if comp_pct >= 65 else "#b91c1c")

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 280px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span class="badge-pill {type_badge_cls}">{type_badge}</span>
                        <span class="badge-pill badge-sage" style="font-weight: 700;">{supp_code} • {supp_name}</span>
                        <span style="font-size: 0.72rem; color: #75776C;">ID: <code>{p.external_id}</code></span>
                    </div>
                    <h3 style="font-size: 1.15rem; margin: 4px 0 6px 0; color: #590907; font-weight: 700;">
                        {p.name}
                    </h3>
                    <p style="margin: 0 0 6px 0; font-size: 0.8rem; color: #5C5E55;">
                        📍 {p.address or 'Address not specified'}, {p.city or 'City'}, {p.country or 'Country'} &bull; <span style="color: #75776C;">{coords_str}</span>
                    </p>
                    <div style="font-size: 0.825rem; color: #2A2B27; margin-bottom: 8px;">
                        {details_line}
                    </div>
                    <p style="margin: 0 0 8px 0; font-size: 0.8rem; color: #43443E; line-height: 1.45;">
                        {p.description or 'No property description provided.'}
                    </p>
                    <div style="display: flex; flex-wrap: wrap; gap: 4px; align-items: center;">
                        {tags_html}
                    </div>
                </div>
                
                <div style="text-align: right; min-width: 160px; border-left: 1px solid rgba(165,167,155,0.3); padding-left: 16px;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #75776C;">Baseline Rate</div>
                    <div style="font-size: 1.6rem; font-weight: 800; color: #590907;">
                        ${p.base_price:.2f} <span style="font-size: 0.75rem; color: #5C5E55;">{p.currency}</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #75776C; margin-top: 2px;">
                        +${p.tax_amount:.2f} taxes / fees
                    </div>
                    <div style="margin-top: 8px;">
                        <span class="badge-pill {'badge-emerald' if 'free' in (p.cancellation_policy or '').lower() else 'badge-amber'}">
                            {p.cancellation_policy or 'Standard Policy'}
                        </span>
                    </div>
                    <div style="margin-top: 6px; font-size: 0.75rem; font-weight: 600; color: #065f46;">
                        ● {p.availability_status or 'Available'}
                    </div>
                    <div style="margin-top: 8px; font-size: 0.72rem; color: #5C5E55;">
                        Quality Score: <strong style="color: {comp_color};">{comp_pct}%</strong>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"🔍 Inspect Raw Supplier Feed Payload — {p.external_id}"):
            p_payload = {
                "id": p.id,
                "external_id": p.external_id,
                "supplier": supp_name,
                "supplier_code": supp_code,
                "product_type": p.product_type,
                "name": p.name,
                "city": p.city,
                "country": p.country,
                "address": p.address,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "base_price": p.base_price,
                "currency": p.currency,
                "cancellation_policy": p.cancellation_policy,
                "availability_status": p.availability_status,
                "attributes": {
                    "star_rating": p.star_rating,
                    "room_category": p.room_category,
                    "amenities": p.amenities,
                    "duration_hours": p.duration_hours,
                    "activity_type": p.activity_type,
                    "inclusions": p.inclusions,
                    "meeting_point": p.meeting_point,
                },
                "raw_payload": p.raw_payload
            }
            st.json(p_payload)

