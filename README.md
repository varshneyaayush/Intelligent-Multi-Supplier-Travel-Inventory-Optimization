# OptiSupply AI — Intelligent Multi-Supplier Travel Inventory Optimization Platform
### VOYAGEHACK 4.0 | Team ASTRA (Sonali & Aayush)

> **"Transforming Fragmented Travel Inventory into Intelligent Decisions."**

---

## 🌟 Executive Summary

**OptiSupply AI** is an enterprise-grade AI travel inventory optimization platform engineered for travel distributors, online travel agencies (OTAs), bedbanks, and travel-tech platforms. It addresses multi-supplier travel inventory fragmentation across hotels and travel experiences through real-time AI multimodal duplicate detection, relationship clustering, supplier trust scoring, dynamic price anomaly detection, multi-criteria ranking, grounded content enrichment, and interactive What-If scenario simulations.

The application has been fully architected as a standalone **Python Streamlit application** running with custom glassmorphism design, capable of running locally or deploying directly to **Streamlit Community Cloud**.

---

## 🎨 Strict Brand Design System

The application strictly reflects the project's brand palette:
- **Primary Background — Muted Sage Grey (`#A5A79B`)**: Sophisticated backdrop tone.
- **Secondary Surface — Warm Cream Beige (`#E8D2B5`)**: Frosted-glass cards, control panels, and containers.
- **Accent / Hero — Deep Burgundy (`#590907`)**: Key actions, navigation active states, branding, and alert highlights.
- **Card Background (`#FDFCF9`)**: Subtle warm white card fill for enhanced readability.
- **Glassmorphism & Micro-Interactions**: Frosted glass panels with layered depth, soft borders, and rounded corners (`border-radius: 12px`).

---

## 🚀 Quick Start (Local Run)

### 1. Prerequisites
- Python 3.10+ (tested and verified on Python 3.14)
- Git

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/your-username/Intelligent-Multi-Supplier-Travel-Inventory-Optimization.git
cd Intelligent-Multi-Supplier-Travel-Inventory-Optimization

pip install -r requirements.txt
```

### 3. Run Application
Launch the Streamlit application:
```bash
streamlit run app.py
```
The application will automatically initialize the database (`optisupply.db`), seed the benchmark demonstration scenarios, and open in your default browser at `http://localhost:8501`.

---

## ☁️ Streamlit Community Cloud Deployment Guide

OptiSupply AI is built specifically for seamless deployment to **Streamlit Community Cloud**:

### Deployment Steps:
1. **Push to GitHub**: Ensure all files (including `app.py`, `requirements.txt`, `.streamlit/config.toml`, `ai/`, `core/`, `services/`, `views/`) are pushed to your GitHub repository.
2. **Sign in to Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub account.
3. **Create New App**:
   - **Repository**: `your-username/Intelligent-Multi-Supplier-Travel-Inventory-Optimization`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. **Configure Secrets (Optional PostgreSQL)**:
   In the Streamlit App Settings under **Secrets**, you can configure an external PostgreSQL database or keep the default zero-config SQLite persistence:
   ```toml
   # .streamlit/secrets.toml (Optional - default uses SQLite ./optisupply.db)
   DATABASE_URL = "postgresql://user:password@host:5432/optisupply"
   DUPLICATE_CONFIDENCE_THRESHOLD = 0.85
   GEO_VICINITY_METERS = 100.0
   ```
5. **Deploy**: Click **Deploy!** The application will install dependencies from `requirements.txt` and launch automatically.

---

## 📂 Modular Architecture

