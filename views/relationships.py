import streamlit as st
import plotly.graph_objects as go
import math
from sqlalchemy.orm import Session
from core.models import ProductRelationship, InventoryProduct

def render_relationships(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                🔗 Intelligent Product Relationship Engine
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Distinguishes identical cross-supplier listings from distinct room categories, related destination experiences, and alternative options.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Semantic Graph</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Filter Bar
    type_options = [
        "ALL",
        "SAME_PROPERTY_DIFFERENT_SUPPLIER",
        "DIFFERENT_ROOM_CATEGORY",
        "RELATED_EXPERIENCE",
        "ALTERNATIVE_HOTEL",
        "ALTERNATIVE_EXPERIENCE"
    ]
    type_labels = [
        "All Relationship Categories",
        "🏨 Same Property (Cross-Supplier)",
        "🛏️ Different Room Tier / Category",
        "🎟️ Related Experience (Same Landmark/City)",
        "🏢 Alternative Hotel (Same Vicinity & Stars)",
        "🗺️ Alternative Experience"
    ]
    
    selected_type = st.selectbox(
        "Relationship Category Filter",
        options=type_options,
        format_func=lambda x: type_labels[type_options.index(x)],
        key="rel_type_select"
    )

    # 2. Database Query
    query = db.query(ProductRelationship)
    if selected_type != "ALL":
        query = query.filter(ProductRelationship.relationship_type == selected_type)
    
    relationships = query.order_by(ProductRelationship.confidence_score.desc()).all()

    # 3. Interactive Graph Visualization
    st.markdown("""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="font-size: 0.95rem; margin: 0; color: #590907; font-weight: 700;">
                🌐 Multi-Supplier Inventory Relationship Graph
            </h3>
            <span class="badge-pill badge-cream">Interactive Topology</span>
        </div>
        <p style="margin: 0 0 10px 0; font-size: 0.8rem; color: #5C5E55;">
            Visualizing clustered connections between cross-supplier properties, room categories, and alternative sightseeing experiences.
        </p>
    """, unsafe_allow_html=True)

    # Build node positions in a circle layout
    all_prods = db.query(InventoryProduct).all()
    num_nodes = len(all_prods)
    node_pos = {}
    node_text = []
    node_x = []
    node_y = []
    node_colors = []

    for idx, p in enumerate(all_prods):
        angle = 2 * math.pi * idx / max(1, num_nodes)
        x = math.cos(angle)
        y = math.sin(angle)
        node_pos[p.id] = (x, y)
        node_x.append(x)
        node_y.append(y)
        is_hotel = (p.product_type == "HOTEL")
        node_colors.append("#590907" if is_hotel else "#E8D2B5")
        node_text.append(f"{p.name}<br>Supplier: {p.supplier.code if p.supplier else 'UNK'}<br>Price: ${p.base_price:.2f}")

    # Build edge traces
    edge_x = []
    edge_y = []
    for r in relationships:
        if r.source_product_id in node_pos and r.target_product_id in node_pos:
            x0, y0 = node_pos[r.source_product_id]
            x1, y1 = node_pos[r.target_product_id]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

    fig_graph = go.Figure()
    # Edges
    fig_graph.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='rgba(89, 9, 7, 0.45)'),
        hoverinfo='none',
        mode='lines'
    ))
    # Nodes
    fig_graph.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[p.name[:18] + '...' if len(p.name) > 18 else p.name for p in all_prods],
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            size=22,
            color=node_colors,
            line=dict(width=2, color='#590907')
        )
    ))

    fig_graph.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        font=dict(family="Plus Jakarta Sans, sans-serif", size=10, color="#2A2B27")
    )
    st.plotly_chart(fig_graph, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Relationship Cards
    st.markdown(f"""
    <div style="margin: 15px 0 10px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Showing <strong>{len(relationships)}</strong> identified product relationship links
    </div>
    """, unsafe_allow_html=True)

    for r in relationships:
        src = r.source_product
        tgt = r.target_product
        if not src or not tgt:
            continue

        rel_type_label = r.relationship_type.replace("_", " ")
        conf_pct = round(r.confidence_score * 100, 1)

        # Badge color based on relationship type
        if r.relationship_type == "SAME_PROPERTY_DIFFERENT_SUPPLIER":
            badge_cls = "badge-burgundy"
        elif r.relationship_type == "DIFFERENT_ROOM_CATEGORY":
            badge_cls = "badge-emerald"
        else:
            badge_cls = "badge-cream"

        evidence = r.evidence or {}
        desc_evidence = evidence.get("description", "Algorithmic relationship link")

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(165,167,155,0.3); padding-bottom: 8px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="badge-pill {badge_cls}">{rel_type_label}</span>
                    <span style="font-size: 0.75rem; color: #75776C;">Link #{r.id}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.72rem; text-transform: uppercase; font-weight: 700; color: #75776C;">Confidence:</span>
                    <strong style="font-size: 1.05rem; color: #590907; margin-left: 6px;">{conf_pct}%</strong>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr auto 1fr; gap: 12px; align-items: center; margin-bottom: 12px;">
                <!-- Source Item -->
                <div style="background: rgba(253,252,249,0.7); border: 1px solid rgba(232,210,181,0.7); border-radius: 10px; padding: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span class="badge-pill badge-sage">{src.supplier.code if src.supplier else 'SUP'}</span>
                        <strong style="color: #590907;">${src.base_price:.2f}</strong>
                    </div>
                    <div style="font-weight: 700; font-size: 0.9rem; color: #2A2B27;">{src.name}</div>
                    <div style="font-size: 0.75rem; color: #75776C; margin-top: 2px;">
                        {src.room_category or src.activity_type or 'Standard'} &bull; {src.city}
                    </div>
                </div>
                
                <!-- Connector Arrow -->
                <div style="font-size: 1.3rem; color: #590907; font-weight: 800; padding: 0 4px;">
                    ⟷
                </div>
                
                <!-- Target Item -->
                <div style="background: rgba(253,252,249,0.7); border: 1px solid rgba(232,210,181,0.7); border-radius: 10px; padding: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span class="badge-pill badge-sage">{tgt.supplier.code if tgt.supplier else 'SUP'}</span>
                        <strong style="color: #590907;">${tgt.base_price:.2f}</strong>
                    </div>
                    <div style="font-weight: 700; font-size: 0.9rem; color: #2A2B27;">{tgt.name}</div>
                    <div style="font-size: 0.75rem; color: #75776C; margin-top: 2px;">
                        {tgt.room_category or tgt.activity_type or 'Standard'} &bull; {tgt.city}
                    </div>
                </div>
            </div>
            
            <p style="margin: 0; font-size: 0.78rem; color: #43443E; background: rgba(165,167,155,0.15); padding: 8px 12px; border-radius: 8px;">
                💡 <strong>Evidence Details:</strong> {desc_evidence}
            </p>
        </div>
        """, unsafe_allow_html=True)

