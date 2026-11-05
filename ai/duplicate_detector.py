import math
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Fallback-safe fuzzy string matching
try:
    from rapidfuzz import fuzz
except ImportError:
    import difflib
    class FuzzFallback:
        @staticmethod
        def token_sort_ratio(s1: str, s2: str) -> float:
            if not s1 or not s2:
                return 0.0
            t1 = " ".join(sorted(str(s1).lower().split()))
            t2 = " ".join(sorted(str(s2).lower().split()))
            return difflib.SequenceMatcher(None, t1, t2).ratio() * 100.0

        @staticmethod
        def token_set_ratio(s1: str, s2: str) -> float:
            if not s1 or not s2:
                return 0.0
            tokens1 = set(str(s1).lower().split())
            tokens2 = set(str(s2).lower().split())
            common = tokens1.intersection(tokens2)
            if not common:
                return difflib.SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio() * 100.0
            sorted_common = " ".join(sorted(common))
            sorted_t1 = " ".join(sorted(tokens1))
            sorted_t2 = " ".join(sorted(tokens2))
            r1 = difflib.SequenceMatcher(None, sorted_common, sorted_t1).ratio()
            r2 = difflib.SequenceMatcher(None, sorted_common, sorted_t2).ratio()
            r3 = difflib.SequenceMatcher(None, sorted_t1, sorted_t2).ratio()
            return max(r1, r2, r3) * 100.0

    fuzz = FuzzFallback()

# Lazy-loaded transformer model
_sentence_model = None
_sentence_model_initialized = False

