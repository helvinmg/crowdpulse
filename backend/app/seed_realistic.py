"""Realistic seed data for test mode with natural sentiment patterns.

Creates more natural sentiment fluctuations that mimic real market behavior
with momentum, mean reversion, and news-driven sentiment spikes.
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
# Enhanced Hinglish comments with more variety and context
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
        "Technical indicators sab green hai",
        "Promoter share increase kiya, confidence boost",
        "New product launch hoga, demand badhegi",
        "Margin improvement dekh raha hun",
        "Order book strong hai, backlog full",
        "Management commentary positive tha",
        "Analyst upgrade aaya, target badhaya",
        "PE ratio reasonable hai sector comparison mein",
        "Dividend yield accha hai, income stock",
        "Debt reduced hai, balance sheet strong",
        "Capex efficiency improve ho rahi hai",
        "Market share gain kar raha hai",
        "R&D investment dekh raha hun, innovation strong",
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
        "Quarterly results disappointing the",
        "Margin pressure dekh raha hun",
        "Competition badh rahi hai, market share lose",
        "Regulatory issues aaye, uncertainty",
        "Working capital tight hai",
        "Inventory pile up ho rahi hai",
        "Cash flow negative hai",
        "EBITDA margin girta ja raha hai",
        "Customer complaints badh rahe hain",
        "Employee turnover high hai",
        "Legal issues pending hain",
        "Tax notice aaya hai",
        "Auditor qualification hai",
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
        "Promoter holding kitni hai?",
        "Mutual fund exposure kya hai?",
        "Technical indicators kya keh rahe hain?",
        "Global cues kya hain?",
        "Crude oil prices ka impact?",
        "Dollar index movement kya hai?",
        "Bond yields kya signal de rahe hain?",
        "Monsoon forecast kya hai?",
        "GDP growth numbers kya hain?",
        "Inflation data kya bol raha hai?",
        "Manufacturing PMI kya aaya?",
        "Service sector performance kaisi hai?",
        "Auto sales numbers dekhe?",
        "Bank credit growth kya hai?",
        "Retail investor sentiment kya hai?",
        "Foreign portfolio flows kya hain?",
    ],
}

# More sophisticated sentiment profiles with market dynamics
_SENTIMENT_PROFILES = {
    "growth_tech": {  # High growth tech stocks
        "base_sentiment": 0.65,
        "volatility": 0.25,
        "momentum_factor": 0.8,
        "news_sensitivity": 0.9,
        "mean_reversion": 0.3,
    },
    "stable_bluechip": {  # Large stable companies
        "base_sentiment": 0.55,
        "volatility": 0.15,
        "momentum_factor": 0.4,
        "news_sensitivity": 0.5,
        "mean_reversion": 0.7,
    },
    "cyclical": {  # Cyclical stocks
        "base_sentiment": 0.45,
        "volatility": 0.35,
        "momentum_factor": 0.6,
        "news_sensitivity": 0.7,
        "mean_reversion": 0.5,
    },
    "defensive": {  # Defensive stocks
        "base_sentiment": 0.60,
        "volatility": 0.20,
        "momentum_factor": 0.3,
        "news_sensitivity": 0.4,
        "mean_reversion": 0.8,
    },
    "high_beta": {  # High volatility stocks
        "base_sentiment": 0.40,
        "volatility": 0.45,
        "momentum_factor": 0.9,
        "news_sensitivity": 1.0,
        "mean_reversion": 0.4,
    },
}

def _get_symbol_profile(symbol):
    """Assign a sentiment profile based on symbol characteristics."""
    # This is a simplified assignment - in reality, you'd have a proper mapping
    hash_val = hash(symbol) % 5
    profiles = list(_SENTIMENT_PROFILES.keys())
    return _SENTIMENT_PROFILES[profiles[hash_val]]

def _generate_sentiment_time_series(symbol, num_hours, profile):
    """Generate realistic sentiment time series with market dynamics."""
    sentiments = []
    current_sentiment = profile["base_sentiment"]
    
    for hour in range(num_hours):
        # Add momentum effect
        momentum = 0
        if len(sentiments) > 0:
            momentum = (sentiments[-1] - profile["base_sentiment"]) * profile["momentum_factor"]
        
        # Add mean reversion
        mean_reversion = (profile["base_sentiment"] - current_sentiment) * profile["mean_reversion"]
        
        # Add random walk with volatility
        random_walk = random.gauss(0, profile["volatility"])
        
        # Add news events (occasional spikes)
        news_event = 0
        if random.random() < 0.05:  # 5% chance of news event
            news_event = random.choice([-0.3, 0.3]) * profile["news_sensitivity"]
        
        # Add intraday pattern (market hours effect)
        hour_of_day = hour % 24
        intraday_effect = 0
        if 9 <= hour_of_day <= 15:  # Market hours
            intraday_effect = math.sin((hour_of_day - 9) * math.pi / 6) * 0.1
        
        # Calculate new sentiment
        new_sentiment = current_sentiment + momentum + mean_reversion + random_walk + news_event + intraday_effect
        
        # Clamp to valid range
        new_sentiment = max(0.1, min(0.9, new_sentiment))
        
        sentiments.append(new_sentiment)
        current_sentiment = new_sentiment
    
    return sentiments

def _sentiment_to_label(score):
    """Convert sentiment score to label with realistic distribution."""
    if score > 0.65:
        return "positive"
    elif score < 0.45:
        return "negative"
    else:
        return "neutral"

def _confidence_score(label, sentiment_score):
    """Generate realistic confidence scores."""
    base_confidence = {
        "positive": (0.70, 0.95),
        "negative": (0.65, 0.90),
        "neutral": (0.60, 0.85),
    }
    
    lo, hi = base_confidence[label]
    # Higher confidence for extreme sentiments
    if abs(sentiment_score - 0.5) > 0.3:
        lo += 0.05
        hi += 0.05
    
    return round(random.uniform(lo, hi), 6)

NUM_DAYS = 7
POSTS_PER_SYMBOL_PER_DAY = 4

def seed_realistic_data(
    num_days: int = None,
    posts_per_symbol_per_day: int = None,
    data_source: str = "test",
):
    """Seed realistic data with natural sentiment patterns."""
    if num_days is None:
        num_days = NUM_DAYS
    if posts_per_symbol_per_day is None:
        posts_per_symbol_per_day = POSTS_PER_SYMBOL_PER_DAY

    db = SessionLocal()
    try:
        _clear_data_by_source(db, data_source)
        db.commit()

        posts_created = _seed_realistic_social_posts(db, num_days, posts_per_symbol_per_day, data_source)
        market_created = _seed_market_data(db, num_days, data_source)
        sentiment_created = _seed_realistic_sentiment_records(db, data_source)
        signals_created = _seed_realistic_divergence_signals(db, num_days, data_source)
        db.commit()

        logger.info(
            f"Realistic seed complete ({data_source}): {posts_created} posts, {sentiment_created} sentiment, "
            f"{market_created} market, {signals_created} signals"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Seed failed: {e}")
        raise
    finally:
        db.close()

def _clear_data_by_source(db, data_source: str):
    """Remove all rows for the given data_source."""
    db.query(DivergenceSignal).filter(DivergenceSignal.data_source == data_source).delete()
    db.flush()
    db.query(SentimentRecord).filter(SentimentRecord.data_source == data_source).delete()
    db.flush()
    live_post_ids = [r.id for r in db.query(SocialPost.id).filter(SocialPost.data_source == data_source).all()]
    if live_post_ids:
        db.query(SentimentRecord).filter(SentimentRecord.post_id.in_(live_post_ids)).delete(synchronize_session=False)
        db.flush()
    db.query(MarketData).filter(MarketData.data_source == data_source).delete()
    db.flush()
    db.query(SocialPost).filter(SocialPost.data_source == data_source).delete()
    db.flush()
    logger.info(f"Cleared existing {data_source} data")

def _seed_realistic_social_posts(db, num_days: int, per_symbol_per_day: int, data_source: str = "test") -> int:
    """Create social posts with realistic sentiment patterns."""
    now = datetime.utcnow()
    sources = ["telegram", "youtube", "twitter"]
    created = 0
    prefix = "realistic_seed"

    for symbol in NIFTY_50_SYMBOLS:
        profile = _get_symbol_profile(symbol)
        num_hours = num_days * 24
        sentiment_series = _generate_sentiment_time_series(symbol, num_hours, profile)
        
        for day in range(num_days):
            day_start = now - timedelta(days=day + 1)
            day_hours = sentiment_series[day * 24:(day + 1) * 24]
            
            for i in range(per_symbol_per_day):
                # Pick a random hour in the day
                hour_idx = random.randint(0, 23)
                sentiment_score = day_hours[hour_idx]
                label = _sentiment_to_label(sentiment_score)
                
                comment = random.choice(SAMPLE_COMMENTS[label])
                source = random.choice(sources)

                # Inject symbol mention
                if random.random() < 0.6:
                    comment = f"{symbol} - {comment}"

                # Spread within the hour
                minute_offset = random.uniform(0, 60)
                posted_at = day_start + timedelta(hours=hour_idx, minutes=minute_offset)

                source_id = f"{prefix}_{source}_{symbol}_{day}_{i}"

                post = SocialPost(
                    source=source,
                    symbol=symbol,
                    raw_text=comment,
                    cleaned_text=comment,
                    author=f"seed_user_{random.randint(1, 200)}",
                    source_id=source_id,
                    posted_at=posted_at,
                    ingested_at=posted_at + timedelta(minutes=random.randint(1, 30)),
                    data_source=data_source,
                )
                db.add(post)
                created += 1

        if created % 2000 == 0:
            db.flush()

    db.flush()
    logger.info(f"Seeded {created} realistic social posts for {len(NIFTY_50_SYMBOLS)} symbols ({data_source})")
    return created

def _seed_market_data(db, num_days: int, data_source: str = "test") -> int:
    """Create market data with realistic price movements."""
    now = datetime.utcnow()
    created = 0

    for symbol in NIFTY_50_SYMBOLS:
        profile = _get_symbol_profile(symbol)
        base_price = random.uniform(200, 3000)
        
        # Add trend based on profile
        trend = (profile["base_sentiment"] - 0.5) * 0.02  # Daily trend

        for day_offset in range(num_days):
            date = (now - timedelta(days=day_offset)).replace(
                hour=15, minute=30, second=0, microsecond=0
            )

            # Realistic price movement with trend and volatility
            change_pct = trend + random.gauss(0, profile["volatility"] * 0.5)
            change_pct = max(-0.10, min(0.10, change_pct))  # Limit daily change
            
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
                data_source=data_source,
            )
            db.merge(record)
            created += 1
            base_price = close_price

    db.flush()
    logger.info(f"Seeded {created} realistic market data records for {len(NIFTY_50_SYMBOLS)} symbols ({data_source})")
    return created

def _seed_realistic_sentiment_records(db, data_source: str = "test") -> int:
    """Create sentiment records based on realistic sentiment patterns."""
    posts = db.query(SocialPost).filter(SocialPost.data_source == data_source).all()
    created = 0

    # Group posts by symbol and calculate sentiment patterns
    symbol_posts = {}
    for post in posts:
        if post.symbol not in symbol_posts:
            symbol_posts[post.symbol] = []
        symbol_posts[post.symbol].append(post)

    for symbol, posts_list in symbol_posts.items():
        profile = _get_symbol_profile(symbol)
        
        # Sort posts by time
        posts_list.sort(key=lambda p: p.posted_at or datetime.min)
        
        # Generate sentiment series for this symbol
        num_hours = len(posts_list) // 2 + 1  # Rough estimate
        sentiment_series = _generate_sentiment_time_series(symbol, num_hours, profile)
        
        for i, post in enumerate(posts_list):
            # Use sentiment from series or generate based on content
            if i < len(sentiment_series):
                sentiment_score = sentiment_series[i]
            else:
                sentiment_score = profile["base_sentiment"] + random.gauss(0, profile["volatility"])
                sentiment_score = max(0.1, min(0.9, sentiment_score))
            
            label = _sentiment_to_label(sentiment_score)
            score = _confidence_score(label, sentiment_score)

            scored_at = post.posted_at + timedelta(minutes=random.randint(5, 60)) if post.posted_at else post.ingested_at

            record = SentimentRecord(
                post_id=post.id,
                symbol=post.symbol,
                label=label,
                score=score,
                model_version="finbert-realistic",
                scored_at=scored_at,
                data_source=data_source,
            )
            db.add(record)
            created += 1

        if created % 2000 == 0:
            db.flush()

    db.flush()
    logger.info(f"Seeded {created} realistic sentiment records ({data_source})")
    return created

def _seed_realistic_divergence_signals(db, num_days: int, data_source: str = "test") -> int:
    """Create realistic divergence signals based on sentiment patterns."""
    now = datetime.utcnow()
    created = 0

    for symbol in NIFTY_50_SYMBOLS:
        profile = _get_symbol_profile(symbol)
        
        # Generate sentiment series for divergence calculation
        num_hours = num_days * 24
        sentiment_series = _generate_sentiment_time_series(symbol, num_hours, profile)

        for day in range(num_days):
            # 6 signals per day (every 4 hours)
            for hour_slot in range(6):
                ts = now - timedelta(days=day, hours=hour_slot * 4)
                
                # Get sentiment around this time
                hour_idx = day * 24 + hour_slot * 4
                if hour_idx < len(sentiment_series):
                    current_sentiment = sentiment_series[hour_idx]
                    
                    # Calculate divergence (sentiment vs historical average)
                    recent_sentiments = sentiment_series[max(0, hour_idx - 24):hour_idx]
                    if recent_sentiments:
                        avg_sentiment = sum(recent_sentiments) / len(recent_sentiments)
                        divergence = (current_sentiment - avg_sentiment) * 3  # Scale up
                    else:
                        divergence = 0
                else:
                    divergence = random.gauss(0, profile["volatility"])
                
                # Add some noise and trend
                trend = (profile["base_sentiment"] - 0.5) * 2
                noise = random.gauss(0, 0.3)
                div_score = round(divergence + trend + noise, 3)

                # Classify divergence direction
                if div_score > 1.5:
                    direction = "hype"
                elif div_score < -1.5:
                    direction = "panic"
                else:
                    direction = "neutral"

                # Velocity based on sentiment change rate
                if hour_idx > 0 and hour_idx < len(sentiment_series):
                    sentiment_change = abs(sentiment_series[hour_idx] - sentiment_series[hour_idx - 1])
                    velocity = round(50 + sentiment_change * 200 + random.gauss(0, 5), 2)
                else:
                    velocity = round(50 + random.gauss(0, 10), 2)
                
                velocity = max(0, min(100, velocity))

                # Discussion volume correlates with sentiment extremes
                if hour_idx < len(sentiment_series):
                    sentiment_extremeness = abs(sentiment_series[hour_idx] - 0.5) * 2
                    disc_vol = round(20 + sentiment_extremeness * 60 + random.gauss(0, 10))
                else:
                    disc_vol = random.randint(20, 80)
                
                disc_vol = max(10, min(100, disc_vol))

                # Confidence components
                model_cert = round(random.uniform(0.65, 0.95), 4)
                data_suff = round(random.uniform(0.25, 0.70), 4)
                sig_consist = round(random.uniform(0.50, 0.95), 4)
                confidence = round(
                    0.4 * model_cert + 0.3 * data_suff + 0.3 * sig_consist, 4
                )

                # Avg sentiment score
                if hour_idx < len(sentiment_series):
                    avg_sent = round(sentiment_series[hour_idx], 4)
                else:
                    avg_sent = round(0.5 + random.gauss(0, 0.1), 4)
                
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
                    data_source=data_source,
                )
                db.add(signal)
                created += 1

        if created % 500 == 0:
            db.flush()

    db.flush()
    logger.info(f"Seeded {created} realistic divergence signals for {len(NIFTY_50_SYMBOLS)} symbols ({data_source})")
    return created
