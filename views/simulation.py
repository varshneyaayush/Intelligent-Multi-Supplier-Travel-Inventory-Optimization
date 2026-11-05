import streamlit as st
from sqlalchemy.orm import Session
from core.models import InventoryProduct, Supplier, SimulationScenario
from ai.simulation_engine import simulation_engine

def render_simulation(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                🧪 What-If Scenario Simulation &amp; Optimization Engine
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Simulate operational shifts such as excluding suppliers or enforcing strict cancellation terms with rank shift projections.
            </p>
        </div>
        <span class="badge-pill badge-burgundy">Predictive Sandbox</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(165,167,155,0.25); border: 1px solid rgba(165,167,155,0.45); border-radius: 12px; padding: 10px 16px; margin-bottom: 16px; font-size: 0.78rem; color: #2A2B27; display: flex; align-items: center; gap: 8px;">
        <span>ℹ️</span> <strong>Algorithmic Projection Disclaimer:</strong> All simulated metrics represent theoretical heuristic projections based on the current inventory universe. These projections do not constitute financial guarantees.
    </div>
    """, unsafe_allow_html=True)

    suppliers = db.query(Supplier).all()
    products = db.query(InventoryProduct).all()

    # 1. Interactive Simulation Controls Card
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 12px 0; color: #590907; font-weight: 700;">
            1. Configure Simulation Parameters
        </h3>
    """, unsafe_allow_html=True)

    sc_name = st.text_input(
        "Scenario Name",
        value=st.session_state.get("sim_scenario_name", "Excluding Bedrock & Prioritizing Trust"),
        key="sim_name_input"
    )
    st.session_state["sim_scenario_name"] = sc_name

    col_sup, col_rules = st.columns([1.5, 1.5])

    with col_sup:
        st.markdown("<div style='font-size: 0.825rem; font-weight: 700; color: #2A2B27; margin-bottom: 6px;'>Simulate Excluding Specific Suppliers:</div>", unsafe_allow_html=True)
        excluded_ids = []
        for s in suppliers:
            excl = st.checkbox(
                f"Exclude {s.name} ({s.code})",
                value=(s.id in st.session_state.get("sim_excluded_suppliers", [])),
                key=f"sim_excl_{s.id}"
            )
            if excl:
                excluded_ids.append(s.id)
        st.session_state["sim_excluded_suppliers"] = excluded_ids

    with col_rules:
        st.markdown("<div style='font-size: 0.825rem; font-weight: 700; color: #2A2B27; margin-bottom: 6px;'>Enforce Booking Policies & Price Caps:</div>", unsafe_allow_html=True)
        free_cancel = st.checkbox(
            "Enforce Mandatory Free Cancellation Only",
            value=st.session_state.get("sim_require_free_cancellation", False),
            help="Filters out all non-refundable or restricted rate options.",
            key="sim_free_cancel_cb"
        )
        st.session_state["sim_require_free_cancellation"] = free_cancel

        price_cap = st.slider(
            "Maximum Rate Cap ($)",
            min_value=50,
            max_value=600,
            value=int(st.session_state.get("sim_max_price_cap", 500.0)),
            step=25,
            key="sim_price_cap_slider"
        )
        st.session_state["sim_max_price_cap"] = float(price_cap)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.825rem; font-weight: 700; color: #2A2B27; margin-bottom: 6px;'>Adjust Decision Utility Weights:</div>", unsafe_allow_html=True)
    sim_w_cols = st.columns(5)
    with sim_w_cols[0]:
        sim_w_p = st.slider("Price", 0, 60, int(st.session_state["sim_weights"]["price_weight"]*100), step=5, key="sim_w_p")
    with sim_w_cols[1]:
        sim_w_t = st.slider("Trust", 0, 60, int(st.session_state["sim_weights"]["trust_weight"]*100), step=5, key="sim_w_t")
    with sim_w_cols[2]:
        sim_w_a = st.slider("Availability", 0, 50, int(st.session_state["sim_weights"]["availability_weight"]*100), step=5, key="sim_w_a")
    with sim_w_cols[3]:
        sim_w_q = st.slider("Quality", 0, 50, int(st.session_state["sim_weights"]["quality_weight"]*100), step=5, key="sim_w_q")
    with sim_w_cols[4]:
        sim_w_c = st.slider("Cancel Flex", 0, 50, int(st.session_state["sim_weights"]["cancellation_weight"]*100), step=5, key="sim_w_c")

    tot_sim_w = (sim_w_p + sim_w_t + sim_w_a + sim_w_q + sim_w_c) or 100
    st.session_state["sim_weights"] = {
        "price_weight": sim_w_p / tot_sim_w,
        "trust_weight": sim_w_t / tot_sim_w,
        "availability_weight": sim_w_a / tot_sim_w,
        "quality_weight": sim_w_q / tot_sim_w,
        "cancellation_weight": sim_w_c / tot_sim_w
    }

    run_sim_btn = st.button("🚀 Execute What-If Scenario Simulation", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Run simulation on click or load existing
    prod_dicts = []
    for p in products:
        prod_dicts.append({
            "id": p.id,
            "name": p.name,
            "supplier_id": p.supplier_id,
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

    if run_sim_btn or st.session_state.get("simulation_result") is None:
        sim_res = simulation_engine.simulate_scenario(
            products=prod_dicts,
            scenario_name=sc_name,
            excluded_supplier_ids=excluded_ids,
            weight_adjustments=st.session_state["sim_weights"],
            max_price_cap=price_cap if price_cap < 600 else None,
            require_free_cancellation=free_cancel
        )
        st.session_state["simulation_result"] = sim_res

    res = st.session_state["simulation_result"]
    if not res:
        return

    # 3. Projected Impact KPIs
    impact = res.get("projected_impact", {})
    p_delta = impact.get("price_delta", 0.0)
    t_delta = impact.get("trust_delta", 0.0)
    inv_drop = impact.get("inventory_reduction_pct", 0.0)

    p_delta_sign = "+" if p_delta > 0 else ""
    t_delta_sign = "+" if t_delta > 0 else ""

    p_delta_color = "#9f1239" if p_delta > 0 else "#065f46"
    t_delta_color = "#065f46" if t_delta > 0 else "#9f1239"

    st.markdown("""
    <div style="margin: 15px 0 10px 0; font-size: 0.8rem; font-weight: 600; color: #5C5E55;">
        Simulated Operational Outcomes
    </div>
    """, unsafe_allow_html=True)

    imp_col1, imp_col2, imp_col3 = st.columns(3)
    with imp_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Top-10 Rate Impact</div>
            <div class="kpi-value" style="color: {p_delta_color};">{p_delta_sign}${p_delta:.2f}</div>
            <div class="kpi-subtitle">Per-booking baseline shift</div>
        </div>
        """, unsafe_allow_html=True)

    with imp_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Avg Supplier Trust Impact</div>
            <div class="kpi-value" style="color: {t_delta_color};">{t_delta_sign}{t_delta:.1f} pts</div>
            <div class="kpi-subtitle">Change in top recommendation trust</div>
        </div>
        """, unsafe_allow_html=True)

    with imp_col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Inventory Pool Reduction</div>
            <div class="kpi-value" style="color: #b45309;">{inv_drop:.1f}%</div>
            <div class="kpi-subtitle">{res['simulated_summary']['eligible_products']} of {res['baseline_summary']['total_products']} products eligible</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Projected Rank Shifts Table
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
            📊 Projected Top Recommendation Rank Shifts
        </h3>
        <p style="margin: 0 0 12px 0; font-size: 0.8rem; color: #5C5E55;">
            Comparing product rank advancements and declines under the simulated scenario.
        </p>
    """, unsafe_allow_html=True)

    shifts = res.get("rank_shifts", [])
    if not shifts:
        st.info("No items qualify under simulated constraints.")
    else:
        shift_rows = ""
        for s in shifts:
            status = s["status"]
            if status == "Advanced":
                shift_badge = f'<span class="badge-pill badge-emerald">▲ +{s["rank_delta"]} Advanced</span>'
            elif status == "Declined":
                shift_badge = f'<span class="badge-pill badge-rose">▼ {s["rank_delta"]} Declined</span>'
            else:
                shift_badge = '<span class="badge-pill badge-sage">▬ Unchanged</span>'

            shift_rows += f"""
            <tr>
                <td style="font-weight: 700; color: #590907;">#{s['simulated_rank']}</td>
                <td style="font-weight: 600;">{s['product_name']}</td>
                <td><span class="badge-pill badge-sage">{s['supplier_name']}</span></td>
                <td style="font-weight: 700;">${s['base_price']:.2f}</td>
                <td style="color: #75776C;">#{s['baseline_rank']}</td>
                <td>{shift_badge}</td>
            </tr>
            """
        st.markdown(f"""
        <div style="overflow-x: auto;">
            <table class="custom-table">
                <thead>
                    <tr>
                        <th>Simulated Rank</th>
                        <th>Product Name</th>
                        <th>Supplier</th>
                        <th>Rate</th>
                        <th>Baseline Rank</th>
                        <th>Trajectory</th>
                    </tr>
                </thead>
                <tbody>
                    {shift_rows}
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Trade-off Analysis Notes
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
            🔍 Algorithmic Trade-off Analysis
        </h3>
    """, unsafe_allow_html=True)

    trade_offs = res.get("trade_off_analysis", [])
    for t in trade_offs:
        st.markdown(f"- <span style='font-size: 0.825rem; color: #2A2B27;'>{t}</span>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

