import logging
from sqlalchemy.orm import Session
from app.models import (
    Supplier, InventoryProduct, DuplicateCandidate, ProductRelationship,
    PriceAnomalyAlert, SupplierMetric, InventoryQualityReport, OptimizationRecommendation
)
from app.ai.duplicate_detector import duplicate_engine
from app.ai.relationship_engine import relationship_engine
from app.ai.price_anomaly import price_engine
from app.ai.supplier_intelligence import supplier_engine
from app.ai.quality_enrichment import quality_engine
from app.ai.recommendation_engine import recommendation_engine

logger = logging.getLogger(__name__)

def seed_demo_data(db: Session, force_reset: bool = False):
    """
    Seeds comprehensive, realistic demonstration datasets for both Hotels and Sightseeing.
    Directly incorporates the Grand Palace Hotel example from the presentation.
    """
    if force_reset:
        db.query(OptimizationRecommendation).delete()
        db.query(InventoryQualityReport).delete()
        db.query(PriceAnomalyAlert).delete()
        db.query(ProductRelationship).delete()
        db.query(DuplicateCandidate).delete()
        db.query(SupplierMetric).delete()
        db.query(InventoryProduct).delete()
        db.query(Supplier).delete()
        db.commit()

    if db.query(Supplier).count() > 0:
        logger.info("Demo data already loaded.")
        return

    # 1. Create Suppliers
    suppliers_data = [
        {
            "code": "SUP_A",
            "name": "Apex Global Travel Wholesalers",
            "contact_email": "connect@apexwholesale.travel",
            "country": "United States",
            "reliability_tier": "Tier 1 (Preferred)",
            "metrics": {
                "price_competitiveness": 86.0,
                "booking_success_rate": 97.4,
                "availability_accuracy": 94.2,
                "cancellation_reliability": 91.0,
                "data_completeness": 92.5,
                "response_time_ms": 185.0,
                "is_synthetic": True
            }
        },
        {
            "code": "SUP_B",
            "name": "Bedrock B2B Inventory Network",
            "contact_email": "partners@bedrocknetwork.com",
            "country": "United Kingdom",
            "reliability_tier": "Tier 1 (Preferred)",
            "metrics": {
                "price_competitiveness": 93.5, # Aggressive discount pricing
                "booking_success_rate": 91.0,
                "availability_accuracy": 88.5,
                "cancellation_reliability": 82.0,
                "data_completeness": 84.0,
                "response_time_ms": 290.0,
                "is_synthetic": True
            }
        },
        {
            "code": "SUP_C",
            "name": "Continental Luxury Res & DMC",
            "contact_email": "b2b@continentalres.eu",
            "country": "France",
            "reliability_tier": "Tier 2 (Standard)",
            "metrics": {
                "price_competitiveness": 68.0, # High luxury rates
                "booking_success_rate": 96.0,
                "availability_accuracy": 95.0,
                "cancellation_reliability": 94.0,
                "data_completeness": 95.0,
                "response_time_ms": 340.0,
                "is_synthetic": True
            }
        },
        {
            "code": "SUP_D",
            "name": "Discovery Local Experiences Group",
            "contact_email": "inventory@discoverylocal.io",
            "country": "Global",
            "reliability_tier": "Tier 2 (Standard)",
            "metrics": {
                "price_competitiveness": 84.0,
                "booking_success_rate": 88.0,
                "availability_accuracy": 86.0,
                "cancellation_reliability": 79.0,
                "data_completeness": 76.0,
                "response_time_ms": 420.0,
                "is_synthetic": True
            }
        }
    ]

    supplier_models = {}
    for s_info in suppliers_data:
        m_info = s_info.pop("metrics")
        sup = Supplier(**s_info)
        db.add(sup)
        db.flush()
        supplier_models[sup.code] = sup

        # Evaluate transparent trust score
        trust_eval = supplier_engine.compute_trust_score(m_info)
        metric_record = SupplierMetric(
            supplier_id=sup.id,
            price_competitiveness=m_info["price_competitiveness"],
            booking_success_rate=m_info["booking_success_rate"],
            availability_accuracy=m_info["availability_accuracy"],
            cancellation_reliability=m_info["cancellation_reliability"],
            data_completeness=m_info["data_completeness"],
            response_time_ms=m_info["response_time_ms"],
            trust_score=trust_eval["trust_score"],
            score_breakdown=trust_eval["score_breakdown"],
            strengths=trust_eval["strengths"],
            weaknesses=trust_eval["weaknesses"],
            is_synthetic=True
        )
        db.add(metric_record)

    db.commit()

    # 2. Seed Hotel Products
    # Specific Scenario from prompt & presentation:
    # Supplier A: Grand Palace Hotel — Deluxe King — $120
    # Supplier B: The Grand Palace — Deluxe Room — $98
    # Supplier C: Grand Palace Hotel & Spa — Deluxe Room — $145
    hotels_data = [
        # The Core Grand Palace Benchmark Scenario
        {
            "supplier_code": "SUP_A",
            "external_id": "APX-HTL-7741",
            "product_type": "HOTEL",
            "name": "Grand Palace Hotel",
            "description": "Prestigious 5-star historic hotel in central Paris with luxurious suites, high-speed Wi-Fi, swimming pool, luxury spa, and fine dining.",
            "city": "Paris",
            "country": "France",
            "address": "14 Rue du Palais, 75001 Paris",
            "latitude": 48.860611,
            "longitude": 2.337644,
            "star_rating": 5.0,
            "room_category": "Deluxe King",
            "amenities": ["WiFi", "Pool", "Spa", "Fitness Center", "Restaurant"],
            "currency": "USD",
            "base_price": 120.00,
            "tax_amount": 14.40,
            "cancellation_policy": "Free Cancellation 48h",
            "availability_status": "Available",
            "data_completeness_score": 0.98
        },
        {
            "supplier_code": "SUP_B",
            "external_id": "BDR-HTL-9024",
            "product_type": "HOTEL",
            "name": "The Grand Palace",
            "description": "Centrally located luxury palace hotel situated in the 1st arrondissement. Near Louvre museum. Features pool, spa, and air conditioning.",
            "city": "Paris",
            "country": "France",
            "address": "14 Rue du Palais, 75001 Paris",
            "latitude": 48.860635,
            "longitude": 2.337612,
            "star_rating": 5.0,
            "room_category": "Deluxe Room",
            "amenities": ["WiFi", "Pool", "Spa"],
            "currency": "USD",
            "base_price": 98.00, # Lowest rate - aggressive discount
            "tax_amount": 11.76,
            "cancellation_policy": "Non-refundable",
            "availability_status": "Available",
            "data_completeness_score": 0.92
        },
        {
            "supplier_code": "SUP_C",
            "external_id": "CNT-HTL-1102",
            "product_type": "HOTEL",
            "name": "Grand Palace Hotel & Spa",
            "description": "5-star historic palace hotel in central Paris offering opulent suites, wellness spa and gourmet restaurant. Breakfast included.",
            "city": "Paris",
            "country": "France",
            "address": "14 Rue du Palais, Paris",
            "latitude": 48.860590,
            "longitude": 2.337680,
            "star_rating": 5.0,
            "room_category": "Deluxe Room",
            "amenities": ["WiFi", "Pool", "Spa", "Restaurant", "Breakfast"],
            "currency": "USD",
            "base_price": 145.00, # Substantial premium rate
            "tax_amount": 17.40,
            "cancellation_policy": "Free Cancellation 24h",
            "availability_status": "Available",
            "data_completeness_score": 0.95
        },
        # Different room category in same Grand Palace
        {
            "supplier_code": "SUP_A",
            "external_id": "APX-HTL-7742",
            "product_type": "HOTEL",
            "name": "Grand Palace Hotel",
            "description": "Palatial presidential suite overlooking the Tuileries Gardens with marble bathroom and butler service.",
            "city": "Paris",
            "country": "France",
            "address": "14 Rue du Palais, 75001 Paris",
            "latitude": 48.860611,
            "longitude": 2.337644,
            "star_rating": 5.0,
            "room_category": "Presidential Royal Suite",
            "amenities": ["WiFi", "Pool", "Spa", "Butler Service", "Balcony"],
            "currency": "USD",
            "base_price": 420.00,
            "tax_amount": 50.40,
            "cancellation_policy": "Flexible 7d",
            "availability_status": "Limited",
            "data_completeness_score": 0.95
        },
        # Alternative Hotel in same district
        {
            "supplier_code": "SUP_B",
            "external_id": "BDR-HTL-8831",
            "product_type": "HOTEL",
            "name": "Hotel Regina Louvre",
            "description": "Charming Parisian boutique hotel directly facing the Louvre pyramid with elegant antique furnishings.",
            "city": "Paris",
            "country": "France",
            "address": "2 Place des Pyramides, 75001 Paris",
            "latitude": 48.863380,
            "longitude": 2.332350, # ~500m away
            "star_rating": 5.0,
            "room_category": "Prestige Room",
            "amenities": ["WiFi", "Bar", "Fitness Center"],
            "currency": "USD",
            "base_price": 135.00,
            "tax_amount": 16.20,
            "cancellation_policy": "Free Cancellation 48h",
            "availability_status": "Available",
            "data_completeness_score": 0.88
        },
        # Incomplete / Low Quality Record to demonstrate Feature 6
        {
            "supplier_code": "SUP_D",
            "external_id": "DSC-HTL-0419",
            "product_type": "HOTEL",
            "name": "Eiffel River View Lodge",
            "description": "Cozy rooms with views of the Seine and complimentary high-speed Wi-Fi, air conditioning, and on-site restaurant.",
            "city": "Paris",
            "country": "France",
            "address": None, # Missing address
            "latitude": None, # Missing coords
            "longitude": None,
            "star_rating": 4.0,
            "room_category": "Standard Double",
            "amenities": [], # Missing amenities array (can be enriched from description)
            "currency": "USD",
            "base_price": 89.00,
            "tax_amount": 10.68,
            "cancellation_policy": "Non-refundable",
            "availability_status": "Available",
            "data_completeness_score": 0.55
        }
    ]

    # 3. Seed Sightseeing / Travel Experiences
    experiences_data = [
        # Pair 1: Louvre Museum Guided Tours across Suppliers (High Confidence Duplicate)
        {
            "supplier_code": "SUP_A",
            "external_id": "APX-EXP-3011",
            "product_type": "SIGHTSEEING",
            "name": "Louvre Museum Skip-the-Line Express Guided Tour",
            "description": "Priority entrance with expert art historian guide covering the Mona Lisa, Venus de Milo, and masterworks in 2 hours.",
            "city": "Paris",
            "country": "France",
            "address": "Pyramide du Louvre, 75001 Paris",
            "latitude": 48.860611,
            "longitude": 2.335500,
            "duration_hours": 2.0,
            "activity_type": "Guided Museum Tour",
            "inclusions": ["Skip-the-line Ticket", "Licensed English Guide", "Headsets"],
            "exclusions": ["Hotel Pickup", "Food & Drinks"],
            "meeting_point": "Arc de Triomphe du Carrousel",
            "currency": "USD",
            "base_price": 68.00,
            "tax_amount": 0.0,
            "cancellation_policy": "Free Cancellation 24h",
            "availability_status": "Available",
            "data_completeness_score": 0.95
        },
        {
            "supplier_code": "SUP_B",
            "external_id": "BDR-EXP-4022",
            "product_type": "SIGHTSEEING",
            "name": "Louvre Skip-the-Line Masterpieces Tour with Guide",
            "description": "Fast-track admission to the Louvre with licensed guide to see the Mona Lisa and classical treasures in 2 hours.",
            "city": "Paris",
            "country": "France",
            "address": "Louvre Museum Main Entrance, Paris",
            "latitude": 48.860640,
            "longitude": 2.335480,
            "duration_hours": 2.0,
            "activity_type": "Guided Museum Tour",
            "inclusions": ["Admission Ticket", "Professional Guide", "Headsets"],
            "exclusions": ["Gratuities"],
            "meeting_point": "Carrousel Arch, Place du Carrousel",
            "currency": "USD",
            "base_price": 54.00, # Competitive discount
            "tax_amount": 0.0,
            "cancellation_policy": "Non-refundable",
            "availability_status": "Available",
            "data_completeness_score": 0.90
        },
        # Related Experience: Seine River Cruise
        {
            "supplier_code": "SUP_A",
            "external_id": "APX-EXP-3055",
            "product_type": "SIGHTSEEING",
            "name": "Seine River 1-Hour Illuminations Sightseeing Cruise",
            "description": "Scenic panoramic boat cruise on the River Seine with audio commentary passing Eiffel Tower, Notre Dame, and Louvre.",
            "city": "Paris",
            "country": "France",
            "address": "Port de la Bourdonnais, 75007 Paris",
            "latitude": 48.859200,
            "longitude": 2.296500,
            "duration_hours": 1.0,
            "activity_type": "Boat Cruise",
            "inclusions": ["1-Hour Cruise Ticket", "Multi-language Audio Commentary"],
            "exclusions": ["Food & Beverages"],
            "meeting_point": "Pont d'Iena Pier 3",
            "currency": "USD",
            "base_price": 18.00,
            "tax_amount": 0.0,
            "cancellation_policy": "Free Cancellation 24h",
            "availability_status": "Available",
            "data_completeness_score": 0.92
        },
        {
            "supplier_code": "SUP_C",
            "external_id": "CNT-EXP-7108",
            "product_type": "SIGHTSEEING",
            "name": "Gourmet Dinner Cruise on the Seine with Live Music",
            "description": "Refined 3-course French dining cruise along illuminated Parisian monuments with live singer and wine pairing.",
            "city": "Paris",
            "country": "France",
            "address": "Port Solferino, Paris",
            "latitude": 48.862100,
            "longitude": 2.324200,
            "duration_hours": 2.5,
            "activity_type": "Dinner Cruise",
            "inclusions": ["3-Course Dinner", "Champagne Aperitif", "Wine Pairing", "2.5-Hour River Cruise"],
            "exclusions": ["Transfers"],
            "meeting_point": "Solferino Quay, Musee d'Orsay footbridge",
            "currency": "USD",
            "base_price": 140.00,
            "tax_amount": 14.00,
            "cancellation_policy": "Free Cancellation 48h",
            "availability_status": "Available",
            "data_completeness_score": 0.94
        },
        # Desert Safari Scenario (Dubai)
        {
            "supplier_code": "SUP_B",
            "external_id": "BDR-EXP-5510",
            "product_type": "SIGHTSEEING",
            "name": "Dubai Desert Safari with Dune Bashing, Camel Ride & BBQ",
            "description": "Adrenaline dune bashing in 4x4 land cruiser, sandboarding, camel riding, and live belly dance dinner show in Arabian desert.",
            "city": "Dubai",
            "country": "United Arab Emirates",
            "address": "Al Awir Desert, Dubai",
            "latitude": 25.185200,
            "longitude": 55.532100,
            "duration_hours": 6.0,
            "activity_type": "Desert Safari",
            "inclusions": ["4x4 Dune Bashing", "BBQ Buffet Dinner", "Camel Ride", "Hotel Pickup & Drop-off"],
            "exclusions": ["Quad Bike Rental"],
            "meeting_point": "Complimentary Hotel Pickup in Dubai",
            "currency": "USD",
            "base_price": 42.00,
            "tax_amount": 2.10,
            "cancellation_policy": "Free Cancellation 24h",
            "availability_status": "Available",
            "data_completeness_score": 0.96
        },
        {
            "supplier_code": "SUP_D",
            "external_id": "DSC-EXP-8891",
            "product_type": "SIGHTSEEING",
            "name": "Evening Desert Dune Adventure & Bedouin Feast",
            "description": "Exciting 4WD desert safari over red dunes with camel riding, henna tattoos, and grilled barbecue dinner buffet under the stars.",
            "city": "Dubai",
            "country": "United Arab Emirates",
            "address": "Lahbab Desert, Dubai",
            "latitude": 25.184800,
            "longitude": 55.533200,
            "duration_hours": 6.0,
            "activity_type": "Desert Safari",
            "inclusions": ["Dune Bashing", "BBQ Dinner", "Hotel Pickup"],
            "exclusions": ["Alcoholic Drinks"],
            "meeting_point": "Hotel Lobby Pickup",
            "currency": "USD",
            "base_price": 38.00,
            "tax_amount": 1.90,
            "cancellation_policy": "Non-refundable",
            "availability_status": "Available",
            "data_completeness_score": 0.90
        }
    ]

    all_products_raw = hotels_data + experiences_data
    created_products = []

    for item in all_products_raw:
        s_code = item.pop("supplier_code")
        supplier = supplier_models[s_code]
        prod = InventoryProduct(supplier_id=supplier.id, **item)
        db.add(prod)
        db.flush()
        created_products.append(prod)

    db.commit()

    # 4. Run AI Intelligence pipelines to populate relationships, duplicates, anomalies, quality reports
    _run_initial_ai_analysis(db, created_products)


