"""API routes for sentiment data."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.sentiment_record import SentimentRecord
from app.models.social_post import SocialPost


def _parse_since(hours: int, start: Optional[str], end: Optional[str]):
    """Return (since, until) datetimes from either hours or explicit dates."""
    if start:
        since = datetime.fromisoformat(start)
    else:
        since = datetime.utcnow() - timedelta(hours=hours)
    until = datetime.fromisoformat(end) if end else datetime.utcnow()
    return since, until

def _get_mode(mode: Optional[str]) -> str:
    """Resolve data_source from query param or server default."""
    if mode in ("test", "live"):
        return mode
    from app.main import _data_mode
    return _data_mode

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.get("/latest/{symbol}")
def get_latest_sentiment(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=168),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
    mode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get aggregated sentiment for a symbol over the last N hours."""
    since, until = _parse_since(hours, start, end)
    ds = _get_mode(mode)

    records = (
        db.query(SentimentRecord)
        .filter(
            SentimentRecord.symbol == symbol.upper(),
            SentimentRecord.scored_at >= since,
            SentimentRecord.scored_at <= until,
            SentimentRecord.data_source == ds,
        )
        .all()
    )

    if not records:
        return {"symbol": symbol.upper(), "count": 0, "sentiment": None}

    scores = [r.score for r in records if r.label == "positive"]
    neg_scores = [r.score for r in records if r.label == "negative"]

    return {
        "symbol": symbol.upper(),
        "count": len(records),
        "positive_count": len(scores),
        "negative_count": len(neg_scores),
        "neutral_count": len(records) - len(scores) - len(neg_scores),
        "avg_positive_confidence": round(sum(scores) / len(scores), 4) if scores else 0,
        "avg_negative_confidence": round(sum(neg_scores) / len(neg_scores), 4) if neg_scores else 0,
        "period_hours": hours,
    }


@router.get("/timeseries/{symbol}")
def get_sentiment_timeseries(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=168),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
    mode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get sentiment score timeseries for charting."""
    since, until = _parse_since(hours, start, end)
    ds = _get_mode(mode)

    records = (
        db.query(SentimentRecord)
        .filter(
            SentimentRecord.symbol == symbol.upper(),
            SentimentRecord.scored_at >= since,
            SentimentRecord.scored_at <= until,
            SentimentRecord.data_source == ds,
        )
        .order_by(SentimentRecord.scored_at)
        .all()
    )

    return {
        "symbol": symbol.upper(),
        "data": [
            {
                "timestamp": r.scored_at.isoformat(),
                "label": r.label,
                "score": r.score,
            }
            for r in records
        ],
    }


@router.get("/volume/{symbol}")
def get_discussion_volume(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=168),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
    mode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get discussion volume (post count) over time for a symbol."""
    since, until = _parse_since(hours, start, end)
    ds = _get_mode(mode)

    posts = (
        db.query(SocialPost.ingested_at)
        .filter(
            SocialPost.symbol == symbol.upper(),
            SocialPost.ingested_at >= since,
            SocialPost.ingested_at <= until,
            SocialPost.data_source == ds,
        )
        .all()
    )

    # Aggregate per hour in Python (works on any DB)
    from collections import defaultdict
    hourly = defaultdict(int)
    for (ts,) in posts:
        if ts:
            hour_key = ts.replace(minute=0, second=0, microsecond=0)
            hourly[hour_key] += 1

    data = [
        {"timestamp": k.isoformat(), "count": v}
        for k, v in sorted(hourly.items())
    ]

    return {"symbol": symbol.upper(), "data": data}
