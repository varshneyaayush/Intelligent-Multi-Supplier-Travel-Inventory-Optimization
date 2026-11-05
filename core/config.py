import os

class Settings:
    PROJECT_NAME: str = "OptiSupply AI"
    TEAM_NAME: str = "ASTRA"
    TEAM_MEMBERS: str = "Sonali and Aayush"
    HACKATHON: str = "VOYAGEHACK 4.0"
    TAGLINE: str = "Transforming Fragmented Travel Inventory into Intelligent Decisions."

    # Brand Colors
    COLOR_SAGE_GREY: str = "#A5A79B"
    COLOR_CREAM_BEIGE: str = "#E8D2B5"
    COLOR_DEEP_BURGUNDY: str = "#590907"
    COLOR_CARD_BG: str = "#FDFCF9"

    @property
    def DATABASE_URL(self) -> str:
        # Check Streamlit secrets if running inside Streamlit
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "DATABASE_URL" in st.secrets:
                return str(st.secrets["DATABASE_URL"])
        except Exception:
            pass
        return os.getenv("DATABASE_URL", "sqlite:///./optisupply.db")

    # ML / AI Thresholds
    DUPLICATE_HIGH_CONFIDENCE_THRESHOLD: float = float(os.getenv("DUPLICATE_HIGH_THRESHOLD", "0.85"))
    DUPLICATE_REVIEW_THRESHOLD: float = float(os.getenv("DUPLICATE_REVIEW_THRESHOLD", "0.60"))
    GEO_MATCH_RADIUS_METERS: float = float(os.getenv("GEO_MATCH_RADIUS_METERS", "500.0"))

    # Price Anomaly Z-Score & IQR thresholds
    PRICE_ZSCORE_THRESHOLD: float = float(os.getenv("PRICE_ZSCORE_THRESHOLD", "2.0"))
    PRICE_IQR_MULTIPLIER: float = float(os.getenv("PRICE_IQR_MULTIPLIER", "1.5"))

    # Sample Data Indicator
    SAMPLE_DATA_INDICATOR: str = "Sample Data (Synthetic Benchmark for Demonstration)"

settings = Settings()

