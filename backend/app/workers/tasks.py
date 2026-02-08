"""Crowd Pulse pipeline tasks.

Works both as Celery tasks (when Redis is available) and as plain functions
(when called from `python -m app.pipeline`). Compatible with PostgreSQL and MySQL.

Pipeline flow:
  1. ingest_telegram / ingest_youtube / ingest_twitter  → social_posts table
  2. fetch_market_data                                  → market_data table
  3. score_sentiment (clean → NLP → symbol extraction)  → sentiment_records table
  4. compute_all_signals (velocity + divergence + conf)  → divergence_signals table
"""

import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import pandas as pd
from loguru import logger

from app.workers.celery_app import celery_app, CELERY_AVAILABLE
from app.core.database import SessionLocal
from app.core.constants import NIFTY_50_SYMBOLS
from app.models.social_post import SocialPost
from app.models.sentiment_record import SentimentRecord
from app.models.market_data import MarketData
from app.models.divergence_signal import DivergenceSignal


# ---------------------------------------------------------------------------
# Decorator helper: use @celery_app.task when Celery is available, else no-op
# ---------------------------------------------------------------------------

def _optional_task(**kwargs):
    """Return the real Celery task decorator or a pass-through."""
    if CELERY_AVAILABLE and celery_app is not None:
        return celery_app.task(**kwargs)
    # No Celery → return identity decorator so functions stay callable
    def identity(fn):
        return fn
    return identity


# ---------------------------------------------------------------------------
# Layer 1: Data Ingestion Tasks
# ---------------------------------------------------------------------------

@_optional_task(name="app.workers.tasks.ingest_telegram")
def ingest_telegram(user_id: int | None = None):
    """Fetch new messages from Telegram channels and store them."""
    from app.ingestion.telegram_scraper import scrape_all_channels
    from app.core.user_sources import get_telegram_channels, get_telegram_session

    channels = get_telegram_channels(user_id)
    session_string = get_telegram_session(user_id)

    logger.info(f"Starting Telegram ingestion ({len(channels)} channels)")
    try:
        messages = asyncio.run(scrape_all_channels(
            channels=channels, session_string=session_string
        ))
    except RuntimeError as e:
        if "event loop" in str(e).lower():
            loop = asyncio.new_event_loop()
            try:
                messages = loop.run_until_complete(
                    scrape_all_channels(channels=channels, session_string=session_string)
                )
            finally:
                loop.close()
        else:
            raise

    _store_posts(messages)
    logger.info(f"Telegram ingestion complete: {len(messages)} messages")


@_optional_task(name="app.workers.tasks.ingest_youtube")
def ingest_youtube(user_id: int | None = None):
    """Fetch new comments from YouTube videos and store them."""
    from app.ingestion.youtube_scraper import scrape_all_videos
    from app.core.user_sources import get_youtube_video_ids

    video_ids = get_youtube_video_ids(user_id)
    logger.info(f"Starting YouTube ingestion ({len(video_ids)} videos)")
    comments = scrape_all_videos(video_ids=video_ids)
    _store_posts(comments)
    logger.info(f"YouTube ingestion complete: {len(comments)} comments")


@_optional_task(name="app.workers.tasks.ingest_twitter")
def ingest_twitter(user_id: int | None = None):
    """Fetch new tweets and store them."""
    from app.ingestion.twitter_scraper import scrape_all_queries
    from app.core.user_sources import get_twitter_queries

    queries = get_twitter_queries(user_id)
    logger.info(f"Starting Twitter ingestion ({len(queries)} queries)")
    tweets = scrape_all_queries(queries=queries)
    _store_posts(tweets)
    logger.info(f"Twitter ingestion complete: {len(tweets)} tweets")


@_optional_task(name="app.workers.tasks.ingest_reddit")
def ingest_reddit(user_id: int | None = None):
    """Fetch new Reddit posts/comments and store them."""
    from app.ingestion.reddit_scraper import scrape_all_subreddits
    from app.core.user_sources import get_reddit_subreddits

    subreddits = get_reddit_subreddits(user_id)
    logger.info(f"Starting Reddit ingestion ({len(subreddits)} subreddits)")
    posts = scrape_all_subreddits(subreddits=subreddits)
    _store_posts(posts)
    logger.info(f"Reddit ingestion complete: {len(posts)} posts/comments")


