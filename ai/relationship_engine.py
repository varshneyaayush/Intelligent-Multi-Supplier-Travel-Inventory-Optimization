import logging
from typing import Dict, Any, Optional
from ai.duplicate_detector import DuplicateDetectionEngine

logger = logging.getLogger(__name__)

class RelationshipEngine:
    def __init__(self):
        self.detector = DuplicateDetectionEngine()

    def classify_relationship(self, prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Classifies the relationship between two inventory items:
        - SAME_PROPERTY_DIFFERENT_SUPPLIER
        - DIFFERENT_ROOM_CATEGORY
        - RELATED_EXPERIENCE
        - ALTERNATIVE_HOTEL
        - ALTERNATIVE_EXPERIENCE
        """
        type_a = prod_a.get("product_type")
        type_b = prod_b.get("product_type")
        if type_a != type_b:
            return None

        if prod_a.get("id") == prod_b.get("id"):
            return None

        is_hotel = (type_a == "HOTEL")
        name_sim = self.detector.compute_fuzzy_similarity(prod_a.get("name"), prod_b.get("name"))
        
        # Geo distance
        geo_dist = self.detector.haversine_distance(
            prod_a.get("latitude"), prod_a.get("longitude"),
            prod_b.get("latitude"), prod_b.get("longitude")
        )

        city_a = str(prod_a.get("city") or "").lower().strip()
        city_b = str(prod_b.get("city") or "").lower().strip()
        same_city = (city_a == city_b) and len(city_a) > 0

        supplier_a = prod_a.get("supplier_id")
        supplier_b = prod_b.get("supplier_id")
        different_supplier = (supplier_a != supplier_b)

        if is_hotel:
            room_a = str(prod_a.get("room_category") or "").lower().strip()
            room_b = str(prod_b.get("room_category") or "").lower().strip()
            room_sim = self.detector.compute_fuzzy_similarity(room_a, room_b) if (room_a and room_b) else 1.0

            # 1. Check if same property, same room category across different suppliers
            if name_sim >= 0.82 and (geo_dist is None or geo_dist <= 300.0):
                if room_sim >= 0.75:
                    return {
                        "relationship_type": "SAME_PROPERTY_DIFFERENT_SUPPLIER",
                        "confidence_score": round(name_sim, 2),
                        "evidence": {
                            "description": "Identical hotel property and room tier offered by competing suppliers.",
                            "hotel_name_similarity": f"{name_sim * 100:.1f}%",
                            "room_category_a": prod_a.get("room_category") or "Standard Room",
                            "room_category_b": prod_b.get("room_category") or "Standard Room",
                            "geographical_distance": f"{geo_dist:.1f}m" if geo_dist is not None else "Address match",
                            "supplier_a": prod_a.get("supplier_name"),
                            "supplier_b": prod_b.get("supplier_name"),
                        }
                    }
                else:
                    # 2. Same property, but different room categories (e.g. Deluxe King vs Suite)
                    return {
                        "relationship_type": "DIFFERENT_ROOM_CATEGORY",
                        "confidence_score": round(name_sim, 2),
                        "evidence": {
                            "description": "Same underlying hotel property, but representing distinct room categories or upgrades.",
                            "hotel_name": prod_a.get("name"),
                            "room_tier_source": prod_a.get("room_category") or "Room Option A",
                            "room_tier_target": prod_b.get("room_category") or "Room Option B",
                            "room_similarity": f"{room_sim * 100:.1f}%",
                            "geographical_distance": f"{geo_dist:.1f}m" if geo_dist is not None else "Same premises",
                        }
                    }

            # 3. Check for Alternative Hotel (same city, close radius < 3.5km, similar star rating)
            if same_city and (geo_dist is not None and geo_dist <= 3500.0):
                star_a = prod_a.get("star_rating")
                star_b = prod_b.get("star_rating")
                if star_a and star_b and abs(float(star_a) - float(star_b)) <= 1.0:
                    return {
                        "relationship_type": "ALTERNATIVE_HOTEL",
                        "confidence_score": round(max(0.6, 1.0 - (geo_dist / 4000.0)), 2),
                        "evidence": {
                            "description": f"Viable alternative property in {prod_a.get('city')} within {geo_dist/1000:.1f}km radius.",
                            "distance_km": round(geo_dist / 1000.0, 2),
                            "star_rating_source": star_a,
                            "star_rating_target": star_b,
                            "price_comparison": f"${prod_a.get('base_price')} vs ${prod_b.get('base_price')}"
                        }
                    }
        else:
            # Sightseeing / Experiences
            act_a = str(prod_a.get("activity_type") or "").lower().strip()
            act_b = str(prod_b.get("activity_type") or "").lower().strip()
            dur_a = prod_a.get("duration_hours")
            dur_b = prod_b.get("duration_hours")

            # 1. Same core experience offered by competing suppliers
            if name_sim >= 0.80 and same_city:
                return {
                    "relationship_type": "SAME_PROPERTY_DIFFERENT_SUPPLIER",
                    "confidence_score": round(name_sim, 2),
                    "evidence": {
                        "description": "Same core sightseeing tour / ticket inventory sourced from different suppliers.",
                        "tour_name_similarity": f"{name_sim * 100:.1f}%",
                        "activity_type": prod_a.get("activity_type"),
                        "duration_source": f"{dur_a}h" if dur_a else "Flexible",
                        "duration_target": f"{dur_b}h" if dur_b else "Flexible",
                        "supplier_a": prod_a.get("supplier_name"),
                        "supplier_b": prod_b.get("supplier_name")
                    }
                }

            # 2. Related Experience (same attraction or activity type in same city)
            if same_city and (act_a == act_b or name_sim >= 0.50):
                return {
                    "relationship_type": "RELATED_EXPERIENCE",
                    "confidence_score": round(max(0.65, name_sim), 2),
                    "evidence": {
                        "description": "Related travel activity at or around the same landmark/theme in the destination.",
                        "city": prod_a.get("city"),
                        "activity_category": prod_a.get("activity_type") or prod_b.get("activity_type"),
                        "keyword_alignment": f"{name_sim * 100:.1f}%",
                    }
                }

            # 3. Alternative Experience (general alternative in same city)
            if same_city:
                return {
                    "relationship_type": "ALTERNATIVE_EXPERIENCE",
                    "confidence_score": 0.55,
                    "evidence": {
                        "description": f"Alternative activity available for travelers visiting {prod_a.get('city')}.",
                        "city": prod_a.get("city"),
                        "activity_source": prod_a.get("activity_type"),
                        "activity_target": prod_b.get("activity_type")
                    }
                }

        return None

relationship_engine = RelationshipEngine()

