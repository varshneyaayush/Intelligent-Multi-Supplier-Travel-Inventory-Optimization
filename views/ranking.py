import streamlit as st
from sqlalchemy.orm import Session
from core.models import InventoryProduct
from ai.ranking_engine import ranking_engine

def render_ranking(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                ⚖️ Explainable Multi-Criteria Ranking Engine
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Balances cost efficiency against supplier fulfillment trust and booking cancellation flexibility.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Utility Optimization</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Filter and Interactive Utility Sliders
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
            1. Multi-Criteria Utility Weight Configuration
        </h3>
        <p style="margin: 0 0 12px 0; font-size: 0.8rem; color: #5C5E55;">
            Cheapest does not mean best. Tune utility weights to balance price savings against cancellation risk and supplier reliability.
        </p>
    """, unsafe_allow_html=True)

    w_cols = st.columns(5)
    with w_cols[0]:
        w_price = st.slider("Price Weight", 0, 60, int(st.session_state["ranking_weights"]["price_weight"]*100), step=5, key="rk_w_price")
    with w_cols[1]:
        w_trust = st.slider("Supplier Trust", 0, 60, int(st.session_state["ranking_weights"]["trust_weight"]*100), step=5, key="rk_w_trust")
    with w_cols[2]:
        w_avail = st.slider("Availability", 0, 50, int(st.session_state["ranking_weights"]["availability_weight"]*100), step=5, key="rk_w_avail")
    with w_cols[3]:
        w_qual = st.slider("Content Quality", 0, 50, int(st.session_state["ranking_weights"]["quality_weight"]*100), step=5, key="rk_w_qual")
    with w_cols[4]:
        w_cancel = st.slider("Cancellation Flex.", 0, 50, int(st.session_state["ranking_weights"]["cancellation_weight"]*100), step=5, key="rk_w_cancel")

    total_sum = (w_price + w_trust + w_avail + w_qual + w_cancel) or 100
    norm_weights = {
        "price_weight": w_price / total_sum,
        "trust_weight": w_trust / total_sum,
        "availability_weight": w_avail / total_sum,
        "quality_weight": w_qual / total_sum,
        "cancellation_weight": w_cancel / total_sum
    }
    st.session_state["ranking_weights"] = norm_weights

    # Type Filter
    cat_cols = st.columns([1.5, 3])
    with cat_cols[0]:
        cat_filter = st.selectbox(
            "Product Domain Filter",
            options=["ALL", "HOTEL", "SIGHTSEEING"],
            format_func=lambda x: "All Inventory Types" if x == "ALL" else ("Hotels Only" if x == "HOTEL" else "Sightseeing Only"),
            key="rk_cat_select"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Database Query
    query = db.query(InventoryProduct)
    if cat_filter != "ALL":
        query = query.filter(InventoryProduct.product_type == cat_filter)
    
    products = query.all()
    if not products:
        st.warning("No products available to rank.")
        return

    prod_dicts = []
    for p in products:
        prod_dicts.append({
            "id": p.id,
            "name": p.name,
            "product_type": p.product_type,
            "supplier_name": p.supplier.name if p.supplier else "Unknown",
            "supplier_code": p.supplier.code if p.supplier else "UNK",
            "supplier_trust_score": p.supplier.metrics.trust_score if (p.supplier and p.supplier.metrics) else 80.0,
            "base_price": p.base_price,
            "star_rating": p.star_rating,
            "room_category": p.room_category,
            "activity_type": p.activity_type,
            "cancellation_policy": p.cancellation_policy,
            "availability_status": p.availability_status,
            "data_completeness_score": p.data_completeness_score
        })

    # Execute Ranking
    ranked_results = ranking_engine.rank_products(prod_dicts, norm_weights)

    # 3. Render Ranked Leaderboard
    st.markdown(f"""
    <div style="margin: 15px 0 10px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Optimized Selection Hierarchy (Top <strong>{len(ranked_results)}</strong> products)
    </div>
    """, unsafe_allow_html=True)

    for item in ranked_results:
        rank = item["rank"]
        # Medal or rank styling
        if rank == 1:
            rank_badge = '<span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: #590907; color: #E8D2B5; border-radius: 50%; font-weight: 800; font-size: 14px; box-shadow: 0 0 12px rgba(89,9,7,0.4);">🥇 #1</span>'
        elif rank == 2:
            rank_badge = '<span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: #8E9084; color: #FFFFFF; border-radius: 50%; font-weight: 800; font-size: 14px;">🥈 #2</span>'
        elif rank == 3:
            rank_badge = '<span style="display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: #D2AD7D; color: #590907; border-radius: 50%; font-weight: 800; font-size: 14px;">🥉 #3</span>'
        else:
            rank_badge = f'<span style="display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: rgba(165,167,155,0.4); color: #2A2B27; border-radius: 50%; font-weight: 700; font-size: 12px;">#{rank}</span>'

        is_hotel = (item["product_type"] == "HOTEL")
        type_badge = "🏨 HOTEL" if is_hotel else "🎟️ SIGHTSEEING"
        sb = item["score_breakdown"]
        trade_offs = item.get("trade_offs", [])

        trade_offs_html = "".join([f'<span class="badge-pill badge-cream" style="margin-right: 4px; margin-bottom: 4px; font-size: 0.7rem;">{t}</span>' for t in trade_offs])

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(165,167,155,0.3); padding-bottom: 10px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {rank_badge}
                    <span class="badge-pill badge-burgundy">{type_badge}</span>
                    <span class="badge-pill badge-sage">{item['supplier_code']} &bull; {item['supplier_name']}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #75776C;">Optimization Index:</span>
                    <strong style="font-size: 1.3rem; color: #590907; margin-left: 6px;">{item['overall_score']:.1f}</strong> <span style="font-size: 0.75rem; color: #75776C;">/ 100</span>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr auto; gap: 16px; margin-bottom: 12px; align-items: center;">
                <div>
                    <h3 style="font-size: 1.15rem; margin: 0 0 4px 0; color: #590907; font-weight: 700;">
                        {item['product_name']}
                    </h3>
                    <div style="font-size: 0.8rem; color: #5C5E55;">
                        <strong>Tier:</strong> {item['room_or_activity']} &bull; <strong>Policy:</strong> {item['cancellation_policy']} &bull; <strong>Status:</strong> {item['availability_status']}
                    </div>
                </div>
                
                <div style="text-align: right; background: rgba(232,210,181,0.35); border-radius: 10px; padding: 8px 16px;">
                    <div style="font-size: 0.7rem; color: #75776C; font-weight: 700; text-transform: uppercase;">Rate</div>
                    <div style="font-size: 1.4rem; font-weight: 800; color: #590907;">
                        ${item['base_price']:.2f}
                    </div>
                </div>
            </div>
            
            <!-- Utility Sub-scores 5-pack -->
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 12px; font-size: 0.72rem; text-align: center;">
                <div style="background: rgba(253,252,249,0.9); border: 1px solid rgba(232,210,181,0.7); border-radius: 6px; padding: 6px;">
                    <div style="color: #75776C; font-weight: 600;">Price Score</div>
                    <div style="font-weight: 800; font-size: 0.95rem; color: #590907;">{sb['price_score']:.0f}</div>
                </div>
                <div style="background: rgba(253,252,249,0.9); border: 1px solid rgba(232,210,181,0.7); border-radius: 6px; padding: 6px;">
                    <div style="color: #75776C; font-weight: 600;">Trust Score</div>
                    <div style="font-weight: 800; font-size: 0.95rem; color: #065f46;">{sb['trust_score']:.0f}</div>
                </div>
                <div style="background: rgba(253,252,249,0.9); border: 1px solid rgba(232,210,181,0.7); border-radius: 6px; padding: 6px;">
                    <div style="color: #75776C; font-weight: 600;">Availability</div>
                    <div style="font-weight: 800; font-size: 0.95rem; color: #590907;">{sb['availability_score']:.0f}</div>
                </div>
                <div style="background: rgba(253,252,249,0.9); border: 1px solid rgba(232,210,181,0.7); border-radius: 6px; padding: 6px;">
                    <div style="color: #75776C; font-weight: 600;">Quality Score</div>
                    <div style="font-weight: 800; font-size: 0.95rem; color: #590907;">{sb['quality_score']:.0f}</div>
                </div>
                <div style="background: rgba(253,252,249,0.9); border: 1px solid rgba(232,210,181,0.7); border-radius: 6px; padding: 6px;">
                    <div style="color: #75776C; font-weight: 600;">Cancellation</div>
                    <div style="font-weight: 800; font-size: 0.95rem; color: #590907;">{sb['cancellation_score']:.0f}</div>
                </div>
            </div>
            
            <div style="display: flex; flex-wrap: wrap; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #75776C; margin-right: 6px;">Decision Trade-offs:</span>
                {trade_offs_html}
            </div>
            
            <p style="margin: 0; font-size: 0.78rem; color: #43443E; background: rgba(165,167,155,0.15); padding: 8px 12px; border-radius: 8px;">
                💡 <strong>Explainable Utility Rationale:</strong> {item['explanation']}
            </p>
        </div>
        """, unsafe_allow_html=True)