@_optional_task(name="app.workers.tasks.fetch_market_data")
def fetch_market_data():
    """Fetch latest market data for Nifty 50 stocks."""
    from app.ingestion.market_data import fetch_nifty50_data

    logger.info("Starting market data fetch")
    records = fetch_nifty50_data(period="5d")

    from app.main import _data_mode

    db = SessionLocal()
    try:
        for rec in records:
            rec["data_source"] = _data_mode
            db.merge(MarketData(**rec))
        db.commit()
        logger.info(f"Market data stored: {len(records)} records ({_data_mode} mode)")
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing market data: {e}")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Layer 2 + 3: Preprocessing & Sentiment Scoring
# ---------------------------------------------------------------------------

@_optional_task(name="app.workers.tasks.score_sentiment")
def score_sentiment():
    """Clean, extract symbols, and score unprocessed social posts.
    
    Uses hybrid scoring: Gemini for Hinglish, FinBERT for English.
    Falls back to FinBERT if Gemini is unavailable.
    """
    from app.nlp.preprocessor import clean_text, extract_stock_mentions
    from app.nlp.hybrid_scorer import score_texts_hybrid
    from app.main import _data_mode

    db = SessionLocal()
    try:
        scored_ids = db.query(SentimentRecord.post_id).subquery()
        unscored = (
            db.query(SocialPost)
            .filter(
                SocialPost.id.notin_(scored_ids),
                SocialPost.data_source == _data_mode
            )
            .limit(200)
            .all()
        )

        if not unscored:
            logger.info("No unscored posts found")
            return

        # Clean texts
        cleaned = []
        for p in unscored:
            c = clean_text(p.raw_text)
            cleaned.append(c)
            if not p.cleaned_text:
                p.cleaned_text = c

        # Extract symbols and assign to posts that don't have one
        # Posts without a specific stock mention get assigned "NIFTY" (general market sentiment)
        for p in unscored:
            if not p.symbol:
                symbols = extract_stock_mentions(p.raw_text, NIFTY_50_SYMBOLS)
                if symbols:
                    p.symbol = symbols[0]
                else:
                    p.symbol = "NIFTY"

        # Hybrid batch scoring: Gemini for Hinglish, FinBERT for English
        results = score_texts_hybrid(cleaned)

        for post, result in zip(unscored, results):
            record = SentimentRecord(
                post_id=post.id,
                symbol=post.symbol,
                label=result["label"],
                score=result["score"],
                model_version=result.get("scorer", "hybrid"),
                data_source=_data_mode,
            )
            db.add(record)

        db.commit()
        scored_gemini = sum(1 for r in results if r.get("scorer") == "gemini")
        scored_finbert = sum(1 for r in results if r.get("scorer") == "finbert")
        logger.info(f"Scored {len(unscored)} posts (Gemini: {scored_gemini}, FinBERT: {scored_finbert})")

    except Exception as e:
        db.rollback()
        logger.error(f"Error scoring sentiment: {e}")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Layer 4: Divergence + Velocity + Confidence Signal Computation
# ---------------------------------------------------------------------------

@_optional_task(name="app.workers.tasks.compute_all_signals")
def compute_all_signals():
    """Full signal computation: score → velocity → divergence → confidence → store."""
    # Step 1: Ensure latest posts are scored
    score_sentiment()

    from app.engine.divergence import compute_divergence, classify_divergence
    from app.engine.confidence import (
        compute_confidence,
        estimate_data_sufficiency,
        estimate_signal_consistency,
    )
    from app.nlp.velocity import get_latest_velocity
    from app.main import _data_mode

    db = SessionLocal()
    try:
        now = datetime.utcnow()
        since = now - timedelta(hours=24)
        signals_created = 0

        for symbol in NIFTY_50_SYMBOLS:
            signal = _compute_symbol_signal(
                db, symbol, since, now, _data_mode,
                compute_divergence, classify_divergence,
                compute_confidence, estimate_data_sufficiency,
                estimate_signal_consistency, get_latest_velocity,
            )
            if signal:
                db.add(signal)
                signals_created += 1

        db.commit()
        logger.info(f"Signal computation complete: {signals_created} symbols updated")

    except Exception as e:
        db.rollback()
        logger.error(f"Error computing signals: {e}")
    finally:
        db.close()