def _run_initial_ai_analysis(db: Session, products: list):
    """Executes AI algorithms across seeded inventory."""
    prod_dicts = []
    for p in products:
        d = {
            "id": p.id,
            "supplier_id": p.supplier_id,
            "supplier_name": p.supplier.name,
            "supplier_code": p.supplier.code,
            "supplier_trust_score": p.supplier.metrics.trust_score if p.supplier.metrics else 80.0,
            "external_id": p.external_id,
            "product_type": p.product_type,
            "name": p.name,
            "description": p.description,
            "city": p.city,
            "country": p.country,
            "address": p.address,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "star_rating": p.star_rating,
            "room_category": p.room_category,
            "amenities": p.amenities,
            "duration_hours": p.duration_hours,
            "activity_type": p.activity_type,
            "inclusions": p.inclusions,
            "base_price": p.base_price,
            "currency": p.currency,
            "cancellation_policy": p.cancellation_policy,
            "availability_status": p.availability_status,
            "data_completeness_score": p.data_completeness_score
        }
        prod_dicts.append(d)

    # 1. Duplicate & Relationship Analysis (Pairwise comparison)
    n = len(prod_dicts)
    for i in range(n):
        for j in range(i + 1, n):
            p1 = prod_dicts[i]
            p2 = prod_dicts[j]
            if p1["product_type"] != p2["product_type"]:
                continue

            # Duplicate evaluation
            dup_res = duplicate_engine.compare_pair(p1, p2)
            if dup_res["overall_confidence"] >= 0.50:
                dup_rec = DuplicateCandidate(
                    product_a_id=p1["id"],
                    product_b_id=p2["id"],
                    overall_confidence=dup_res["overall_confidence"],
                    name_similarity=dup_res["name_similarity"],
                    geo_distance_meters=dup_res["geo_distance_meters"],
                    geo_similarity=dup_res["geo_similarity"],
                    semantic_similarity=dup_res["semantic_similarity"],
                    attribute_similarity=dup_res["attribute_similarity"],
                    match_classification=dup_res["match_classification"],
                    evidence_breakdown=dup_res["evidence_breakdown"],
                    status="PENDING"
                )
                db.add(dup_rec)

            # Relationship evaluation
            rel_res = relationship_engine.classify_relationship(p1, p2)
            if rel_res is not None:
                rel_rec = ProductRelationship(
                    source_product_id=p1["id"],
                    target_product_id=p2["id"],
                    relationship_type=rel_res["relationship_type"],
                    confidence_score=rel_res["confidence_score"],
                    evidence=rel_res["evidence"]
                )
                db.add(rel_rec)

    # 2. Price Anomaly Analysis
    # Group by city & product_type to find comparable clusters
    clusters = {}
    for p in prod_dicts:
        key = (p.get("city") or "General", p.get("product_type"))
        clusters.setdefault(key, []).append(p)

    for key, cluster_prods in clusters.items():
        anomalies = price_engine.detect_group_anomalies(cluster_prods)
        for a in anomalies:
            alert = PriceAnomalyAlert(
                product_id=a["product_id"],
                observed_price=a["observed_price"],
                baseline_price=a["baseline_price"],
                price_diff_pct=a["price_diff_pct"],
                anomaly_type=a["anomaly_type"],
                detection_method=a["detection_method"],
                severity=a["severity"],
                explanation=a["explanation"],
                status="PENDING"
            )
            db.add(alert)

    # 3. Quality & Enrichment Analysis
    for p in prod_dicts:
        q_res = quality_engine.evaluate_quality(p)
        q_rec = InventoryQualityReport(
            product_id=p["id"],
            completeness_score=q_res["completeness_score"],
            missing_fields=q_res["missing_fields"],
            inconsistencies=q_res["inconsistencies"],
            enrichment_suggestions=q_res["enrichment_suggestions"],
            status="PENDING"
        )
        db.add(q_rec)

    db.commit()

    # 4. Actionable Recommendations Synthesis
    dups_list = [
        {
            "match_classification": d.match_classification,
            "status": d.status,
            "overall_confidence": d.overall_confidence,
            "geo_distance_meters": d.geo_distance_meters,
            "product_a": {"name": d.product_a.name, "supplier_name": d.product_a.supplier.name},
            "product_b": {"name": d.product_b.name, "supplier_name": d.product_b.supplier.name}
        }
        for d in db.query(DuplicateCandidate).all()
    ]
    anom_list = [
        {
            "severity": a.severity,
            "status": a.status,
            "observed_price": a.observed_price,
            "baseline_price": a.baseline_price,
            "price_diff_pct": a.price_diff_pct,
            "product": {"name": a.product.name}
        }
        for a in db.query(PriceAnomalyAlert).all()
    ]
    supp_list = [
        {
            "name": s.name,
            "code": s.code,
            "metrics": {
                "trust_score": s.metrics.trust_score if s.metrics else 80.0,
                "weaknesses": s.metrics.weaknesses if s.metrics else []
            }
        }
        for s in db.query(Supplier).all()
    ]
    qual_list = [
        {
            "completeness_score": q.completeness_score,
            "missing_fields": q.missing_fields
        }
        for q in db.query(InventoryQualityReport).all()
    ]

    recs = recommendation_engine.generate_recommendations(dups_list, anom_list, supp_list, qual_list)
    for r in recs:
        rec_model = OptimizationRecommendation(
            category=r["category"],
            title=r["title"],
            recommendation=r["recommendation"],
            why_recommended=r["why_recommended"],
            supporting_evidence=r["supporting_evidence"],
            expected_benefit=r["expected_benefit"],
            confidence_level=r["confidence_level"],
            status="ACTIVE"
        )
        db.add(rec_model)

    db.commit()
    logger.info("Demo data seeding and AI intelligence pipelines completed successfully.")

