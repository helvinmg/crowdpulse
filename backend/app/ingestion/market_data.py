"""Layer 1: Market data fetcher using yfinance (NSE/BSE proxy)."""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
from loguru import logger
from app.core.constants import NIFTY_50_SYMBOLS
from app.core.usage_tracker import record_usage, is_blocked


def fetch_stock_data(
    symbol: str,
    period: str = "5d",
) -> list[dict]:
    """Fetch OHLCV data for a single NSE stock via yfinance."""
    if is_blocked("yfinance"):
        logger.warning(f"yfinance API limit reached — skipping {symbol}")
        return []

    if not record_usage("yfinance"):
        return []

    nse_ticker = f"{symbol}.NS"
    records = []

    try:
        ticker = yf.Ticker(nse_ticker)
        df = ticker.history(period=period)

        if df.empty:
            logger.warning(f"No data returned for {nse_ticker}")
            return []

        # Estimate delivery % heuristic for each row
        # Nifty 50 stocks typically have 35-65% delivery.
        # Higher intraday range relative to close suggests more speculative (lower delivery).
        for date, row in df.iterrows():
            volume = int(row.get("Volume", 0))
            high = float(row.get("High", 0))
            low = float(row.get("Low", 0))
            close = float(row.get("Close", 0))

            delivery_pct = _estimate_delivery_pct(high, low, close)
            delivery_vol = int(volume * delivery_pct) if volume else None

            records.append(
                {
                    "symbol": symbol,
                    "date": date.to_pydatetime().replace(tzinfo=timezone.utc),
                    "open": float(row.get("Open", 0)),
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": volume,
                    "delivery_volume": delivery_vol,
                    "delivery_pct": round(delivery_pct * 100, 2),
                }
            )

        logger.info(f"Fetched {len(records)} records for {symbol}")

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")

    return records


def fetch_nifty50_data(period: str = "5d") -> list[dict]:
    """Fetch market data for all Nifty 50 stocks."""
    all_records = []
    for symbol in NIFTY_50_SYMBOLS:
        if is_blocked("yfinance"):
            logger.warning("yfinance API limit reached mid-run — stopping market data fetch")
            break
        records = fetch_stock_data(symbol, period)
        all_records.extend(records)
    return all_records


def _estimate_delivery_pct(high: float, low: float, close: float) -> float:
    """Estimate delivery percentage from intraday price range.

    Heuristic: wider intraday range relative to close = more speculative = lower delivery.
    Nifty 50 stocks typically see 35-65% delivery.
    """
    if close <= 0:
        return 0.50  # default midpoint

    intraday_range_pct = (high - low) / close if close else 0

    # Map: 0% range → ~60% delivery, 5%+ range → ~35% delivery
    # Linear interpolation clamped to [0.35, 0.65]
    delivery = 0.60 - (intraday_range_pct * 5.0)
    return max(0.35, min(0.65, delivery))
