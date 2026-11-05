import streamlit as st
import pandas as pd
import io
from sqlalchemy.orm import Session
from services.ingestion import ingestion_service, STANDARD_FIELDS
from ai.quality_enrichment import quality_engine
from core.models import Supplier, InventoryProduct, AuditLog

def render_upload(db: Session):
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
        <div>
            <h2 style="font-size: 1.35rem; margin: 0; font-weight: 800; color: #590907;">
                📥 Supplier Inventory Feed Ingestion
            </h2>
            <p style="margin: 4px 0 0 0; font-size: 0.825rem; color: #5C5E55;">
                Upload multi-supplier CSV or Excel inventory files with automated column mapping, row-level validation, and quality auditing.
            </p>
        </div>
        <span class="badge-pill badge-cream">CSV &amp; XLSX Supported</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Ingestion Configuration Card
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 12px 0; color: #590907; font-weight: 700;">
            1. Configure Feed Metadata
        </h3>
    """, unsafe_allow_html=True)

    cfg_col1, cfg_col2, cfg_col3 = st.columns([1.2, 1.2, 1.2])

    with cfg_col1:
        prod_type = st.radio(
            "Target Product Domain",
            options=["HOTEL", "SIGHTSEEING"],
            format_func=lambda x: "🏨 Hotel Accommodations" if x == "HOTEL" else "🎟️ Sightseeing / Experiences",
            horizontal=True,
            key="upload_domain_radio"
        )
        st.session_state["target_product_type"] = prod_type

    with cfg_col2:
        supp_code = st.text_input(
            "Supplier Code",
            value=st.session_state.get("upload_supplier_code", "SUP_NEW"),
            placeholder="e.g. SUP_EXPEDIA, SUP_HOTELBEDS",
            key="upload_code_input"
        )
        st.session_state["upload_supplier_code"] = supp_code

    with cfg_col3:
        supp_name = st.text_input(
            "Supplier Brand Name",
            value=st.session_state.get("upload_supplier_name", "Global Partner DMC"),
            placeholder="e.g. Global Partner DMC",
            key="upload_name_input"
        )
        st.session_state["upload_supplier_name"] = supp_name

    st.markdown("</div>", unsafe_allow_html=True)

    # 2. File Upload Dropzone
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 12px 0; color: #590907; font-weight: 700;">
            2. Upload Feed File (CSV or Excel XLSX)
        </h3>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a CSV or XLSX file",
        type=["csv", "xlsx", "xls"],
        help="Upload multi-supplier inventory files up to 50MB."
    )

    # Sample template download helper
    samp_col1, samp_col2, _ = st.columns([1.5, 1.8, 3])
    with samp_col1:
        sample_hotels_csv = (
            "name,external_id,city,country,address,latitude,longitude,base_price,currency,cancellation_policy,star_rating,room_category,amenities,description\n"
            "Grand Palace Hotel,HOTEL_001,Paris,France,14 Rue du Palais,48.860611,2.337644,120.00,USD,Free Cancellation 48h,5.0,Deluxe King,\"WiFi,Pool,Spa\",Luxury 5-star hotel near Louvre\n"
            "Eiffel Boutique Suites,HOTEL_002,Paris,France,8 Ave Montaigne,48.865500,2.304500,165.00,USD,Flexible,4.5,Junior Suite,\"WiFi,Gym,Bar\",Boutique suites with Eiffel views\n"
        )
        st.download_button(
            "📄 Download Hotels Template CSV",
            data=sample_hotels_csv,
            file_name="sample_hotels_template.csv",
            mime="text/csv",
            use_container_width=True
        )

    with samp_col2:
        sample_sightseeing_csv = (
            "title,code,destination,country,address,lat,lon,rate,currency,cancellation,activity_type,duration_hours,meeting_point,inclusions,overview\n"
            "Louvre Skip-the-Line Express Tour,EXP_001,Paris,France,Louvre Museum,48.860611,2.335500,68.00,USD,Free Cancellation 24h,Guided Museum Tour,2.0,Pyramid Entrance,\"Admission Ticket,Licensed Guide\",Express guided Louvre masterpiece tour\n"
            "Seine River Sightseeing Cruise,EXP_002,Paris,France,Port de la Bourdonnais,48.859200,2.296500,18.00,USD,Non-refundable,Boat Cruise,1.0,Pont d'Iena,\"1-Hour Cruise,Audio Guide\",Scenic Seine boat cruise\n"
        )
        st.download_button(
            "📄 Download Sightseeing Template CSV",
            data=sample_sightseeing_csv,
            file_name="sample_sightseeing_template.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is None:
        return

    # 3. Parse File and Display Schema Mapping
    file_bytes = uploaded_file.getvalue()
    try:
        df = ingestion_service.parse_file(file_bytes, uploaded_file.name)
    except Exception as e:
        st.error(f"❌ Failed to parse uploaded file: {str(e)}")
        return

    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <h3 style="font-size: 0.95rem; margin: 0; color: #590907; font-weight: 700;">
                    3. Intelligent Column Mapping &amp; Schema Validation
                </h3>
                <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #5C5E55;">
                    Detected <strong>{len(df.columns)} columns</strong> across <strong>{len(df)} rows</strong> in <code>{uploaded_file.name}</code>.
                </p>
            </div>
            <span class="badge-pill badge-emerald">Auto-Mapped</span>
        </div>
    """, unsafe_allow_html=True)

    suggested_mapping = ingestion_service.suggest_column_mapping(list(df.columns))
    available_canonical = ["-- Do Not Map --"] + list(STANDARD_FIELDS.keys())

    # Mapping grid
    col_mapping = {}
    map_cols = st.columns(3)
    for idx, orig_col in enumerate(df.columns):
        suggested = suggested_mapping.get(orig_col)
        default_idx = (available_canonical.index(suggested) if (suggested and suggested in available_canonical) else 0)
        with map_cols[idx % 3]:
            mapped = st.selectbox(
                f"Column: **`{orig_col}`**",
                options=available_canonical,
                index=default_idx,
                key=f"col_map_{orig_col}_{idx}"
            )
            col_mapping[orig_col] = (mapped if mapped != "-- Do Not Map --" else None)

    st.markdown("</div>", unsafe_allow_html=True)

    # 4. Preview Sample Rows
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 0.95rem; margin: 0 0 10px 0; color: #590907; font-weight: 700;">
            4. Live Data Preview (First 5 Rows)
        </h3>
    """, unsafe_allow_html=True)
    st.dataframe(df.head(5), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Pre-validation of rows
    valid_records = []
    validation_errors = []

    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        norm, errs = ingestion_service.validate_and_normalize_row(row_dict, col_mapping, prod_type)
        if errs:
            validation_errors.append(f"Row {idx+1}: {', '.join(errs)}")
        elif norm:
            valid_records.append(norm)

    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <h3 style="font-size: 0.95rem; margin: 0; color: #590907; font-weight: 700;">
                5. Ingestion Verification Summary
            </h3>
            <span class="badge-pill {'badge-emerald' if len(valid_records) > 0 else 'badge-rose'}">
                {len(valid_records)} Ready to Import
            </span>
        </div>
        <div style="font-size: 0.85rem; color: #2A2B27; margin-bottom: 8px;">
            &bull; <strong>{len(valid_records)}</strong> rows successfully validated against standard schema.<br>
            &bull; <strong>{len(validation_errors)}</strong> rows flagged with missing mandatory fields or invalid coordinates.
        </div>
    """, unsafe_allow_html=True)

    if validation_errors:
        with st.expander(f"⚠️ View {len(validation_errors)} Validation Issues"):
            for err in validation_errors[:15]:
                st.markdown(f"- <span style='font-size: 0.8rem; color: #9f1239;'>{err}</span>", unsafe_allow_html=True)
            if len(validation_errors) > 15:
                st.markdown(f"_...and {len(validation_errors)-15} more issues._")

    # Commit Import Button
    commit_btn = st.button(
        f"🚀 Commit Feed Import ({len(valid_records)} items to database)",
        disabled=(len(valid_records) == 0),
        use_container_width=True
    )

    if commit_btn:
        with st.spinner("Ingesting and auditing feed items..."):
            # Ensure supplier exists or create
            supplier = db.query(Supplier).filter(Supplier.code == supp_code.strip()).first()
            if not supplier:
                supplier = Supplier(
                    code=supp_code.strip(),
                    name=supp_name.strip(),
                    country="Global",
                    reliability_tier="Tier 2 (Standard)"
                )
                db.add(supplier)
                db.flush()

            imported_count = 0
            for norm in valid_records:
                # Deduplicate by external_id for same supplier
                existing = db.query(InventoryProduct).filter(
                    InventoryProduct.supplier_id == supplier.id,
                    InventoryProduct.external_id == norm["external_id"]
                ).first()
                if existing:
                    continue

                q_eval = quality_engine.evaluate_quality(norm)
                norm["data_completeness_score"] = q_eval["completeness_score"]

                prod = InventoryProduct(
                    supplier_id=supplier.id,
                    **norm
                )
                db.add(prod)
                imported_count += 1

            db.commit()

            # Record in AuditLog
            audit = AuditLog(
                action="IMPORT_INVENTORY",
                entity_type="INVENTORY",
                entity_id=supplier.id,
                decision="IMPORTED",
                details={
                    "supplier_code": supplier.code,
                    "imported_count": imported_count,
                    "filename": uploaded_file.name
                }
            )
            db.add(audit)
            db.commit()

            st.success(f"✅ Successfully imported {imported_count} inventory records for supplier **{supplier.name}** ({supplier.code})!")
            st.balloons()
            st.session_state["pending_reviews_count"] = st.session_state.get("pending_reviews_count", 0)

    st.markdown("</div>", unsafe_allow_html=True)

