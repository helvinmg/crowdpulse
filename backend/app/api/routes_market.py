"""API routes for market data."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.market_data import MarketData

def _get_mode(mode):
    if mode in ("test", "live", "demo"):
        return mode
    from app.main import _data_mode
    return _data_mode

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/price/{symbol}")
def get_price_data(
    symbol: str,
    days: int = Query(default=5, ge=1, le=30),
    mode: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get OHLCV price data for a symbol."""
    ds = _get_mode(mode)
    since = datetime.utcnow() - timedelta(days=days)

    records = (
        db.query(MarketData)
        .filter(
            MarketData.symbol == symbol.upper(),
            MarketData.date >= since,
            MarketData.data_source == ds,
        )
        .order_by(MarketData.date)
        .all()
    )

    return {
        "symbol": symbol.upper(),
        "data": [
            {
                "date": r.date.isoformat(),
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
                "delivery_volume": r.delivery_volume,
                "delivery_pct": r.delivery_pct,
            }
            for r in records
        ],
    }
