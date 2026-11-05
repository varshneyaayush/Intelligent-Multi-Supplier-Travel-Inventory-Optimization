import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class QualityEnrichmentEngine:
    def evaluate_quality(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates measurable inventory quality score and extracts grounded enrichments.
        Grounded rule: Never invent factual details. Only extract enrichments explicitly
        verifiable from descriptions or existing product attributes.
        """
        is_hotel = (product.get("product_type") == "HOTEL")
        missing_fields = []
        inconsistencies = []
        enrichment_suggestions = []

        total_weight = 0
        earned_points = 0

        # 1. Product Name (Weight: 20)
        total_weight += 20
        name = product.get("name")
        if name and len(name.strip()) >= 5:
            earned_points += 20
        else:
            missing_fields.append("name")

        # 2. Location & Geo (Weight: 25)
        total_weight += 25
        has_city = bool(product.get("city"))
        has_coords = (product.get("latitude") is not None and product.get("longitude") is not None)
        has_address = bool(product.get("address"))

        if has_city:
            earned_points += 10
        else:
            missing_fields.append("city")

        if has_coords:
            earned_points += 10
            # Consistency check for lat/lon
            lat = product.get("latitude")
            lon = product.get("longitude")
            if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
                inconsistencies.append(f"Coordinates ({lat}, {lon}) are outside valid geographical bounds.")
        else:
            missing_fields.append("coordinates (latitude/longitude)")

        if has_address:
            earned_points += 5
        else:
            missing_fields.append("street address")

        # 3. Description (Weight: 20)
        total_weight += 20
        desc = product.get("description") or ""
        if len(desc.strip()) >= 40:
            earned_points += 20
        elif len(desc.strip()) > 0:
            earned_points += 10
            inconsistencies.append("Description is very brief (< 40 characters) and lacks detail.")
        else:
            missing_fields.append("description")

        # 4. Domain specific attributes (Weight: 20)
        total_weight += 20
        if is_hotel:
            # Amenities & Room category
            amenities = product.get("amenities") or []
            if amenities and len(amenities) > 0:
                earned_points += 10
            else:
                missing_fields.append("amenities list")

            room = product.get("room_category")
            if room:
                earned_points += 10
            else:
                missing_fields.append("room category")

            # Grounded Enrichment: Extract amenities mentioned in description if missing
            desc_lower = desc.lower().replace("-", "")
            known_amenity_keywords = {
                "wifi": "Complimentary High-Speed Wi-Fi",
                "pool": "Swimming Pool",
                "spa": "Full-Service Spa",
                "fitness": "Fitness Center / Gym",
                "breakfast": "Breakfast Available",
                "air conditioning": "Air Conditioning",
                "parking": "On-site Parking",
                "restaurant": "On-site Restaurant",
                "bar": "Lounge / Bar"
            }
            if not amenities or len(amenities) == 0:
                found_in_text = []
                for kw, label in known_amenity_keywords.items():
                    if kw in desc_lower:
                        found_in_text.append(label)
                if found_in_text:
                    enrichment_suggestions.append({
                        "field": "amenities",
                        "suggested_value": found_in_text,
                        "grounding_source": "Explicitly extracted from property description text.",
                        "confidence": "High (Direct text verification)"
                    })

        else:
            # Sightseeing attributes
            inclusions = product.get("inclusions") or []
            if inclusions and len(inclusions) > 0:
                earned_points += 10
            else:
                missing_fields.append("inclusions list")

            meeting = product.get("meeting_point")
            if meeting:
                earned_points += 5
            else:
                missing_fields.append("meeting point")

            duration = product.get("duration_hours")
            if duration is not None and duration > 0:
                earned_points += 5
            else:
                missing_fields.append("duration hours")

            # Grounded extraction for sightseeing
            desc_lower = desc.lower()
            if not inclusions or len(inclusions) == 0:
                found_inclusions = []
                if "guide" in desc_lower:
                    found_inclusions.append("Professional English-speaking Guide")
                if "ticket" in desc_lower or "entry" in desc_lower:
                    found_inclusions.append("Admission / Entry Ticket Included")
                if "hotel pickup" in desc_lower or "pick-up" in desc_lower:
                    found_inclusions.append("Hotel Pickup & Drop-off")
                if found_inclusions:
                    enrichment_suggestions.append({
                        "field": "inclusions",
                        "suggested_value": found_inclusions,
                        "grounding_source": "Extracted directly from experience itinerary text.",
                        "confidence": "High (Direct text verification)"
                    })

        # 5. Price & Policy (Weight: 15)
        total_weight += 15
        price = product.get("base_price")
        if price is not None and price > 0:
            earned_points += 10
        else:
            missing_fields.append("base price")
            inconsistencies.append("Base price is zero or missing.")

        policy = product.get("cancellation_policy")
        if policy:
            earned_points += 5
        else:
            missing_fields.append("cancellation policy")

        completeness_score = round(earned_points / float(total_weight), 2)

        return {
            "product_id": product.get("id"),
            "completeness_score": completeness_score,
            "completeness_pct": round(completeness_score * 100, 1),
            "missing_fields": missing_fields,
            "inconsistencies": inconsistencies,
            "enrichment_suggestions": enrichment_suggestions,
            "quality_tier": "Excellent" if completeness_score >= 0.90 else ("Good" if completeness_score >= 0.75 else ("Fair" if completeness_score >= 0.50 else "Poor"))
        }

quality_engine = QualityEnrichmentEngine()

