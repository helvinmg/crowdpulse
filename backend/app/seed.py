"""Seed sample data for testing the Crowd Pulse pipeline without live APIs.

Creates realistic Hinglish social posts, market data, pre-scored sentiment
records, and divergence signals for all Nifty 50 symbols over 7 days.
"""

import math
import random
from datetime import datetime, timedelta
from loguru import logger

from app.core.database import SessionLocal
from app.core.constants import NIFTY_50_SYMBOLS
from app.models.social_post import SocialPost
from app.models.sentiment_record import SentimentRecord
from app.models.market_data import MarketData
from app.models.divergence_signal import DivergenceSignal

# ---------------------------------------------------------------------------
# Sample Hinglish comments (positive, negative, neutral)
# ---------------------------------------------------------------------------
SAMPLE_COMMENTS = {
    "positive": [
        "Rocket jaayega bhai 🚀🚀🚀",
        "Results dekhe? Bohot mast hai, buy karo",
        "Future bright hai, long term hold karo 💰",
        "Entry le lo, breakout aane wala hai",
        "Strong hai, government backing hai 🔥",
        "EV story zabardast hai, moon confirmed 🌙",
        "Chart dekho, bullish pattern ban raha hai",
        "Finally move kar raha hai, multibagger banega",
        "Accha opportunity hai dip pe",
        "Solid fundamentals, buy on dips 💪",
        "Sales figures amazing aaye hai",
        "Brand value kya hai, long term gem 💎",
        "Undervalued hai, accumulate karo",
        "Sector ka king hai",
        "Infrastructure boom se faayda hoga 📈",
        "Bhai ye stock toh gold mine hai 🏆",
        "Sab log bol rahe hai buy karo, mein bhi le raha 💵",
        "Isko hold karo, 2x hoga 6 months mein",
        "FII buying badh rahi hai, bullish signal 📊",
        "Quarterly results zabardast aaye, party time 🎉",
    ],
    "negative": [
        "Door raho, trap hai bhai 💀",
        "Mat faso, cycle down hai",
        "PAYTM jaisa haal hoga, sab doobega 📉",
        "Ye pump and dump hai, mat lo please",
        "Overvalued hai, correction aayega",
        "Market crash hone wala hai, sab sell karo 😭",
        "Loss ho raha hai, exit karo",
        "Ye stock scam hai, operator chal raha hai",
        "Koi future nahi hai isme",
        "Government stock hai, kabhi nahi badhega",
        "Dead stock hai, paisa barbaad",
        "Bubble ban raha hai 💀💀",
        "Risky hai, NPA badh rahe hai",
        "Ye finfluencer sab milke trap kar rahe hai",
        "Volume nahi hai, avoid karo",
        "Stop loss hit ho gaya, bohot bura 😤",
        "Sab red hai aaj, portfolio barbaad",
        "Management pe trust nahi hai",
        "Debt bohot zyada hai, risky play",
        "Promoter pledge badh raha hai, danger signal ⚠️",
    ],
    "neutral": [
        "Result kab aa raha hai?",
        "Kya lagta hai aaj market green ya red?",
        "PE ratio kitna hai abhi?",
        "Koi news aaya kya?",
        "Aaj flat band mein hai",
        "Dividend kab milega?",
        "Market timing kya hai aaj?",
        "Quarterly results kab hai?",
        "Koi analysis share karo",
        "Konsa better hai comparison mein?",
        "Delivery volume check karo pehle",
        "FII data kya bol raha hai aaj?",
        "RBI policy ka impact kya hoga?",
        "Budget mein kya announcements honge?",
        "SEBI ka naya circular padha kya?",
        "Koi target price batao",
        "Support level kya hai?",
        "Resistance kahan hai chart pe?",
        "Sector rotation ho raha hai kya?",
        "Open interest data check karo",
    ],
}

# Sentiment profiles: some stocks trend bullish, some bearish, some mixed
# (pos_weight, neg_weight, neu_weight)
_PROFILES = {
    "bullish":  (0.55, 0.20, 0.25),
    "bearish":  (0.15, 0.55, 0.30),
    "mixed":    (0.35, 0.35, 0.30),
    "neutral":  (0.25, 0.25, 0.50),
}

# Assign each symbol a profile for variety
def _symbol_profile(symbol):
    h = hash(symbol) % 4
    return list(_PROFILES.values())[h]

# Confidence score for a label
_LABEL_SCORE_RANGE = {
    "positive": (0.60, 0.98),
    "negative": (0.55, 0.95),
    "neutral":  (0.50, 0.90),
}

