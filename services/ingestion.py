import io
import re
import pandas as pd
import logging
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Standard canonical fields for mapping
STANDARD_FIELDS = {
    "name": ["name", "hotel_name", "property_name", "title", "tour_name", "experience_name", "activity_name"],
    "external_id": ["id", "external_id", "product_id", "code", "sku", "item_id", "hotel_id"],
    "city": ["city", "destination", "location_city", "town", "metro"],
    "country": ["country", "nation", "country_code"],
    "address": ["address", "street", "street_address", "location"],
    "latitude": ["lat", "latitude", "coord_lat", "geo_lat"],
    "longitude": ["lon", "lng", "longitude", "coord_lon", "geo_lon"],
    "base_price": ["price", "base_price", "rate", "cost", "amount", "room_rate", "ticket_price"],
    "currency": ["currency", "curr", "price_currency"],
    "description": ["description", "desc", "overview", "summary", "details"],
    "star_rating": ["stars", "star_rating", "rating", "hotel_stars"],
    "room_category": ["room", "room_category", "room_type", "room_name"],
    "amenities": ["amenities", "facilities", "features", "hotel_amenities"],
    "cancellation_policy": ["cancellation", "cancellation_policy", "cancel_policy", "refund_policy"],
    "availability_status": ["availability", "status", "inventory_status", "in_stock"],
    "duration_hours": ["duration", "duration_hours", "hours", "tour_duration"],
    "meeting_point": ["meeting_point", "pickup_point", "meeting_location"],
    "activity_type": ["activity_type", "category", "tour_type", "experience_type"],
    "inclusions": ["inclusions", "included", "whats_included"],
    "exclusions": ["exclusions", "excluded", "not_included"],
}