class DuplicateDetectionEngine:
    def __init__(self):
        self._model = None
        self._tfidf_vectorizer = None

    def _get_sentence_model(self):
        global _sentence_model, _sentence_model_initialized
        if not _sentence_model_initialized:
            _sentence_model_initialized = True
            try:
                from sentence_transformers import SentenceTransformer
                # Load from local cache with local_files_only=True to prevent network hang
                _sentence_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
            except Exception:
                logger.info("SentenceTransformer local model not present. Using TF-IDF semantic vectorizer.")
                _sentence_model = False
        return _sentence_model if _sentence_model is not False else None

    @staticmethod
    def haversine_distance(lat1: Optional[float], lon1: Optional[float], lat2: Optional[float], lon2: Optional[float]) -> Optional[float]:
        """Calculates distance in meters between two lat/lon points using Haversine formula."""
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return None
        try:
            r = 6371000.0  # Earth radius in meters
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)

            a = math.sin(delta_phi / 2.0) ** 2 + \
                math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
            c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
            return r * c
        except Exception:
            return None

    def compute_fuzzy_similarity(self, s1: Optional[str], s2: Optional[str]) -> float:
        """Token sort ratio normalized to 0.0 - 1.0"""
        if not s1 or not s2:
            return 0.0
        s1_clean = str(s1).lower().strip()
        s2_clean = str(s2).lower().strip()
        if s1_clean == s2_clean:
            return 1.0
        # Combination of token_set_ratio and token_sort_ratio
        ratio_sort = fuzz.token_sort_ratio(s1_clean, s2_clean) / 100.0
        ratio_set = fuzz.token_set_ratio(s1_clean, s2_clean) / 100.0
        return max(ratio_sort, ratio_set)

    def compute_semantic_similarity(self, text1: Optional[str], text2: Optional[str]) -> Tuple[float, str]:
        """Calculates semantic similarity using Sentence Transformers or TF-IDF fallback."""
        if not text1 or not text2:
            return 0.0, "Missing description"

        t1 = str(text1).strip()
        t2 = str(text2).strip()
        if t1.lower() == t2.lower():
            return 1.0, "Exact description match"

        model = self._get_sentence_model()
        if model is not None:
            try:
                embeddings = model.encode([t1, t2], normalize_embeddings=True)
                sim = float((embeddings[0] * embeddings[1]).sum())
                return max(0.0, min(1.0, sim)), "Sentence-Transformers (all-MiniLM-L6-v2)"
            except Exception as e:
                logger.warning(f"Error computing transformer embedding: {e}")

        # Fallback using Scikit-Learn TF-IDF Cosine Similarity
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            matrix = vec.fit_transform([t1, t2])
            sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
            return max(0.0, min(1.0, sim)), "TF-IDF Cosine Similarity (grounded semantic model)"
        except Exception:
            return self.compute_fuzzy_similarity(t1, t2), "Character N-gram Overlap (fallback)"

    def compare_pair(self, prod_a: Dict[str, Any], prod_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Multimodal comparison of two inventory records (hotels or sightseeing).
        Combines:
        - Name similarity (token sort/set ratio)
        - Geographic distance (Haversine formula in meters)
        - Semantic description similarity (Sentence Transformers / TF-IDF)
        - Attribute consistency (Star rating, room category, activity type, duration)
        """
        # 1. Name Similarity
        name_sim = self.compute_fuzzy_similarity(prod_a.get("name"), prod_b.get("name"))
        
        # 2. Geo Proximity
        lat1, lon1 = prod_a.get("latitude"), prod_a.get("longitude")
        lat2, lon2 = prod_b.get("latitude"), prod_b.get("longitude")
        geo_dist = self.haversine_distance(lat1, lon1, lat2, lon2)
        
        geo_sim = None
        geo_notes = "Coordinates unavailable"
        if geo_dist is not None:
            if geo_dist <= 50.0:
                geo_sim = 1.0
                geo_notes = f"Exact coordinates ({geo_dist:.1f}m apart)"
            elif geo_dist <= 250.0:
                geo_sim = 0.90
                geo_notes = f"Immediate vicinity ({geo_dist:.1f}m apart)"
            elif geo_dist <= 1000.0:
                geo_sim = 0.70
                geo_notes = f"Same neighborhood ({geo_dist:.0f}m apart)"
            elif geo_dist <= 5000.0:
                geo_sim = 0.35
                geo_notes = f"Same metropolitan district ({geo_dist/1000:.1f}km apart)"
            else:
                geo_sim = 0.05
                geo_notes = f"Distant locations ({geo_dist/1000:.1f}km apart)"
        else:
            # Fallback to address text similarity
            addr_a = f"{prod_a.get('address') or ''} {prod_a.get('city') or ''}".strip()
            addr_b = f"{prod_b.get('address') or ''} {prod_b.get('city') or ''}".strip()
            if addr_a and addr_b:
                geo_sim = self.compute_fuzzy_similarity(addr_a, addr_b)
                geo_notes = f"Fuzzy address text match ({geo_sim*100:.1f}%)"

        # 3. Semantic Similarity
        desc_a = prod_a.get("description") or prod_a.get("name") or ""
        desc_b = prod_b.get("description") or prod_b.get("name") or ""
        semantic_sim, sem_model_used = self.compute_semantic_similarity(desc_a, desc_b)

        # 4. Attribute Similarity
        attr_scores = []
        is_hotel = prod_a.get("product_type") == "HOTEL"
        
        if is_hotel:
            # Star rating comparison
            star_a = prod_a.get("star_rating")
            star_b = prod_b.get("star_rating")
            if star_a is not None and star_b is not None:
                attr_scores.append(1.0 if star_a == star_b else max(0.0, 1.0 - abs(star_a - star_b) * 0.3))
            
            # City comparison
            city_a = prod_a.get("city")
            city_b = prod_b.get("city")
            if city_a and city_b:
                attr_scores.append(1.0 if str(city_a).lower() == str(city_b).lower() else 0.0)

            # Room type similarity
            room_a = prod_a.get("room_category")
            room_b = prod_b.get("room_category")
            if room_a and room_b:
                room_sim = self.compute_fuzzy_similarity(room_a, room_b)
                attr_scores.append(room_sim)
        else:
            # Sightseeing attributes
            act_a = prod_a.get("activity_type")
            act_b = prod_b.get("activity_type")
            if act_a and act_b:
                attr_scores.append(1.0 if str(act_a).lower() == str(act_b).lower() else 0.4)
                
            dur_a = prod_a.get("duration_hours")
            dur_b = prod_b.get("duration_hours")
            if dur_a is not None and dur_b is not None:
                diff = abs(dur_a - dur_b)
                attr_scores.append(max(0.0, 1.0 - diff * 0.25))

        attr_sim = sum(attr_scores) / len(attr_scores) if attr_scores else 0.80

        # Weighted Ensemble Confidence Score
        if geo_sim is not None:
            overall_confidence = (
                0.40 * name_sim +
                0.30 * geo_sim +
                0.20 * semantic_sim +
                0.10 * attr_sim
            )
        else:
            overall_confidence = (
                0.55 * name_sim +
                0.30 * semantic_sim +
                0.15 * attr_sim
            )

        overall_confidence = round(max(0.0, min(1.0, overall_confidence)), 4)

        # Classification based on thresholds
        if overall_confidence >= 0.85:
            classification = "HIGH_CONFIDENCE"
            explanation = "High multi-modal alignment across property name, geographical proximity, and content semantics."
        elif overall_confidence >= 0.60:
            classification = "POSSIBLE_REVIEW"
            explanation = "Potential duplicate listing detected with moderate similarity. Human review recommended to verify distinctions."
        else:
            classification = "UNLIKELY"
            explanation = "Low overall match confidence. Products appear to represent distinct inventory items."

        evidence = {
            "name_similarity_pct": round(name_sim * 100, 1),
            "geo_proximity_notes": geo_notes,
            "geo_distance_meters": round(geo_dist, 1) if geo_dist is not None else None,
            "geo_similarity_pct": round(geo_sim * 100, 1) if geo_sim is not None else None,
            "semantic_similarity_pct": round(semantic_sim * 100, 1),
            "semantic_model": sem_model_used,
            "attribute_similarity_pct": round(attr_sim * 100, 1),
            "summary_explanation": explanation,
            "key_matching_factors": [
                f"Name match: {round(name_sim * 100)}%",
                geo_notes,
                f"Content semantic alignment: {round(semantic_sim * 100)}%",
            ]
        }

        return {
            "overall_confidence": overall_confidence,
            "name_similarity": round(name_sim, 4),
            "geo_distance_meters": geo_dist,
            "geo_similarity": round(geo_sim, 4) if geo_sim is not None else None,
            "semantic_similarity": round(semantic_sim, 4),
            "attribute_similarity": round(attr_sim, 4),
            "match_classification": classification,
            "evidence_breakdown": evidence
        }

duplicate_engine = DuplicateDetectionEngine()
