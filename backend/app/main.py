"""Crowd Pulse — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import get_settings
from app.core.database import engine, Base, get_db, SessionLocal
from app.api.routes_sentiment import router as sentiment_router
from app.api.routes_divergence import router as divergence_router
from app.api.routes_market import router as market_router
from app.api.routes_pipeline import router as pipeline_router
from app.api.routes_auth import router as auth_router
from app.api.routes_onboarding import router as onboarding_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    import app.models.api_usage_log  # noqa: F401
    import app.models.user  # noqa: F401
    import app.models.user_config  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Crowd Pulse API ready")
    yield
    logger.info("Shutting down Crowd Pulse API")


app = FastAPI(
    title="Crowd Pulse API",
    description="Hinglish sentiment analysis and contrarian signals for Indian equity markets (Nifty 50)",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(sentiment_router, prefix="/api/v1")
app.include_router(divergence_router, prefix="/api/v1")
app.include_router(market_router, prefix="/api/v1")
app.include_router(pipeline_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "app": "Crowd Pulse",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/status")
def pipeline_status():
    """Return current row counts for all pipeline tables."""
    from app.models.social_post import SocialPost
    from app.models.sentiment_record import SentimentRecord
    from app.models.market_data import MarketData
    from app.models.divergence_signal import DivergenceSignal

    db = SessionLocal()
    try:
        return {
            "social_posts": db.query(SocialPost).count(),
            "sentiment_records": db.query(SentimentRecord).count(),
            "market_data": db.query(MarketData).count(),
            "divergence_signals": db.query(DivergenceSignal).count(),
        }
    finally:
        db.close()


@app.get("/api/v1/stats")
def get_stats(
    hours: int = 24,
    start: str = None,
    end: str = None,
    mode: str = None,
):
    """Return record statistics for the current data mode with optional date filtering."""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from app.models.social_post import SocialPost
    from app.models.sentiment_record import SentimentRecord
    from app.models.divergence_signal import DivergenceSignal
    
    # Resolve mode
    if mode in ("test", "live", "demo"):
        ds = mode
    else:
        ds = _data_mode
    
    # Parse date range
    if start:
        since = datetime.fromisoformat(start)
    else:
        since = datetime.utcnow() - timedelta(hours=hours)
    until = datetime.fromisoformat(end) if end else datetime.utcnow()
    
    db = SessionLocal()
    try:
        # Posts by source with date filtering
        source_counts = (
            db.query(SocialPost.source, func.count(SocialPost.id))
            .filter(
                SocialPost.data_source == ds,
                SocialPost.ingested_at >= since,
                SocialPost.ingested_at <= until,
            )
            .group_by(SocialPost.source)
            .all()
        )
        by_source = {src: cnt for src, cnt in source_counts}
        total_posts = sum(by_source.values())

        # Unique authors (proxy for channels/accounts tracked)
        unique_authors = (
            db.query(func.count(func.distinct(SocialPost.author)))
            .filter(
                SocialPost.data_source == ds,
                SocialPost.ingested_at >= since,
                SocialPost.ingested_at <= until,
            )
            .scalar()
        ) or 0

        # Unique symbols with data
        symbols_tracked = (
            db.query(func.count(func.distinct(SocialPost.symbol)))
            .filter(
                SocialPost.data_source == ds,
                SocialPost.ingested_at >= since,
                SocialPost.ingested_at <= until,
            )
            .scalar()
        ) or 0

        sentiment_count = (
            db.query(func.count(SentimentRecord.id))
            .filter(
                SentimentRecord.data_source == ds,
                SentimentRecord.scored_at >= since,
                SentimentRecord.scored_at <= until,
            )
            .scalar()
        ) or 0

        signal_count = (
            db.query(func.count(DivergenceSignal.id))
            .filter(
                DivergenceSignal.data_source == ds,
                DivergenceSignal.timestamp >= since,
                DivergenceSignal.timestamp <= until,
            )
            .scalar()
        ) or 0

        return {
            "mode": ds,
            "total_posts": total_posts,
            "telegram_posts": by_source.get("telegram", 0),
            "youtube_comments": by_source.get("youtube", 0),
            "twitter_posts": by_source.get("twitter", 0),
            "sentiment_records": sentiment_count,
            "divergence_signals": signal_count,
            "unique_authors": unique_authors,
            "symbols_tracked": symbols_tracked,
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# API Usage Tracking & Data Mode
# ---------------------------------------------------------------------------

@app.get("/api/v1/usage")
def api_usage():
    """Return current API usage for all external services."""
    from app.core.usage_tracker import get_all_usage_summary
    return get_all_usage_summary()


@app.get("/api/v1/data-mode")
def get_data_mode():
    """Return the current data mode (live or test)."""
    return {"mode": _data_mode}


@app.post("/api/v1/data-mode")
def set_data_mode(mode: str = "test"):
    """Switch between 'live' and 'test' data modes."""
    global _data_mode
    if mode not in ("live", "test"):
        return {"error": "mode must be 'live' or 'test'"}
    _data_mode = mode
    logger.info(f"Data mode switched to: {mode}")
    return {"mode": _data_mode}


@app.post("/api/v1/seed")
def trigger_seed():
    """Seed sample data for testing (only works in test mode)."""
    if _data_mode != "test":
        return {"error": "Seed only available in test mode"}
    from app.seed import seed_sample_data
    seed_sample_data()
    return {"status": "seeded", "message": "Sample data created"}


@app.get("/api/v1/usage/logs")
def api_usage_logs(limit: int = 100):
    """Return recent API usage log entries from the database."""
    from app.models.api_usage_log import ApiUsageLog
    from sqlalchemy import desc
    db = SessionLocal()
    try:
        logs = (
            db.query(ApiUsageLog)
            .order_by(desc(ApiUsageLog.called_at))
            .limit(limit)
            .all()
        )
        return {
            "logs": [
                {
                    "id": log.id,
                    "service": log.service,
                    "endpoint": log.endpoint,
                    "status": log.status,
                    "response_time_ms": log.response_time_ms,
                    "records_fetched": log.records_fetched,
                    "error_message": log.error_message,
                    "daily_count": log.daily_count,
                    "daily_limit": log.daily_limit,
                    "called_at": log.called_at.isoformat() if log.called_at else None,
                }
                for log in logs
            ]
        }
    finally:
        db.close()


# Global data mode: "test" = seed data only, "live" = real API calls
_data_mode = "test"