```
optisupply-ai/
│
├── app.py                      # Main Streamlit application entry point & layout
├── requirements.txt            # Production dependencies for Streamlit Cloud
├── .gitignore                  # Excludes caches, secrets, and temp files
│
├── .streamlit/
│   └── config.toml             # Brand theme colors, server & client settings
│
├── core/                       # Core infrastructure & configuration
│   ├── __init__.py
│   ├── config.py               # Application settings, DB URLs, thresholds
│   ├── database.py             # SQLAlchemy engine & session management
│   ├── models.py               # 10 SQLAlchemy ORM models
│   ├── theme.py                # Glassmorphic CSS styling injection
│   ├── navigation.py           # 14 Navigation item definitions & metadata
│   └── session.py              # Streamlit session state initialization
│
├── ai/                         # Grounded AI Engines (Standalone, Zero-Hallucination)
│   ├── __init__.py
│   ├── duplicate_detector.py   # Token sort + Haversine geo + TF-IDF/Sentence-Transformers
│   ├── relationship_engine.py  # 5-type cross-supplier relationship classifier
│   ├── price_anomaly.py        # IQR, Z-Score, and Isolation Forest anomaly detector
│   ├── supplier_intelligence.py# Multi-factor explainable trust scoring (0–100)
│   ├── ranking_engine.py       # Multi-criteria weighted utility ranking
│   ├── quality_enrichment.py   # Field completeness auditing & text extraction enrichment
│   ├── recommendation_engine.py# Actionable inventory optimization directives
│   └── simulation_engine.py    # What-if scenario simulation & trade-off analyzer
│
├── services/                   # Application business services
│   ├── __init__.py
│   ├── ingestion.py            # CSV / Excel XLSX ingestion, column mapping & validation
│   ├── demo_data.py            # Automated seeder for hotels, sightseeing, & AI pipeline
│   └── analytics.py            # Live database KPI aggregation
│
├── views/                      # 14 Dedicated View Pages
│   ├── __init__.py
│   ├── overview.py             # Executive dashboard & Grand Palace spotlight
│   ├── inventory.py            # Inventory explorer with supplier payload viewer
│   ├── upload.py               # Ingestion studio with CSV/XLSX template downloads
│   ├── duplicate_detection.py  # Side-by-side duplicate candidate comparison
│   ├── relationships.py        # Interactive Plotly relationship network graph
│   ├── supplier_intelligence.py# Supplier trust scorecards & radar charts
│   ├── price_anomalies.py      # Statistical price anomaly alerts
│   ├── ranking.py              # Interactive multi-criteria ranking sliders
│   ├── quality_enrichment.py   # Grounded enrichment & completeness auditing
│   ├── review_center.py        # Centralized human review queue & audit trail
│   ├── recommendations.py      # Optimization directives with business rationale
│   ├── simulation.py           # What-if simulation sandbox with rank shifts
│   ├── analytics.py            # Live distribution analytics & box plots
│   └── settings.py             # System thresholds & benchmark demo reset
│
└── tests/                      # Automated test suite
    ├── __init__.py
    ├── test_pipeline.py        # 8 AI engine & service unit tests
    └── test_app_views.py       # 15 AppTest end-to-end view rendering tests
```

---

## 🧩 The 14 Application Views

1. **Executive Overview Dashboard**: High-level KPI cards, Grand Palace Hotel demonstration scenario spotlight, quality completeness bar chart, price anomaly breakdown, and top-ranked supplier leaderboard.
2. **Inventory Management**: Filter by category (Hotels / Sightseeing), search by keyword, view rate, coordinates, amenities, and inspect raw supplier JSON payloads.
3. **Data Upload & Processing**: Drag-and-drop ingestion interface supporting CSV and XLSX files with automatic column detection, interactive schema mapping, row validation, template downloads, and bulk import.
4. **Duplicate Detection**: Side-by-side comparison of candidate duplicate pairs with multi-modal scoring (string distance, Haversine geo radius, and semantic similarity). Includes one-click Approve / Reject actions.
5. **Product Relationships**: Plotly circular network graph and relationship cards categorizing cross-supplier identical properties, distinct room categories (e.g. Deluxe King vs Royal Suite), related sightseeing tours, and destination alternatives.
6. **Supplier Intelligence**: Transparent, explainable supplier trust scores (0–100) based on price competitiveness, booking success rate, availability accuracy, cancellation reliability, data completeness, and API latency with Plotly radar charts.
7. **Price Anomaly Detection**: Statistical anomaly detection utilizing IQR multipliers, Z-scores, and Scikit-learn Isolation Forests. Highlights cross-supplier price disparity (e.g. $98 vs $145).
8. **Supplier & Product Ranking**: Multi-criteria ranking engine with dynamic sliders for Price, Supplier Trust, Availability, Content Quality, and Cancellation Flexibility.
9. **Inventory Quality & Content Enrichment**: Field-level completeness auditing and non-hallucinatory AI enrichment suggestions extracted strictly from verified property descriptions.
10. **Human Review Center**: Centralized review queue for pending duplicates, severe price anomalies, and quality reports, backed by an immutable, timestamped audit trail.
11. **Optimization Recommendations**: Actionable operational recommendations synthesized directly from live database findings with explicit rationale and expected business benefits.
12. **What-If Simulation Engine**: Interactive sandbox to simulate excluding specific suppliers, enforcing free cancellation, and tuning cost sensitivity with projected trade-offs and rank shifts.
13. **Analytics & Insights**: True database metrics visualized via Plotly charts (completeness tiers, price anomaly distributions, supplier trust comparisons).
14. **System Settings**: Configurable thresholds for duplicate confidence, geo-vicinity radius, database engine info, and a one-click Demonstration Benchmark Reset.

