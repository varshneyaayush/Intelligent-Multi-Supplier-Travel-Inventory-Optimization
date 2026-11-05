import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from core.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # e.g. "SUP_A", "SUP_B"
    name = Column(String(200), nullable=False)
    contact_email = Column(String(200), nullable=True)
    country = Column(String(100), default="Global")
    reliability_tier = Column(String(50), default="Standard")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    products = relationship("InventoryProduct", back_populates="supplier", cascade="all, delete-orphan")
    metrics = relationship("SupplierMetric", back_populates="supplier", uselist=False, cascade="all, delete-orphan")


class InventoryProduct(Base):
    __tablename__ = "inventory_products"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    external_id = Column(String(100), nullable=False, index=True)
    product_type = Column(String(20), nullable=False, index=True) # "HOTEL" or "SIGHTSEEING"
    
    # Core attributes
    name = Column(String(300), nullable=False, index=True)
    description = Column(Text, nullable=True)
    city = Column(String(100), nullable=True, index=True)
    country = Column(String(100), nullable=True)
    address = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Hotel specific attributes
    star_rating = Column(Float, nullable=True)
    room_category = Column(String(150), nullable=True)
    amenities = Column(JSON, nullable=True)
    
    # Sightseeing specific attributes
    duration_hours = Column(Float, nullable=True)
    inclusions = Column(JSON, nullable=True)
    exclusions = Column(JSON, nullable=True)
    meeting_point = Column(String(300), nullable=True)
    activity_type = Column(String(100), nullable=True)
    
    # Commercial & Booking attributes
    currency = Column(String(10), default="USD")
    base_price = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    cancellation_policy = Column(String(100), default="Non-refundable")
    availability_status = Column(String(50), default="Available")
    
    # Quality & Ingestion metadata
    data_completeness_score = Column(Float, default=1.0)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    anomalies = relationship("PriceAnomalyAlert", back_populates="product", cascade="all, delete-orphan")
    quality_report = relationship("InventoryQualityReport", back_populates="product", uselist=False, cascade="all, delete-orphan")


class DuplicateCandidate(Base):
    __tablename__ = "duplicate_candidates"

    id = Column(Integer, primary_key=True, index=True)
    product_a_id = Column(Integer, ForeignKey("inventory_products.id", ondelete="CASCADE"), nullable=False, index=True)
    product_b_id = Column(Integer, ForeignKey("inventory_products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    overall_confidence = Column(Float, nullable=False, index=True) # 0.0 - 1.0
    name_similarity = Column(Float, nullable=False)
    geo_distance_meters = Column(Float, nullable=True)
    geo_similarity = Column(Float, nullable=True)
    semantic_similarity = Column(Float, nullable=False)
    attribute_similarity = Column(Float, nullable=False)
    
    match_classification = Column(String(50), nullable=False, index=True) # "HIGH_CONFIDENCE", "POSSIBLE_REVIEW", "UNLIKELY"
    evidence_breakdown = Column(JSON, nullable=False)
    
    status = Column(String(30), default="PENDING", index=True) # "PENDING", "APPROVED", "REJECTED"
    review_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    product_a = relationship("InventoryProduct", foreign_keys=[product_a_id])
    product_b = relationship("InventoryProduct", foreign_keys=[product_b_id])


class ProductRelationship(Base):
    __tablename__ = "product_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_product_id = Column(Integer, ForeignKey("inventory_products.id", ondelete="CASCADE"), nullable=False, index=True)
    target_product_id = Column(Integer, ForeignKey("inventory_products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    relationship_type = Column(String(100), nullable=False, index=True)
    # Types:
    # "SAME_PROPERTY_DIFFERENT_SUPPLIER"
    # "DIFFERENT_ROOM_CATEGORY"
    # "RELATED_EXPERIENCE"
    # "ALTERNATIVE_HOTEL"
    # "ALTERNATIVE_EXPERIENCE"
    
    confidence_score = Column(Float, nullable=False)
    evidence = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    source_product = relationship("InventoryProduct", foreign_keys=[source_product_id])
    target_product = relationship("InventoryProduct", foreign_keys=[target_product_id])


class PriceAnomalyAlert(Base):
    __tablename__ = "price_anomaly_alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("inventory_products.id", ondelete="CASCADE"), nullable=False, index=True)
    
    observed_price = Column(Float, nullable=False)
    baseline_price = Column(Float, nullable=False)
    price_diff_pct = Column(Float, nullable=False)
    
    anomaly_type = Column(String(50), nullable=False, index=True) # "HIGH_PRICE", "LOW_PRICE", "SUPPLIER_DISPARITY", "CURRENCY_INCONSISTENCY"
    detection_method = Column(String(50), nullable=False) # "IQR", "Z_SCORE", "ISOLATION_FOREST"
    severity = Column(String(20), nullable=False, index=True) # "HIGH", "MEDIUM", "LOW"
    
    explanation = Column(Text, nullable=False)
    status = Column(String(30), default="PENDING", index=True) # "PENDING", "DISMISSED", "RESOLVED"
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("InventoryProduct", back_populates="anomalies")


class SupplierMetric(Base):
    __tablename__ = "supplier_metrics"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    price_competitiveness = Column(Float, default=85.0)
    booking_success_rate = Column(Float, default=95.0)
    availability_accuracy = Column(Float, default=92.0)
    cancellation_reliability = Column(Float, default=90.0)
    data_completeness = Column(Float, default=88.0)
    response_time_ms = Column(Float, default=240.0)
    
    trust_score = Column(Float, nullable=False)
    score_breakdown = Column(JSON, nullable=False)
    strengths = Column(JSON, nullable=False)
    weaknesses = Column(JSON, nullable=False)
    is_synthetic = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    supplier = relationship("Supplier", back_populates="metrics")


class InventoryQualityReport(Base):
    __tablename__ = "inventory_quality_reports"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("inventory_products.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    completeness_score = Column(Float, nullable=False)
    missing_fields = Column(JSON, nullable=False)
    inconsistencies = Column(JSON, nullable=False)
    enrichment_suggestions = Column(JSON, nullable=False)
    status = Column(String(30), default="PENDING")
    reviewed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    product = relationship("InventoryProduct", back_populates="quality_report")


class OptimizationRecommendation(Base):
    __tablename__ = "optimization_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    
    title = Column(String(250), nullable=False)
    recommendation = Column(Text, nullable=False)
    why_recommended = Column(Text, nullable=False)
    supporting_evidence = Column(JSON, nullable=False)
    expected_benefit = Column(String(250), nullable=False)
    confidence_level = Column(String(30), default="High")
    status = Column(String(30), default="ACTIVE", index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    parameters = Column(JSON, nullable=False)
    baseline_metrics = Column(JSON, nullable=False)
    simulated_metrics = Column(JSON, nullable=False)
    trade_offs = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    decision = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

