"""Crowd Pulse Pipeline CLI — run the full pipeline manually without Celery.

Usage:
    python -m app.pipeline --all                   # Run full pipeline
    python -m app.pipeline --ingest                # Only data ingestion
    python -m app.pipeline --score                 # Only sentiment scoring
    python -m app.pipeline --signals               # Only signal computation
    python -m app.pipeline --market                # Only market data fetch
    python -m app.pipeline --seed                  # Seed sample data for testing
"""

import argparse
import sys
from loguru import logger

from app.core.database import engine, Base


def init_db():
    """Create all tables if they don't exist."""
    # Import all models so Base.metadata knows about them
    import app.models.social_post  # noqa: F401
    import app.models.sentiment_record  # noqa: F401
    import app.models.market_data  # noqa: F401
    import app.models.divergence_signal  # noqa: F401
    import app.models.api_usage_log  # noqa: F401

    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database ready")


def run_ingestion():
    """Run all data ingestion tasks sequentially."""
    from app.workers.tasks import ingest_telegram, ingest_youtube, ingest_twitter

    logger.info("=== Starting Data Ingestion ===")

    logger.info("--- Telegram ---")
    try:
        ingest_telegram()
    except Exception as e:
        logger.warning(f"Telegram ingestion failed (may not be configured): {e}")

    logger.info("--- YouTube ---")
    try:
        ingest_youtube()
    except Exception as e:
        logger.warning(f"YouTube ingestion failed (may not be configured): {e}")

    logger.info("--- Twitter ---")
    try:
        ingest_twitter()
    except Exception as e:
        logger.warning(f"Twitter ingestion failed (may not be configured): {e}")

    logger.info("=== Ingestion Complete ===")


def run_market_data():
    """Fetch market data for Nifty 50."""
    from app.workers.tasks import fetch_market_data

    logger.info("=== Fetching Market Data ===")
    fetch_market_data()
    logger.info("=== Market Data Complete ===")


def run_scoring():
    """Score all unprocessed posts."""
    from app.workers.tasks import score_sentiment

    logger.info("=== Scoring Sentiment ===")
    score_sentiment()
    logger.info("=== Scoring Complete ===")


def run_signals():
    """Compute divergence + velocity + confidence signals."""
    from app.workers.tasks import compute_all_signals

    logger.info("=== Computing Signals ===")
    compute_all_signals()
    logger.info("=== Signals Complete ===")


def run_seed():
    """Seed sample data for testing the pipeline without live APIs."""
    from app.seed import seed_sample_data

    logger.info("=== Seeding Sample Data (test) ===")
    seed_sample_data()
    logger.info("=== Seed Complete ===")


def run_seed_live():
    """Seed sample data with data_source=live for testing live-mode charts."""
    from app.seed import seed_sample_data

    logger.info("=== Seeding Sample Data (live) ===")
    seed_sample_data(data_source="live")
    logger.info("=== Live Seed Complete ===")


def run_seed_realistic():
    """Seed realistic test data with natural sentiment patterns."""
    from app.seed_realistic import seed_realistic_data

    logger.info("=== Seeding Realistic Test Data ===")
    seed_realistic_data()
    logger.info("=== Realistic Seed Complete ===")


def run_all():
    """Run the complete pipeline end-to-end."""
    init_db()
    run_ingestion()
    run_market_data()
    run_scoring()
    run_signals()
    logger.info("========================================")
    logger.info("  Full pipeline run complete!")
    logger.info("  Start the API: uvicorn app.main:app")
    logger.info("========================================")


def run_status():
    """Print current pipeline status (row counts)."""
    from app.core.database import SessionLocal
    from app.models.social_post import SocialPost
    from app.models.sentiment_record import SentimentRecord
    from app.models.market_data import MarketData
    from app.models.divergence_signal import DivergenceSignal

    db = SessionLocal()
    try:
        posts = db.query(SocialPost).count()
        scored = db.query(SentimentRecord).count()
        market = db.query(MarketData).count()
        signals = db.query(DivergenceSignal).count()

        logger.info("=== Pipeline Status ===")
        logger.info(f"  Social Posts:       {posts}")
        logger.info(f"  Sentiment Records:  {scored}")
        logger.info(f"  Market Data Rows:   {market}")
        logger.info(f"  Divergence Signals: {signals}")
        logger.info(f"  Unscored Posts:     {posts - scored}")
        logger.info("=======================")
    finally:
        db.close()


def run_usage():
    """Print API usage summary for today."""
    from app.core.usage_tracker import get_all_usage_summary

    summary = get_all_usage_summary()
    logger.info(f"=== API Usage ({summary['date']}) ===")
    for service in ["telegram", "youtube", "twitter", "yfinance", "gemini"]:
        svc = summary.get(service, {})
        used = svc.get("used", 0)
        limit = svc.get("limit", 0)
        pct = svc.get("percent_used", 0)
        status = "BLOCKED" if svc.get("blocked") else f"{svc.get('remaining', 0)} left"
        bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
        logger.info(f"  {service:<10} [{bar}] {used}/{limit} ({pct:.0f}%) — {status}")
    logger.info("================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crowd Pulse Pipeline CLI")
    parser.add_argument("--all", action="store_true", help="Run full pipeline")
    parser.add_argument("--ingest", action="store_true", help="Run data ingestion only")
    parser.add_argument("--market", action="store_true", help="Fetch market data only")
    parser.add_argument("--score", action="store_true", help="Score sentiment only")
    parser.add_argument("--signals", action="store_true", help="Compute signals only")
    parser.add_argument("--seed", action="store_true", help="Seed sample test data")
    parser.add_argument("--seed-live", action="store_true", help="Seed sample data with data_source=live (for testing live charts)")
    parser.add_argument("--seed-realistic", action="store_true", help="Seed realistic test data with natural sentiment patterns")
    parser.add_argument("--status", action="store_true", help="Show pipeline status")
    parser.add_argument("--usage", action="store_true", help="Show API usage for today")
    parser.add_argument("--init-db", action="store_true", help="Initialize database tables")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    if args.init_db or args.all or args.seed or args.seed_live or args.seed_realistic:
        init_db()

    if args.seed:
        run_seed()
    elif args.seed_live:
        run_seed_live()
    elif args.seed_realistic:
        run_seed_realistic()
    elif args.all:
        run_all()
    else:
        if args.ingest:
            run_ingestion()
        if args.market:
            run_market_data()
        if args.score:
            run_scoring()
        if args.signals:
            run_signals()

    if args.status or args.all or args.seed:
        run_status()

    if args.usage or args.all or args.ingest or args.market:
        run_usage()
