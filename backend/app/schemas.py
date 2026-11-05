from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Supplier Schemas
class SupplierBase(BaseModel):
    code: str
    name: str
    contact_email: Optional[str] = None
    country: Optional[str] = "Global"
    reliability_tier: Optional[str] = "Standard"
    is_active: Optional[bool] = True

class SupplierCreate(SupplierBase):
    pass

class SupplierMetricOut(BaseModel):
    trust_score: float
    price_competitiveness: float
    booking_success_rate: float
    availability_accuracy: float
    cancellation_reliability: float
    data_completeness: float
    response_time_ms: float
    score_breakdown: Dict[str, Any]
    strengths: List[str]
    weaknesses: List[str]
    is_synthetic: bool

    class Config:
        from_attributes = True

class SupplierOut(SupplierBase):
    id: int
    created_at: datetime
    metrics: Optional[SupplierMetricOut] = None

    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    external_id: str
    product_type: str
    name: str
    description: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    star_rating: Optional[float] = None
    room_category: Optional[str] = None
    amenities: Optional[List[str]] = None
    duration_hours: Optional[float] = None
    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None
    meeting_point: Optional[str] = None
    activity_type: Optional[str] = None
    currency: Optional[str] = "USD"
    base_price: float
    tax_amount: Optional[float] = 0.0
    cancellation_policy: Optional[str] = "Non-refundable"
    availability_status: Optional[str] = "Available"

class ProductCreate(ProductBase):
    supplier_id: int

class ProductOut(ProductBase):
    id: int
    supplier_id: int
    supplier_name: Optional[str] = None
    supplier_code: Optional[str] = None
    data_completeness_score: float
    created_at: datetime

    class Config:
        from_attributes = True

# Duplicate Candidate Schemas
class DuplicateCandidateOut(BaseModel):
    id: int
    product_a_id: int
    product_b_id: int
    product_a: ProductOut
    product_b: ProductOut
    overall_confidence: float
    name_similarity: float
    geo_distance_meters: Optional[float] = None
    geo_similarity: Optional[float] = None
    semantic_similarity: float
    attribute_similarity: float
    match_classification: str
    evidence_breakdown: Dict[str, Any]
    status: str
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReviewActionRequest(BaseModel):
    decision: str = Field(..., description="'APPROVED', 'REJECTED', or 'DISMISSED'")
    notes: Optional[str] = None

# Product Relationship Schemas
class RelationshipOut(BaseModel):
    id: int
    source_product_id: int
    target_product_id: int
    source_product: ProductOut
    target_product: ProductOut
    relationship_type: str
    confidence_score: float
    evidence: Dict[str, Any]

    class Config:
        from_attributes = True

# Price Anomaly Schemas
class PriceAnomalyOut(BaseModel):
    id: int
    product_id: int
    product: ProductOut
    observed_price: float
    baseline_price: float
    price_diff_pct: float
    anomaly_type: str
    detection_method: str
    severity: str
    explanation: str
    status: str
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Inventory Quality Schemas
class QualityReportOut(BaseModel):
    id: int
    product_id: int
    product: ProductOut
    completeness_score: float
    missing_fields: List[str]
    inconsistencies: List[str]
    enrichment_suggestions: List[Dict[str, Any]]
    status: str

    class Config:
        from_attributes = True

# Recommendation Schemas
class RecommendationOut(BaseModel):
    id: int
    category: str
    title: str
    recommendation: str
    why_recommended: str
    supporting_evidence: Dict[str, Any]
    expected_benefit: str
    confidence_level: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Ranking Request & Item Schemas
class RankingWeights(BaseModel):
    price_weight: float = 0.30
    trust_weight: float = 0.25
    availability_weight: float = 0.15
    quality_weight: float = 0.15
    cancellation_weight: float = 0.15

class RankedProductItem(BaseModel):
    rank: int
    product_id: int
    product_name: str
    product_type: str
    supplier_name: str
    supplier_code: str
    base_price: float
    star_rating: Optional[float] = None
    room_or_activity: Optional[str] = None
    cancellation_policy: str
    availability_status: str
    overall_score: float
    score_breakdown: Dict[str, float]
    explanation: str
    trade_offs: List[str]

# What-If Simulation Schemas
class SimulationRequest(BaseModel):
    scenario_name: str
    excluded_supplier_ids: List[int] = []
    weight_adjustments: RankingWeights = RankingWeights()
    max_price_cap: Optional[float] = None
    require_free_cancellation: Optional[bool] = False

class SimulationResult(BaseModel):
    scenario_name: str
    disclaimer: str
    baseline_summary: Dict[str, Any]
    simulated_summary: Dict[str, Any]
    rank_shifts: List[Dict[str, Any]]
    trade_off_analysis: List[str]
    projected_impact: Dict[str, Any]

# Ingestion Schemas
class IngestionPreviewRow(BaseModel):
    row_index: int
    data: Dict[str, Any]

class IngestionPreviewResponse(BaseModel):
    filename: str
    total_rows: int
    detected_columns: List[str]
    suggested_mapping: Dict[str, str]
    sample_rows: List[Dict[str, Any]]

class IngestionCommitRequest(BaseModel):
    product_type: str # "HOTEL" or "SIGHTSEEING"
    supplier_code: str
    supplier_name: str
    column_mapping: Dict[str, str]
    rows: List[Dict[str, Any]]

class IngestionCommitResponse(BaseModel):
    success: bool
    imported_count: int
    skipped_count: int
    errors: List[str]
    sample_imported_ids: List[int]