NUM_DAYS = 7
POSTS_PER_SYMBOL_PER_DAY = 40  # ~40 posts/symbol/day → ~14,000 total


def seed_sample_data(
    num_days: int = NUM_DAYS,
    posts_per_symbol_per_day: int = POSTS_PER_SYMBOL_PER_DAY,
):
    """Seed the database with 7 days of data for all Nifty 50 symbols."""
    db = SessionLocal()
    try:
        # Clear old seed data
        _clear_seed_data(db)
        db.commit()

        posts_created = _seed_social_posts(db, num_days, posts_per_symbol_per_day)
        market_created = _seed_market_data(db, num_days)
        sentiment_created = _seed_sentiment_records(db)
        signals_created = _seed_divergence_signals(db, num_days)
        db.commit()

        logger.info(
            f"Seed complete: {posts_created} posts, {sentiment_created} sentiment, "
            f"{market_created} market, {signals_created} signals"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Seed failed: {e}")
        raise
    finally:
        db.close()


def _clear_seed_data(db):
    """Remove only test data, leave live data intact."""
    db.query(DivergenceSignal).filter(DivergenceSignal.data_source == "test").delete()
    db.query(SentimentRecord).filter(SentimentRecord.data_source == "test").delete()
    db.query(MarketData).filter(MarketData.data_source == "test").delete()
    db.query(SocialPost).filter(SocialPost.data_source == "test").delete()
    logger.info("Cleared existing test data")


def _seed_social_posts(db, num_days: int, per_symbol_per_day: int) -> int:
    """Create Hinglish social posts spread over num_days for all symbols."""
    now = datetime.utcnow()
    sources = ["telegram", "youtube", "twitter"]
    created = 0

    for symbol in NIFTY_50_SYMBOLS:
        profile = _symbol_profile(symbol)
        for day in range(num_days):
            day_start = now - timedelta(days=day + 1)
            for i in range(per_symbol_per_day):
                # Pick sentiment category based on profile
                r = random.random()
                if r < profile[0]:
                    category = "positive"
                elif r < profile[0] + profile[1]:
                    category = "negative"
                else:
                    category = "neutral"

                comment = random.choice(SAMPLE_COMMENTS[category])
                source = random.choice(sources)

                # Inject symbol mention
                if random.random() < 0.6:
                    comment = f"{symbol} - {comment}"

                # Spread within the day (market hours 9:15-15:30 IST ≈ 3:45-10:00 UTC)
                hour_offset = random.uniform(0, 24)
                posted_at = day_start + timedelta(hours=hour_offset)

                source_id = f"seed_{source}_{symbol}_{day}_{i}"

                post = SocialPost(
                    source=source,
                    symbol=symbol,
                    raw_text=comment,
                    cleaned_text=comment,
                    author=f"seed_user_{random.randint(1, 200)}",
                    source_id=source_id,
                    posted_at=posted_at,
                    ingested_at=posted_at + timedelta(minutes=random.randint(1, 30)),
                    data_source="test",
                )
                db.add(post)
                created += 1

        # Flush every symbol to avoid huge memory
        if created % 2000 == 0:
            db.flush()

    db.flush()
    logger.info(f"Seeded {created} social posts for {len(NIFTY_50_SYMBOLS)} symbols")
    return created


def _seed_market_data(db, num_days: int) -> int:
    """Create market data for all Nifty 50 symbols over num_days."""
    now = datetime.utcnow()
    created = 0

    for symbol in NIFTY_50_SYMBOLS:
        base_price = random.uniform(200, 3000)

        for day_offset in range(num_days):
            date = (now - timedelta(days=day_offset)).replace(
                hour=15, minute=30, second=0, microsecond=0
            )

            change_pct = random.uniform(-0.04, 0.04)
            open_price = base_price * (1 + random.uniform(-0.015, 0.015))
            close_price = base_price * (1 + change_pct)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.02))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.02))
            volume = random.randint(500_000, 25_000_000)

            intraday_range = (high_price - low_price) / close_price if close_price else 0
            delivery_pct = max(0.30, min(0.70, 0.55 - intraday_range * 5.0))
            delivery_volume = int(volume * delivery_pct)

            record = MarketData(
                symbol=symbol,
                date=date,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=volume,
                delivery_volume=delivery_volume,
                delivery_pct=round(delivery_pct * 100, 2),
                data_source="test",
            )
            db.merge(record)
            created += 1
            base_price = close_price

    db.flush()
    logger.info(f"Seeded {created} market data records for {len(NIFTY_50_SYMBOLS)} symbols")
    return created