class IngestionService:
    @staticmethod
    def parse_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
        """Parses CSV or Excel file into a Pandas DataFrame."""
        if filename.endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin1")
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise ValueError("Unsupported file format. Please upload CSV or XLSX.")
        
        # Strip string whitespace from column names
        df.columns = [str(c).strip() for c in df.columns]
        return df

    @staticmethod
    def suggest_column_mapping(columns: List[str]) -> Dict[str, str]:
        """Automatically suggests mapping from uploaded columns to canonical schema fields."""
        mapping = {}
        for col in columns:
            clean_col = re.sub(r"[^a-zA-Z0-9_]", "", col.lower().replace(" ", "_"))
            matched_field = None
            
            # Pass 1: Exact alias match
            for standard_field, aliases in STANDARD_FIELDS.items():
                if clean_col in aliases:
                    matched_field = standard_field
                    break
            
            # Pass 2: Word boundary or prefix match if not exact
            if not matched_field:
                tokens = clean_col.split("_")
                for standard_field, aliases in STANDARD_FIELDS.items():
                    if any(t in aliases for t in tokens):
                        # Avoid generic "name" overtaking "city_name"
                        if "city" in tokens and standard_field == "city":
                            matched_field = "city"
                            break
                        if standard_field != "name" or clean_col in ["name", "hotel_name", "tour_name"]:
                            matched_field = standard_field
                            break

            # Pass 3: Fallback substring
            if not matched_field:
                for standard_field, aliases in STANDARD_FIELDS.items():
                    if any(alias in clean_col for alias in aliases):
                        matched_field = standard_field
                        break

            if matched_field:
                mapping[col] = matched_field
        return mapping

    @staticmethod
    def validate_and_normalize_row(
        row: Dict[str, Any],
        column_mapping: Dict[str, str],
        product_type: str
    ) -> Tuple[Optional[Dict[str, Any]], List[str]]:
        """
        Validates an individual row according to mapped columns.
        Returns (normalized_dict, errors_list).
        """
        errors = []
        normalized: Dict[str, Any] = {
            "product_type": product_type,
            "raw_payload": row
        }

        # Invert mapping: standard_field -> original_column
        reverse_map = {std: orig for orig, std in column_mapping.items() if std}

        # 1. Product Name (Mandatory)
        name_col = reverse_map.get("name")
        name_val = row.get(name_col) if name_col else None
        if not name_val or pd.isna(name_val) or str(name_val).strip() == "":
            errors.append("Missing mandatory 'name' attribute.")
        else:
            normalized["name"] = str(name_val).strip()

        # 2. External ID
        ext_col = reverse_map.get("external_id")
        ext_val = row.get(ext_col) if ext_col else None
        if ext_val and not pd.isna(ext_val):
            normalized["external_id"] = str(ext_val).strip()
        else:
            # Generate deterministic fallback ID
            fallback = re.sub(r"[^a-zA-Z0-9]", "", normalized.get("name", "item"))[:12].upper()
            normalized["external_id"] = f"EXT_{fallback}"

        # 3. Base Price (Mandatory)
        price_col = reverse_map.get("base_price")
        price_val = row.get(price_col) if price_col else None
        try:
            if price_val is not None and not pd.isna(price_val):
                clean_p = re.sub(r"[^\d.]", "", str(price_val))
                p_float = float(clean_p)
                if p_float <= 0:
                    errors.append(f"Price must be greater than zero (found: {price_val}).")
                normalized["base_price"] = p_float
            else:
                errors.append("Missing mandatory 'base_price' attribute.")
        except Exception:
            errors.append(f"Invalid numeric value for base_price: '{price_val}'.")

        # 4. Currency
        curr_col = reverse_map.get("currency")
        curr_val = row.get(curr_col) if curr_col else None
        normalized["currency"] = str(curr_val).strip().upper() if (curr_val and not pd.isna(curr_val)) else "USD"

        # 5. Location attributes
        city_col = reverse_map.get("city")
        normalized["city"] = str(row[city_col]).strip() if (city_col and not pd.isna(row.get(city_col))) else None

        country_col = reverse_map.get("country")
        normalized["country"] = str(row[country_col]).strip() if (country_col and not pd.isna(row.get(country_col))) else None

        addr_col = reverse_map.get("address")
        normalized["address"] = str(row[addr_col]).strip() if (addr_col and not pd.isna(row.get(addr_col))) else None

        # Coordinates
        lat_col = reverse_map.get("latitude")
        if lat_col and not pd.isna(row.get(lat_col)):
            try:
                lat = float(row[lat_col])
                if -90 <= lat <= 90:
                    normalized["latitude"] = lat
                else:
                    errors.append(f"Latitude out of bounds: {lat}")
            except Exception:
                errors.append(f"Invalid numeric latitude: {row[lat_col]}")

        lon_col = reverse_map.get("longitude")
        if lon_col and not pd.isna(row.get(lon_col)):
            try:
                lon = float(row[lon_col])
                if -180 <= lon <= 180:
                    normalized["longitude"] = lon
                else:
                    errors.append(f"Longitude out of bounds: {lon}")
            except Exception:
                errors.append(f"Invalid numeric longitude: {row[lon_col]}")

        # Description
        desc_col = reverse_map.get("description")
        normalized["description"] = str(row[desc_col]).strip() if (desc_col and not pd.isna(row.get(desc_col))) else None

        # Cancellation Policy
        cancel_col = reverse_map.get("cancellation_policy")
        normalized["cancellation_policy"] = str(row[cancel_col]).strip() if (cancel_col and not pd.isna(row.get(cancel_col))) else "Non-refundable"

        # Availability Status
        avail_col = reverse_map.get("availability_status")
        normalized["availability_status"] = str(row[avail_col]).strip() if (avail_col and not pd.isna(row.get(avail_col))) else "Available"

        # Hotel or Sightseeing fields
        if product_type == "HOTEL":
            star_col = reverse_map.get("star_rating")
            if star_col and not pd.isna(row.get(star_col)):
                try:
                    normalized["star_rating"] = float(row[star_col])
                except Exception:
                    pass
            
            room_col = reverse_map.get("room_category")
            normalized["room_category"] = str(row[room_col]).strip() if (room_col and not pd.isna(row.get(room_col))) else "Standard Room"

            amen_col = reverse_map.get("amenities")
            if amen_col and not pd.isna(row.get(amen_col)):
                amen_raw = str(row[amen_col])
                normalized["amenities"] = [a.strip() for a in re.split(r"[,;|]", amen_raw) if a.strip()]
            else:
                normalized["amenities"] = []

        else:
            # SIGHTSEEING
            act_col = reverse_map.get("activity_type")
            normalized["activity_type"] = str(row[act_col]).strip() if (act_col and not pd.isna(row.get(act_col))) else "Guided Experience"

            dur_col = reverse_map.get("duration_hours")
            if dur_col and not pd.isna(row.get(dur_col)):
                try:
                    normalized["duration_hours"] = float(row[dur_col])
                except Exception:
                    pass

            meet_col = reverse_map.get("meeting_point")
            normalized["meeting_point"] = str(row[meet_col]).strip() if (meet_col and not pd.isna(row.get(meet_col))) else None

            inc_col = reverse_map.get("inclusions")
            if inc_col and not pd.isna(row.get(inc_col)):
                inc_raw = str(row[inc_col])
                normalized["inclusions"] = [i.strip() for i in re.split(r"[,;|]", inc_raw) if i.strip()]
            else:
                normalized["inclusions"] = []

        return (normalized if not errors else None), errors

ingestion_service = IngestionService()

