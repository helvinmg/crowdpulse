"""API routes for pipeline execution with SSE progress streaming."""

import asyncio
import json
import math
import random
import time
from datetime import datetime, timedelta
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from loguru import logger

from app.core.database import SessionLocal
from app.core.constants import NIFTY_50_SYMBOLS

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


def _sse_event(step: str, progress: int, message: str, done: bool = False):
    """Format a Server-Sent Event."""
    data = json.dumps({
        "step": step,
        "progress": progress,
        "message": message,
        "done": done,
        "timestamp": datetime.utcnow().isoformat(),
    })
    return f"data: {data}\n\n"


# Realistic delays for test pipeline (logged-in user, live mode OFF)
_TEST_STEP_DELAY = 4.0       # seconds before each scraping step
_TEST_PER_ITEM_DELAY = 0.12  # seconds per item (simulates API/network)
_TEST_STEP_TAIL = 1.5        # seconds after each step message


async def _run_test_pipeline(since, until):
    """Fake pipeline run for test mode — fewer records, realistic delays (slower run)."""
    from app.models.social_post import SocialPost
    from app.models.sentiment_record import SentimentRecord
    from app.models.market_data import MarketData
    from app.models.divergence_signal import DivergenceSignal
    from app.seed import (
        SAMPLE_COMMENTS, _symbol_profile, _LABEL_SCORE_RANGE,
        NIFTY_50_SYMBOLS as SYMBOLS,
    )

    db = SessionLocal()
    now = datetime.utcnow()
    time_span_hours = max(1, (until - since).total_seconds() / 3600)

    try:
        # Step 1: Scraping Telegram (fewer symbols, fewer posts, with per-item delay)
        yield _sse_event("telegram", 8, "Scraping Telegram channels...")
        await asyncio.sleep(_TEST_STEP_DELAY)
        telegram_count = 0
        for symbol in SYMBOLS[:6]:
            profile = _symbol_profile(symbol)
            for i in range(random.randint(1, 4)):
                await asyncio.sleep(_TEST_PER_ITEM_DELAY)
                r = random.random()
                cat = "positive" if r < profile[0] else ("negative" if r < profile[0] + profile[1] else "neutral")
                comment = f"{symbol} - {random.choice(SAMPLE_COMMENTS[cat])}"
                minutes_ago = random.uniform(0, time_span_hours * 60)
                posted_at = max(since, min(until, now - timedelta(minutes=minutes_ago)))
                post = SocialPost(
                    source="telegram", symbol=symbol, raw_text=comment,
                    cleaned_text=comment, author=f"tg_user_{random.randint(1,100)}",
                    source_id=f"test_tg_{symbol}_{posted_at.timestamp()}_{i}",
                    posted_at=posted_at,
                    ingested_at=posted_at, data_source="test",
                )
                db.add(post)
                telegram_count += 1
        db.flush()
        yield _sse_event("telegram", 18, f"Telegram: {telegram_count} messages scraped")
        await asyncio.sleep(_TEST_STEP_TAIL)

        # Step 2: Scraping YouTube
        yield _sse_event("youtube", 25, "Scraping YouTube comments...")
        await asyncio.sleep(_TEST_STEP_DELAY)
        youtube_count = 0
        for symbol in SYMBOLS[:5]:
            profile = _symbol_profile(symbol)
            for i in range(random.randint(2, 6)):
                await asyncio.sleep(_TEST_PER_ITEM_DELAY)
                r = random.random()
                cat = "positive" if r < profile[0] else ("negative" if r < profile[0] + profile[1] else "neutral")
                comment = f"{symbol} - {random.choice(SAMPLE_COMMENTS[cat])}"
                minutes_ago = random.uniform(0, time_span_hours * 60)
                posted_at = max(since, min(until, now - timedelta(minutes=minutes_ago)))
                post = SocialPost(
                    source="youtube", symbol=symbol, raw_text=comment,
                    cleaned_text=comment, author=f"yt_user_{random.randint(1,100)}",
                    source_id=f"test_yt_{symbol}_{posted_at.timestamp()}_{i}",
                    posted_at=posted_at,
                    ingested_at=posted_at, data_source="test",
                )
                db.add(post)
                youtube_count += 1
        db.flush()
        yield _sse_event("youtube", 35, f"YouTube: {youtube_count} comments scraped")
        await asyncio.sleep(_TEST_STEP_TAIL)

        # Step 3: Scraping Twitter
        yield _sse_event("twitter", 42, "Scraping Twitter/X posts...")
        await asyncio.sleep(_TEST_STEP_DELAY)
        twitter_count = 0
        for symbol in SYMBOLS[:4]:
            profile = _symbol_profile(symbol)
            for i in range(random.randint(1, 4)):
                await asyncio.sleep(_TEST_PER_ITEM_DELAY)
                r = random.random()
                cat = "positive" if r < profile[0] else ("negative" if r < profile[0] + profile[1] else "neutral")
                comment = f"{symbol} - {random.choice(SAMPLE_COMMENTS[cat])}"
                minutes_ago = random.uniform(0, time_span_hours * 60)
                posted_at = max(since, min(until, now - timedelta(minutes=minutes_ago)))
                post = SocialPost(
                    source="twitter", symbol=symbol, raw_text=comment,
                    cleaned_text=comment, author=f"tw_user_{random.randint(1,100)}",
                    source_id=f"test_tw_{symbol}_{posted_at.timestamp()}_{i}",
                    posted_at=posted_at,
                    ingested_at=posted_at, data_source="test",
                )
                db.add(post)
                twitter_count += 1
        db.flush()
        yield _sse_event("twitter", 50, f"Twitter: {twitter_count} tweets scraped")
        await asyncio.sleep(_TEST_STEP_TAIL)

        # Step 3b: Scraping Reddit
        yield _sse_event("reddit", 55, "Scraping Reddit posts...")
        await asyncio.sleep(_TEST_STEP_DELAY)
        reddit_count = 0
        for symbol in SYMBOLS[:4]:
            profile = _symbol_profile(symbol)
            for i in range(random.randint(1, 4)):
                await asyncio.sleep(_TEST_PER_ITEM_DELAY)
                r = random.random()
                cat = "positive" if r < profile[0] else ("negative" if r < profile[0] + profile[1] else "neutral")
                comment = f"{symbol} - {random.choice(SAMPLE_COMMENTS[cat])}"
                minutes_ago = random.uniform(0, time_span_hours * 60)
                posted_at = max(since, min(until, now - timedelta(minutes=minutes_ago)))
                post = SocialPost(
                    source="reddit", symbol=symbol, raw_text=comment,
                    cleaned_text=comment, author=f"rd_user_{random.randint(1,100)}",
                    source_id=f"test_rd_{symbol}_{posted_at.timestamp()}_{i}",
                    posted_at=posted_at,
                    ingested_at=posted_at, data_source="test",
                )
                db.add(post)
                reddit_count += 1
        db.flush()
        yield _sse_event("reddit", 62, f"Reddit: {reddit_count} posts scraped")
        await asyncio.sleep(_TEST_STEP_TAIL)

        # Step 4: Fetching market data
        yield _sse_event("market", 68, "Fetching market data...")
        await asyncio.sleep(_TEST_STEP_DELAY)
        for symbol in SYMBOLS:
            base = random.uniform(200, 3000)
            chg = random.uniform(-0.03, 0.03)
            o = round(base * (1 + random.uniform(-0.01, 0.01)), 2)
            c = round(base * (1 + chg), 2)
            h = round(max(o, c) * 1.01, 2)
            lo = round(min(o, c) * 0.99, 2)
            vol = random.randint(500_000, 20_000_000)
            dpct = round(random.uniform(35, 65), 2)
            dvol = int(vol * dpct / 100)
            record = MarketData(
                symbol=symbol, date=now.replace(hour=15, minute=30, second=0, microsecond=0),
                open=o, high=h, low=lo, close=c,
                volume=vol, delivery_volume=dvol, delivery_pct=dpct,
                data_source="test",
            )
            db.merge(record)
            await asyncio.sleep(0.04)  # slight delay per symbol
        db.flush()
        yield _sse_event("market", 75, f"Market data: {len(SYMBOLS)} stocks updated")
        await asyncio.sleep(_TEST_STEP_TAIL)

        # Step 5: Scoring sentiment (per-post delay to simulate NLP)
        yield _sse_event("scoring", 78, "Running sentiment analysis (FinBERT)...")
        await asyncio.sleep(_TEST_STEP_DELAY)
        scored_ids_sub = db.query(SentimentRecord.post_id).subquery()
        unscored = (
            db.query(SocialPost)
            .filter(SocialPost.id.notin_(scored_ids_sub))
            .all()
        )
        scored_count = 0
        pos_kw = ["rocket", "buy", "bullish", "strong", "bright", "gem", "moon",
                   "breakout", "multibagger", "opportunity", "amazing", "king",
                   "accumulate", "gold mine", "party", "zabardast", "mast"]
        neg_kw = ["trap", "crash", "sell", "scam", "loss", "dead", "avoid",
                   "doobega", "barbaad", "risky", "danger", "overvalued",
                   "bubble", "dump", "exit", "stop loss", "red"]
        for post in unscored:
            await asyncio.sleep(_TEST_PER_ITEM_DELAY)
            text_lower = post.raw_text.lower()
            ph = sum(1 for kw in pos_kw if kw in text_lower)
            nh = sum(1 for kw in neg_kw if kw in text_lower)
            label = "positive" if ph > nh else ("negative" if nh > ph else "neutral")
            lo_s, hi_s = _LABEL_SCORE_RANGE[label]
            score = round(random.uniform(lo_s, hi_s), 6)
            scored_at = post.posted_at + timedelta(minutes=random.randint(1, 30)) if post.posted_at else now
            db.add(SentimentRecord(
                post_id=post.id, symbol=post.symbol, label=label,
                score=score, model_version="finbert-seed", scored_at=scored_at,
                data_source="test",
            ))
            scored_count += 1
        db.flush()
        yield _sse_event("scoring", 88, f"Scored {scored_count} posts")
        await asyncio.sleep(_TEST_STEP_TAIL)

        # Step 6: Computing signals
        yield _sse_event("signals", 92, "Computing divergence & confidence signals...")
        await asyncio.sleep(_TEST_STEP_DELAY)
        signals_count = 0
        for symbol in SYMBOLS:
            await asyncio.sleep(0.06)
            profile = _symbol_profile(symbol)
            base_div = (profile[0] - profile[1]) * 3.0
            noise = random.gauss(0, 0.6)
            div_score = round(base_div + noise, 3)
            direction = "hype" if div_score > 1.5 else ("panic" if div_score < -1.5 else "neutral")
            velocity = round(max(0, min(100, 50 + div_score * 12 + random.gauss(0, 8))), 2)
            mc = round(random.uniform(0.65, 0.95), 4)
            ds = round(random.uniform(0.25, 0.70), 4)
            sc = round(random.uniform(0.50, 0.95), 4)
            conf = round(0.4 * mc + 0.3 * ds + 0.3 * sc, 4)
            avg_sent = round(max(0.1, min(0.99, 0.5 + div_score * 0.1 + random.gauss(0, 0.05))), 4)

            db.add(DivergenceSignal(
                symbol=symbol, timestamp=now,
                sentiment_score_avg=avg_sent, discussion_volume=random.randint(15, 80),
                sentiment_velocity=velocity, velocity_window_minutes=60,
                divergence_score=div_score, divergence_direction=direction,
                confidence_score=conf, model_certainty=mc,
                data_sufficiency=ds, signal_consistency=sc, computed_at=now,
                data_source="test",
            ))
            signals_count += 1
        db.commit()
        yield _sse_event("signals", 98, f"Computed {signals_count} signals")
        await asyncio.sleep(_TEST_STEP_TAIL)

        total = telegram_count + youtube_count + twitter_count + reddit_count
        yield _sse_event("done", 100,
            f"Pipeline complete! {total} posts scraped, {scored_count} scored, {signals_count} signals",
            done=True)

    except Exception as e:
        db.rollback()
        logger.error(f"Test pipeline error: {e}")
        yield _sse_event("error", 0, f"Pipeline failed: {str(e)}", done=True)
    finally:
        db.close()


