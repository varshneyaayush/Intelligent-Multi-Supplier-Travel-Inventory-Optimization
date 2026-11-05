import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.services.demo_data import seed_demo_data

from app.routers import (
    inventory, duplicates, relationships, suppliers,
    anomalies, ranking, quality, recommendations,
    simulation, analytics, review
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("optisupply")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed initial demo dataset if database is fresh
    db = SessionLocal()
    try:
        seed_demo_data(db, force_reset=False)
    finally:
        db.close()
    
    logger.info("OptiSupply AI backend initialized successfully.")
    yield
    logger.info("OptiSupply AI backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=f"{settings.TAGLINE} | Hackathon: {settings.HACKATHON} | Team: {settings.TEAM_NAME} ({settings.TEAM_MEMBERS})",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup for seamless React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all modular routers
app.include_router(inventory.router)
app.include_router(duplicates.router)
app.include_router(relationships.router)
app.include_router(suppliers.router)
app.include_router(anomalies.router)
app.include_router(ranking.router)
app.include_router(quality.router)
app.include_router(recommendations.router)
app.include_router(simulation.router)
app.include_router(analytics.router)
app.include_router(review.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "team": settings.TEAM_NAME,
        "members": settings.TEAM_MEMBERS,
        "hackathon": settings.HACKATHON,
        "tagline": settings.TAGLINE,
        "database": "connected",
        "capabilities": [
            "Multimodal Duplicate Detection",
            "Intelligent Product Relationships",
            "Supplier Intelligence & Trust Scoring",
            "Dynamic Price Anomaly Detection",
            "Intelligent Supplier & Product Ranking",
            "Inventory Quality & Content Enrichment",
            "Human-in-the-Loop Review Center",
            "Inventory Optimization Recommendations",
            "AI Insights & Analytics Dashboard",
            "What-If Simulation & Optimization"
        ]
    }

