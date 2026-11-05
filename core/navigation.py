from dataclasses import dataclass
from typing import List, Optional

@dataclass
class NavItem:
    id: str
    label: str
    icon: str
    has_badge: bool = False
    description: str = ""

NAV_ITEMS: List[NavItem] = [
    NavItem(
        id="overview",
        label="Overview Dashboard",
        icon="📊",
        description="High-level KPIs, Grand Palace demonstration scenario, quality completeness, price anomalies, and supplier trust leaderboard."
    ),
    NavItem(
        id="inventory",
        label="Inventory Management",
        icon="📦",
        description="Filter by category (Hotels / Sightseeing), search by keyword, view rate, coordinates, amenities, and inspect raw supplier JSON payloads."
    ),
    NavItem(
        id="upload",
        label="Data Upload & Processing",
        icon="📥",
        description="Drag-and-drop ingestion interface supporting CSV and XLSX files with automatic column detection, interactive schema mapping, and validation."
    ),
    NavItem(
        id="duplicates",
        label="Duplicate Detection",
        icon="👥",
        description="Side-by-side comparison of candidate duplicate pairs with multi-modal scoring (string distance, Haversine geo radius, and semantic similarity)."
    ),
    NavItem(
        id="relationships",
        label="Product Relationships",
        icon="🔗",
        description="Differentiates cross-supplier identical properties, distinct room categories, related sightseeing tours, and destination alternatives."
    ),
    NavItem(
        id="suppliers",
        label="Supplier Intelligence",
        icon="🛡️",
        description="Transparent, explainable supplier trust scores (0–100) based on price competitiveness, booking success, availability, and response time."
    ),
    NavItem(
        id="anomalies",
        label="Price Anomaly Detection",
        icon="⚠️",
        description="Statistical anomaly detection utilizing IQR multipliers, Z-scores, and Scikit-learn Isolation Forests across supplier clusters."
    ),
    NavItem(
        id="ranking",
        label="Supplier & Product Ranking",
        icon="⚖️",
        description="Multi-criteria ranking engine with dynamic sliders for Price, Supplier Trust, Availability, Content Quality, and Cancellation Flexibility."
    ),
    NavItem(
        id="quality",
        label="Inventory Quality & Enrichment",
        icon="✨",
        description="Field-level completeness auditing and non-hallucinatory AI enrichment suggestions extracted strictly from verified descriptions."
    ),
    NavItem(
        id="review",
        label="Human Review Center",
        icon="👤",
        has_badge=True,
        description="Centralized review queue for pending duplicates, severe price anomalies, and quality reports, backed by an immutable audit trail."
    ),
    NavItem(
        id="recommendations",
        label="Optimization Recommendations",
        icon="💡",
        description="Actionable operational recommendations synthesized directly from live database findings with explicit rationale and expected benefits."
    ),
    NavItem(
        id="simulation",
        label="What-If Simulation Engine",
        icon="🧪",
        description="Interactive sandbox to simulate excluding specific suppliers, enforcing free cancellation, and tuning cost sensitivity with projected trade-offs."
    ),
    NavItem(
        id="analytics",
        label="Analytics & Insights",
        icon="📈",
        description="True database metrics visualized with interactive charts (completeness tiers, price anomaly distributions, supplier comparisons)."
    ),
    NavItem(
        id="settings",
        label="System Settings",
        icon="⚙️",
        description="Configurable thresholds for duplicate confidence, geo-vicinity radius, database engine info, and a one-click Demonstration Benchmark Reset."
    )
]

def get_nav_item(nav_id: str) -> Optional[NavItem]:
    for item in NAV_ITEMS:
        if item.id == nav_id:
            return item
    return NAV_ITEMS[0]