---

## 🔬 Benchmark Demonstration Scenarios

### Scenario 1 — Grand Palace Hotel Multi-Supplier Consolidation (Hotels)
- **Supplier A (Apex Wholesalers)**: *Grand Palace Hotel* — Deluxe King — **$120.00** (Free Cancellation 48h, Trust Score: 92/100)
- **Supplier B (Bedrock Network)**: *The Grand Palace* — Deluxe Room — **$98.00** (Non-refundable, Trust Score: 87/100, -21% price anomaly)
- **Supplier C (Continental DMC)**: *Grand Palace Hotel & Spa* — Deluxe Room — **$145.00** (Free Cancellation 24h, Trust Score: 89/100, +22% price anomaly)
- **Outcome**: The AI detects identical coordinates (3.2m apart) and 96% semantic identity, surfaces cross-supplier rate disparity, and ranks Supplier A as the optimal balanced choice rather than blindly defaulting to the cheapest non-refundable rate.

### Scenario 2 — Louvre Museum Guided Tours (Sightseeing / Experiences)
- **Supplier A**: *Louvre Museum Skip-the-Line Express Guided Tour* — **$68.00**
- **Supplier B**: *Louvre Skip-the-Line Masterpieces Tour with Guide* — **$54.00**
- **Outcome**: Evaluates duration, licensed guide inclusions, and landmark coordinates to consolidate duplicate activity tickets while separating evening river cruises and dinner packages.

---

## 🧪 Automated Test Suite

The test suite covers both unit AI pipelines and full Streamlit view rendering:

```bash
python -m pytest tests/ -v
```

Output:
```text
tests/test_pipeline.py::test_duplicate_detection_high_confidence PASSED
tests/test_pipeline.py::test_relationship_different_room_category PASSED
tests/test_pipeline.py::test_price_anomaly_detection PASSED
tests/test_pipeline.py::test_supplier_trust_scoring PASSED
tests/test_pipeline.py::test_ranking_engine_multi_criteria PASSED
tests/test_pipeline.py::test_quality_and_grounded_enrichment PASSED
tests/test_pipeline.py::test_ingestion_column_mapping_and_validation PASSED
tests/test_pipeline.py::test_simulation_engine PASSED
tests/test_app_views.py::test_app_initial_load PASSED
tests/test_app_views.py::test_app_render_all_tabs[overview] PASSED
tests/test_app_views.py::test_app_render_all_tabs[inventory] PASSED
tests/test_app_views.py::test_app_render_all_tabs[upload] PASSED
tests/test_app_views.py::test_app_render_all_tabs[duplicates] PASSED
tests/test_app_views.py::test_app_render_all_tabs[relationships] PASSED
tests/test_app_views.py::test_app_render_all_tabs[suppliers] PASSED
tests/test_app_views.py::test_app_render_all_tabs[anomalies] PASSED
tests/test_app_views.py::test_app_render_all_tabs[ranking] PASSED
tests/test_app_views.py::test_app_render_all_tabs[quality] PASSED
tests/test_app_views.py::test_app_render_all_tabs[review] PASSED
tests/test_app_views.py::test_app_render_all_tabs[recommendations] PASSED
tests/test_app_views.py::test_app_render_all_tabs[simulation] PASSED
tests/test_app_views.py::test_app_render_all_tabs[analytics] PASSED
tests/test_app_views.py::test_app_render_all_tabs[settings] PASSED

============================= 23 passed in 21.86s =============================
```

---

*Created with pride for VOYAGEHACK 4.0 by Team ASTRA — Sonali & Aayush.*
