"""API routes for divergence and confidence signals."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.divergence_signal import DivergenceSignal

def _get_mode(mode):
    if mode in ("test", "live", "demo"):
        return mode
    from app.main import _data_mode
    return _data_mode

router = APIRouter(prefix="/divergence", tags=["divergence"])


@router.get("/latest/{symbol}")
def get_latest_divergence(
    symbol: str,
    mode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get the most recent divergence signal for a symbol."""
    ds = _get_mode(mode)
    signal = (
        db.query(DivergenceSignal)
        .filter(DivergenceSignal.symbol == symbol.upper(), DivergenceSignal.data_source == ds)
        .order_by(desc(DivergenceSignal.computed_at))
        .first()
    )

    if not signal:
        return {"symbol": symbol.upper(), "signal": None}

    return {
        "symbol": symbol.upper(),
        "signal": {
            "divergence_score": signal.divergence_score,
            "divergence_direction": signal.divergence_direction,
            "sentiment_score_avg": signal.sentiment_score_avg,
            "discussion_volume": signal.discussion_volume,
            "sentiment_velocity": signal.sentiment_velocity,
            "confidence_score": signal.confidence_score,
            "computed_at": signal.computed_at.isoformat(),
        },
    }


@router.get("/timeseries/{symbol}")
def get_divergence_timeseries(
    symbol: str,
    hours: int = Query(default=72, ge=1, le=720),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
    mode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get divergence signal timeseries for charting."""
    ds = _get_mode(mode)
    if start:
        since = datetime.fromisoformat(start)
    else:
        since = datetime.utcnow() - timedelta(hours=hours)
    until = datetime.fromisoformat(end) if end else datetime.utcnow()

    signals = (
        db.query(DivergenceSignal)
        .filter(
            DivergenceSignal.symbol == symbol.upper(),
            DivergenceSignal.computed_at >= since,
            DivergenceSignal.computed_at <= until,
            DivergenceSignal.data_source == ds,
        )
        .order_by(DivergenceSignal.computed_at)
        .all()
    )

    return {
        "symbol": symbol.upper(),
        "data": [
            {
                "timestamp": s.computed_at.isoformat(),
                "divergence_score": s.divergence_score,
                "divergence_direction": s.divergence_direction,
                "confidence_score": s.confidence_score,
                "sentiment_velocity": s.sentiment_velocity,
                "discussion_volume": s.discussion_volume,
            }
            for s in signals
        ],
    }


@router.get("/overview")
def get_overview(
    mode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get latest divergence signal for all tracked symbols."""
    from app.core.constants import NIFTY_50_SYMBOLS
    from sqlalchemy import func
    ds = _get_mode(mode)

    overview = []
    for symbol in NIFTY_50_SYMBOLS:
        signal = (
            db.query(DivergenceSignal)
            .filter(DivergenceSignal.symbol == symbol, DivergenceSignal.data_source == ds)
            .order_by(desc(DivergenceSignal.computed_at))
            .first()
        )
        if signal:
            overview.append(
                {
                    "symbol": symbol,
                    "divergence_score": signal.divergence_score,
                    "divergence_direction": signal.divergence_direction,
                    "confidence_score": signal.confidence_score,
                    "sentiment_velocity": signal.sentiment_velocity,
                    "discussion_volume": signal.discussion_volume,
                    "computed_at": signal.computed_at.isoformat(),
                }
            )

    return {"stocks": overview}


@router.get("/index-summary")
def get_index_summary(
    hours: int = Query(default=168, ge=1, le=720),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
    mode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get Nifty 50 index-level aggregated analytics."""
    from app.core.constants import NIFTY_50_SYMBOLS
    from app.models.sentiment_record import SentimentRecord
    from sqlalchemy import func
    ds = _get_mode(mode)

    if start:
        since = datetime.fromisoformat(start)
    else:
        since = datetime.utcnow() - timedelta(hours=hours)
    until = datetime.fromisoformat(end) if end else datetime.utcnow()

    # Latest signal per symbol
    stocks = []
    hype_count = 0
    panic_count = 0
    neutral_count = 0
    total_volume = 0
    total_velocity = 0
    total_confidence = 0
    total_divergence = 0
    count = 0

    for symbol in NIFTY_50_SYMBOLS:
        signal = (
            db.query(DivergenceSignal)
            .filter(
                DivergenceSignal.symbol == symbol,
                DivergenceSignal.computed_at >= since,
                DivergenceSignal.computed_at <= until,
                DivergenceSignal.data_source == ds,
            )
            .order_by(desc(DivergenceSignal.computed_at))
            .first()
        )
        if signal:
            d = signal.divergence_direction
            if d == "hype":
                hype_count += 1
            elif d == "panic":
                panic_count += 1
            else:
                neutral_count += 1
            total_volume += signal.discussion_volume or 0
            total_velocity += signal.sentiment_velocity or 0
            total_confidence += signal.confidence_score or 0
            total_divergence += signal.divergence_score or 0
            count += 1

    # Sentiment distribution across all stocks
    sentiment_counts = (
        db.query(SentimentRecord.label, func.count(SentimentRecord.id))
        .filter(
            SentimentRecord.scored_at >= since,
            SentimentRecord.scored_at <= until,
            SentimentRecord.data_source == ds,
        )
        .group_by(SentimentRecord.label)
        .all()
    )
    sentiment_dist = {label: cnt for label, cnt in sentiment_counts}

    # Top movers: stocks with highest absolute divergence
    top_hype = []
    top_panic = []
    for symbol in NIFTY_50_SYMBOLS:
        signal = (
            db.query(DivergenceSignal)
            .filter(
                DivergenceSignal.symbol == symbol,
                DivergenceSignal.computed_at >= since,
                DivergenceSignal.computed_at <= until,
                DivergenceSignal.data_source == ds,
            )
            .order_by(desc(DivergenceSignal.computed_at))
            .first()
        )
        if signal:
            entry = {
                "symbol": symbol,
                "divergence_score": signal.divergence_score,
                "sentiment_velocity": signal.sentiment_velocity,
                "discussion_volume": signal.discussion_volume,
                "confidence_score": signal.confidence_score,
            }
            if signal.divergence_score > 0:
                top_hype.append(entry)
            else:
                top_panic.append(entry)

    top_hype.sort(key=lambda x: x["divergence_score"], reverse=True)
    top_panic.sort(key=lambda x: x["divergence_score"])

    # Index-level timeseries: average divergence across all stocks per time slot
    all_signals = (
        db.query(DivergenceSignal)
        .filter(
            DivergenceSignal.computed_at >= since,
            DivergenceSignal.computed_at <= until,
            DivergenceSignal.data_source == ds,
        )
        .order_by(DivergenceSignal.computed_at)
        .all()
    )
    from collections import defaultdict
    time_buckets = defaultdict(lambda: {"div": [], "vel": [], "conf": [], "vol": []})
    for s in all_signals:
        # Bucket by hour
        bucket = s.computed_at.replace(minute=0, second=0, microsecond=0)
        time_buckets[bucket]["div"].append(s.divergence_score or 0)
        time_buckets[bucket]["vel"].append(s.sentiment_velocity or 0)
        time_buckets[bucket]["conf"].append(s.confidence_score or 0)
        time_buckets[bucket]["vol"].append(s.discussion_volume or 0)

    index_timeseries = []
    for ts in sorted(time_buckets.keys()):
        b = time_buckets[ts]
        n = len(b["div"])
        index_timeseries.append({
            "timestamp": ts.isoformat(),
            "avg_divergence": round(sum(b["div"]) / n, 3) if n else 0,
            "avg_velocity": round(sum(b["vel"]) / n, 1) if n else 0,
            "avg_confidence": round(sum(b["conf"]) / n, 3) if n else 0,
            "total_volume": sum(b["vol"]),
            "stocks_count": n,
        })

    return {
        "direction_distribution": {
            "hype": hype_count,
            "panic": panic_count,
            "neutral": neutral_count,
        },
        "sentiment_distribution": {
            "positive": sentiment_dist.get("positive", 0),
            "negative": sentiment_dist.get("negative", 0),
            "neutral": sentiment_dist.get("neutral", 0),
        },
        "index_stats": {
            "avg_divergence": round(total_divergence / count, 3) if count else 0,
            "avg_velocity": round(total_velocity / count, 1) if count else 0,
            "avg_confidence": round(total_confidence / count, 3) if count else 0,
            "total_volume": total_volume,
            "stocks_tracked": count,
        },
        "top_hype": top_hype[:5],
        "top_panic": top_panic[:5],
        "index_timeseries": index_timeseries,
    }
