# OptiSupply AI — Intelligent Multi-Supplier Travel Inventory Optimization Platform
### VOYAGEHACK 4.0 | Team ASTRA (Sonali & Aayush)

> **"Transforming Fragmented Travel Inventory into Intelligent Decisions."**

---

## 🌟 Platform Overview

**OptiSupply AI** is an enterprise-grade AI SaaS prototype engineered for travel distributors, OTAs, bedbanks, and travel-tech platforms. It resolves multi-supplier travel inventory fragmentation across hotels and travel experiences through real-time AI multimodal duplicate detection, relationship clustering, supplier trust scoring, dynamic price anomaly detection, multi-criteria ranking, grounded content enrichment, and interactive What-If scenario simulations.

---

## 🎨 Design System & Visual Identity

The interface strictly adheres to the approved brand palette and visual hierarchy:
- **Primary Background — Muted Sage Grey (`#A5A79B`)**: Dominates the global layout for a clean, sophisticated backdrop.
- **Secondary Surface — Warm Cream Beige (`#E8D2B5`)**: Forms frosted-glass cards, control panels, and containers.
- **Accent — Deep Burgundy (`#590907`)**: Highlights key actions, navigation active states, branding, and warnings.
- **Glassmorphism**: Frosted glass panels with subtle backdrop blur (`backdrop-blur-md`), soft elevation shadows, and smooth Framer Motion transitions.

---

## 🚀 Live Local Host Access

Both servers are running live in the workspace:

| Service | Local Host URL | Description |
| :--- | :--- | :--- |
| **Frontend Application** | [http://localhost:5173](http://localhost:5173) | Interactive React + TypeScript + Tailwind CSS Dashboard |
| **Backend API Docs (Swagger)** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | Interactive FastAPI documentation and schemas |
| **Backend Health Check** | [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) | Live JSON health check and platform capabilities |

---

## 🧩 14 Functional Application Sections

1. **Overview Dashboard**: High-level KPI cards, Grand Palace Hotel demonstration scenario spotlight, quality completeness bar chart, price anomaly breakdown, and top-ranked supplier leaderboard.
2. **Inventory Management**: Filter by category (Hotels / Sightseeing), search by keyword, view rate, coordinates, amenities, and inspect raw supplier JSON payloads.
3. **Data Upload & Processing**: Drag-and-drop ingestion interface supporting CSV and XLSX files with automatic column detection, interactive schema mapping, row validation, and bulk import.
4. **Duplicate Detection**: Side-by-side comparison of candidate duplicate pairs with multi-modal scoring (string distance, Haversine geo radius, and Sentence-Transformers semantic similarity). Includes one-click Approve / Reject actions.
5. **Product Relationships**: Differentiates cross-supplier identical properties, distinct room categories (e.g. Deluxe King vs Royal Suite), related sightseeing tours, and destination alternatives.
6. **Supplier Intelligence**: Transparent, explainable supplier trust scores (0–100) based on price competitiveness, booking success rate, availability accuracy, cancellation reliability, data completeness, and API latency. Includes customizable trust scoring weights.
7. **Price Anomaly Detection**: Statistical anomaly detection utilizing IQR multipliers, Z-scores, and Scikit-learn Isolation Forests. Highlights cross-supplier price disparity (e.g. $98 vs $145).
8. **Supplier & Product Ranking**: Multi-criteria ranking engine with dynamic sliders for Price, Supplier Trust, Availability, Content Quality, and Cancellation Flexibility.
9. **Inventory Quality & Content Enrichment**: Field-level completeness auditing and non-hallucinatory AI enrichment suggestions extracted strictly from verified property descriptions.
10. **Human Review Center**: Centralized review queue for pending duplicates, severe price anomalies, and quality reports, backed by an immutable, timestamped audit trail.
11. **Optimization Recommendations**: Actionable operational recommendations synthesized directly from live database findings with explicit rationale and expected business benefits.
12. **What-If Simulation Engine**: Interactive sandbox to simulate excluding specific suppliers, enforcing free cancellation, and tuning cost sensitivity with projected trade-offs and rank shifts.
13. **Analytics & Insights**: True database metrics visualized via Recharts charts (completeness tiers, price anomaly distributions, supplier trust comparisons).
14. **System Settings**: Configurable thresholds for duplicate confidence, geo-vicinity radius, database engine info, and a one-click Demonstration Benchmark Reset.

---

## 🔬 Benchmark Demonstration Scenarios Included

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

## 🛠️ Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Framer Motion, Recharts, Lucide Icons
- **Backend**: Python 3.14, FastAPI, Pydantic, Uvicorn
- **AI / ML / Data Science**: Sentence Transformers (`all-MiniLM-L6-v2`), RapidFuzz, Scikit-learn (Isolation Forest), Pandas, NumPy, Geopy / Haversine
- **Database**: PostgreSQL / SQLite through SQLAlchemy ORM
- **Testing**: PyTest with automated test coverage across ingestion, normalization, duplicate detection, ranking, and API routes.

---

## 💻 Manual Start Commands (If Restarting)

### Start Backend
```powershell
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Start Frontend
```powershell
cd frontend
npm run dev -- --host
```

---
*Created with pride for VOYAGEHACK 4.0 by Team ASTRA — Sonali & Aayush.*