def _seed_sentiment_records(db) -> int:
    """Create pre-scored sentiment records for every social post."""
    posts = db.query(SocialPost).all()
    created = 0

    for post in posts:
        # Determine label from the comment content heuristic
        text_lower = post.raw_text.lower()
        # Simple heuristic: check for known positive/negative keywords
        pos_kw = ["rocket", "buy", "bullish", "strong", "bright", "gem", "moon",
                   "breakout", "multibagger", "opportunity", "amazing", "king",
                   "accumulate", "gold mine", "party", "zabardast", "mast"]
        neg_kw = ["trap", "crash", "sell", "scam", "loss", "dead", "avoid",
                   "doobega", "barbaad", "risky", "danger", "overvalued",
                   "bubble", "dump", "exit", "stop loss", "red"]

        pos_hits = sum(1 for kw in pos_kw if kw in text_lower)
        neg_hits = sum(1 for kw in neg_kw if kw in text_lower)

        if pos_hits > neg_hits:
            label = "positive"
        elif neg_hits > pos_hits:
            label = "negative"
        else:
            label = "neutral"

        lo, hi = _LABEL_SCORE_RANGE[label]
        score = round(random.uniform(lo, hi), 6)

        # scored_at slightly after posted_at
        scored_at = post.posted_at + timedelta(minutes=random.randint(5, 60)) if post.posted_at else post.ingested_at

        record = SentimentRecord(
            post_id=post.id,
            symbol=post.symbol,
            label=label,
            score=score,
            model_version="finbert-seed",
            scored_at=scored_at,
            data_source="test",
        )
        db.add(record)
        created += 1

        if created % 2000 == 0:
            db.flush()

    db.flush()
    logger.info(f"Seeded {created} sentiment records")
    return created


def _seed_divergence_signals(db, num_days: int) -> int:
    """Create divergence signals every 4 hours for each symbol over num_days."""
    now = datetime.utcnow()
    created = 0

    for symbol in NIFTY_50_SYMBOLS:
        profile = _symbol_profile(symbol)
        # Base divergence tendency from profile
        # bullish → positive divergence (hype), bearish → negative (panic)
        base_div = (profile[0] - profile[1]) * 3.0  # range roughly -1.65 to +1.65

        for day in range(num_days):
            # 6 signals per day (every 4 hours)
            for hour_slot in range(6):
                ts = now - timedelta(days=day, hours=hour_slot * 4)

                # Add daily drift + noise
                day_drift = math.sin(day * 0.9 + hash(symbol) % 7) * 0.8
                noise = random.gauss(0, 0.5)
                div_score = round(base_div + day_drift + noise, 3)

                # Classify
                if div_score > 1.5:
                    direction = "hype"
                elif div_score < -1.5:
                    direction = "panic"
                else:
                    direction = "neutral"

                # Velocity: 50 = baseline, varies with sentiment
                velocity = round(50 + div_score * 12 + random.gauss(0, 8), 2)
                velocity = max(0, min(100, velocity))

                # Discussion volume
                disc_vol = random.randint(15, 80)

                # Confidence components
                model_cert = round(random.uniform(0.65, 0.95), 4)
                data_suff = round(random.uniform(0.25, 0.70), 4)
                sig_consist = round(random.uniform(0.50, 0.95), 4)
                confidence = round(
                    0.4 * model_cert + 0.3 * data_suff + 0.3 * sig_consist, 4
                )

                # Avg sentiment score
                avg_sent = round(0.5 + div_score * 0.1 + random.gauss(0, 0.05), 4)
                avg_sent = max(0.1, min(0.99, avg_sent))

                signal = DivergenceSignal(
                    symbol=symbol,
                    timestamp=ts,
                    sentiment_score_avg=avg_sent,
                    discussion_volume=disc_vol,
                    sentiment_velocity=velocity,
                    velocity_window_minutes=60,
                    divergence_score=div_score,
                    divergence_direction=direction,
                    confidence_score=confidence,
                    model_certainty=model_cert,
                    data_sufficiency=data_suff,
                    signal_consistency=sig_consist,
                    computed_at=ts,
                    data_source="test",
                )
                db.add(signal)
                created += 1

        if created % 500 == 0:
            db.flush()

    db.flush()
    logger.info(f"Seeded {created} divergence signals for {len(NIFTY_50_SYMBOLS)} symbols")
    return created