async def _run_live_pipeline(user_id: int | None = None):
    """Real pipeline run — calls actual scrapers."""
    yield _sse_event("start", 5, "Starting live pipeline...")
    await asyncio.sleep(0.5)

    # Load global config + user config once
    from app.core.config import get_settings as _get_settings
    _settings = _get_settings()

    user_config = None
    if user_id:
        from app.models.user_config import UserConfig
        db_cfg = SessionLocal()
        try:
            user_config = db_cfg.query(UserConfig).filter(UserConfig.user_id == user_id).first()
        finally:
            db_cfg.close()

    def _get_credential(env_key: str, user_field: str | None = None) -> str | None:
        """Get credential: prioritize user's own, fallback to .env global."""
        # Check user's own credential first
        if user_config and user_field:
            user_val = getattr(user_config, user_field, None)
            if user_val:
                return user_val
        # Fallback to .env global
        return getattr(_settings, env_key, None) or None

    def _is_source_configured(env_keys: list[str], user_fields: list[str] | None = None) -> bool:
        """Check if source is configured: user credentials OR .env globals."""
        # Check user-provided credentials first
        if user_config and user_fields:
            if all(getattr(user_config, f, None) for f in user_fields):
                return True
        # Fallback to .env globals
        return all(getattr(_settings, k, None) for k in env_keys)

    try:
        # Ingestion
        yield _sse_event("telegram", 10, "Scraping Telegram channels (live)...")
        try:
            if not _is_source_configured(['TELEGRAM_API_ID'], ['telegram_session_data']):
                yield _sse_event("telegram", 25, "Telegram skipped (not configured)")
            else:
                from app.ingestion.telegram_scraper import scrape_all_channels
                from app.core.user_sources import get_telegram_channels, get_telegram_session
                from app.workers.tasks import _store_posts
                channels = get_telegram_channels(user_id)
                session_string = get_telegram_session(user_id)
                messages = await scrape_all_channels(channels=channels, session_string=session_string)
                _store_posts(messages)
                yield _sse_event("telegram", 25, f"Telegram: {len(messages)} messages scraped")
        except Exception as e:
            yield _sse_event("telegram", 25, f"Telegram failed: {str(e)[:80]}")

        yield _sse_event("youtube", 30, "Scraping YouTube comments (live)...")
        try:
            from app.workers.tasks import ingest_youtube
            ingest_youtube(user_id)
            yield _sse_event("youtube", 45, "YouTube scraping complete")
        except Exception as e:
            yield _sse_event("youtube", 45, f"YouTube failed: {str(e)[:80]}")

        yield _sse_event("twitter", 45, "Scraping Twitter/X (live)...")
        try:
            # Check for user's own bearer token OR global .env token
            if not _is_source_configured(['TWITTER_BEARER_TOKEN'], ['twitter_bearer_token']):
                yield _sse_event("twitter", 50, "Twitter/X skipped (bearer token not set)")
            else:
                from app.workers.tasks import ingest_twitter
                ingest_twitter(user_id)
                yield _sse_event("twitter", 50, "Twitter scraping complete")
        except Exception as e:
            yield _sse_event("twitter", 50, f"Twitter failed: {str(e)[:80]}")

        yield _sse_event("reddit", 52, "Scraping Reddit (live)...")
        try:
            # Check for user's own credentials OR global .env credentials
            if not _is_source_configured(['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET'], ['reddit_client_id', 'reddit_client_secret']):
                yield _sse_event("reddit", 62, "Reddit skipped (API credentials not set)")
            else:
                from app.workers.tasks import ingest_reddit
                ingest_reddit(user_id)
                yield _sse_event("reddit", 62, "Reddit scraping complete")
        except Exception as e:
            yield _sse_event("reddit", 62, f"Reddit failed: {str(e)[:80]}")

        yield _sse_event("market", 65, "Fetching market data (live)...")
        try:
            from app.workers.tasks import fetch_market_data
            fetch_market_data()
            yield _sse_event("market", 75, "Market data updated")
        except Exception as e:
            yield _sse_event("market", 75, f"Market data failed: {str(e)[:80]}")

        # Scoring
        yield _sse_event("scoring", 80, "Running sentiment scoring (hybrid)...")
        try:
            from app.workers.tasks import score_sentiment
            score_sentiment()
            yield _sse_event("scoring", 90, "Sentiment scoring complete")
        except Exception as e:
            yield _sse_event("scoring", 90, f"Scoring failed: {str(e)[:80]}")

        # Signals
        yield _sse_event("signals", 92, "Computing divergence signals...")
        try:
            from app.workers.tasks import compute_all_signals
            compute_all_signals()
            yield _sse_event("signals", 98, "Signal computation complete")
        except Exception as e:
            yield _sse_event("signals", 98, f"Signals failed: {str(e)[:80]}")

        yield _sse_event("done", 100, "Live pipeline complete!", done=True)

    except Exception as e:
        logger.error(f"Live pipeline error: {e}")
        yield _sse_event("error", 0, f"Pipeline failed: {str(e)}", done=True)


@router.post("/run")
async def run_pipeline(
    hours: int = 24,
    start: str = None,
    end: str = None,
    request: Request = None,
):
    """Run the full pipeline with SSE progress updates."""
    from datetime import datetime, timedelta
    from app.main import _data_mode

    # Try to identify the logged-in user from Authorization header
    user_id = None
    if request:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                from app.core.auth import decode_token
                payload = decode_token(auth_header.split(" ")[1])
                user_id = payload.get("sub") or payload.get("user_id")
                if user_id:
                    user_id = int(user_id)
            except Exception:
                pass

    # Parse date range
    if start:
        since = datetime.fromisoformat(start)
    else:
        since = datetime.utcnow() - timedelta(hours=hours)
    until = datetime.fromisoformat(end) if end else datetime.utcnow()

    if _data_mode == "test":
        generator = _run_test_pipeline(since, until)
    else:
        generator = _run_live_pipeline(user_id=user_id)

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