def _compute_symbol_signal(
    db, symbol, since, now, data_mode,
    compute_divergence, classify_divergence,
    compute_confidence, estimate_data_sufficiency,
    estimate_signal_consistency, get_latest_velocity,
):
    """Compute divergence signal for a single symbol. Returns DivergenceSignal or None."""

    # --- Fetch raw sentiment records (DB-agnostic, no date_trunc) ---
    sent_rows = (
        db.query(SentimentRecord.scored_at, SentimentRecord.score, SentimentRecord.label)
        .filter(
            SentimentRecord.symbol == symbol,
            SentimentRecord.scored_at >= since,
            SentimentRecord.data_source == data_mode,
        )
        .order_by(SentimentRecord.scored_at)
        .all()
    )

    if len(sent_rows) < 2:
        return None

    # --- Aggregate discussion volume per hour (Python-side, works on any DB) ---
    hourly_counts = defaultdict(lambda: {"count": 0, "score_sum": 0.0})
    for r in sent_rows:
        hour_key = r.scored_at.replace(minute=0, second=0, microsecond=0)
        hourly_counts[hour_key]["count"] += 1
        hourly_counts[hour_key]["score_sum"] += r.score

    if len(hourly_counts) < 1:
        return None

    total_count = sum(v["count"] for v in hourly_counts.values())
    avg_score = sum(v["score_sum"] for v in hourly_counts.values()) / total_count if total_count else 0

    # --- Fetch market data (DB-agnostic) ---
    market_rows = (
        db.query(MarketData.date, MarketData.delivery_volume)
        .filter(
            MarketData.symbol == symbol,
            MarketData.date >= since,
            MarketData.delivery_volume.isnot(None),
        )
        .order_by(MarketData.date)
        .all()
    )

    # --- Velocity ---
    velocity_60m = 50.0  # default midpoint
    if len(sent_rows) >= 3:
        sent_df = pd.DataFrame(
            [{"timestamp": r.scored_at, "sentiment_score": r.score} for r in sent_rows]
        )
        sent_df["timestamp"] = pd.to_datetime(sent_df["timestamp"], utc=True)
        velocity_60m = get_latest_velocity(sent_df, window_minutes=60)

    # --- Divergence (discussion volume vs delivery volume, daily alignment) ---
    divergence_val = 0.0
    divergence_dir = "neutral"

    if market_rows:
        # Aggregate discussion volume per day (Python-side)
        disc_daily = defaultdict(int)
        for hour_key, vals in hourly_counts.items():
            day_key = hour_key.date()
            disc_daily[day_key] += vals["count"]

        # Aggregate delivery volume per day (Python-side)
        deliv_daily = defaultdict(int)
        for r in market_rows:
            if r.delivery_volume:
                deliv_daily[r.date.date()] += r.delivery_volume

        # Find overlapping days
        common_days = sorted(set(disc_daily.keys()) & set(deliv_daily.keys()))

        if len(common_days) >= 2:
            disc_series = pd.Series(
                [disc_daily[d] for d in common_days],
                index=pd.DatetimeIndex(common_days),
            )
            deliv_series = pd.Series(
                [deliv_daily[d] for d in common_days],
                index=pd.DatetimeIndex(common_days),
            )
            div_series = compute_divergence(disc_series, deliv_series)
            divergence_val = float(div_series.iloc[-1])
            divergence_dir = classify_divergence(divergence_val)

    # --- Confidence ---
    recent_labels = [r.label for r in sent_rows]

    avg_model_certainty = min(avg_score, 1.0)
    data_suff = estimate_data_sufficiency(total_count)
    sig_consist = estimate_signal_consistency(recent_labels)
    confidence = compute_confidence(avg_model_certainty, data_suff, sig_consist)

    return DivergenceSignal(
        symbol=symbol,
        timestamp=now,
        sentiment_score_avg=round(avg_score, 4),
        discussion_volume=total_count,
        sentiment_velocity=round(velocity_60m, 2),
        velocity_window_minutes=60,
        divergence_score=round(divergence_val, 4),
        divergence_direction=divergence_dir,
        confidence_score=confidence,
        model_certainty=round(avg_model_certainty, 4),
        data_sufficiency=round(data_suff, 4),
        signal_consistency=round(sig_consist, 4),
        computed_at=now,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _store_posts(posts: list[dict]):
    """Store ingested posts in the database, skipping duplicates."""
    if not posts:
        return

    # Deduplicate within the batch by source_id
    seen = set()
    unique_posts = []
    for p in posts:
        sid = p.get("source_id")
        if sid and sid in seen:
            continue
        if sid:
            seen.add(sid)
        unique_posts.append(p)

    db = SessionLocal()
    stored = 0
    skipped = 0
    try:
        for post_data in unique_posts:
            source_id = post_data.get("source_id")
            if source_id:
                existing = (
                    db.query(SocialPost.id)
                    .filter(SocialPost.source_id == source_id)
                    .first()
                )
                if existing:
                    skipped += 1
                    continue
            post_data["data_source"] = "live"
            try:
                db.add(SocialPost(**post_data))
                db.flush()
                stored += 1
            except Exception:
                db.rollback()
                skipped += 1
        db.commit()
        logger.info(f"Stored {stored} new posts (skipped {skipped} duplicates, {len(posts) - len(unique_posts)} batch dupes)")
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing posts: {e}")
    finally:
        db.close()
