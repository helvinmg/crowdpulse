"""Layer 3: Sentiment velocity computation across rolling time windows."""

import pandas as pd
import numpy as np
from loguru import logger
from app.core.constants import VELOCITY_WINDOWS


def compute_velocity(
    sentiment_df: pd.DataFrame,
    windows: list[int] | None = None,
) -> pd.DataFrame:
    """Compute sentiment velocity over rolling time windows.

    Args:
        sentiment_df: DataFrame with columns [timestamp, sentiment_score]
                      sorted by timestamp ascending.
        windows: List of window sizes in minutes.

    Returns:
        DataFrame with velocity columns for each window, normalised to 0-100.
    """
    windows = windows or VELOCITY_WINDOWS
    df = sentiment_df.copy()
    df = df.sort_values("timestamp").set_index("timestamp")

    for w in windows:
        col_name = f"velocity_{w}m"
        rolling_mean = df["sentiment_score"].rolling(f"{w}min").mean()
        # Rate of change: difference of rolling mean
        velocity_raw = rolling_mean.diff()
        # Normalise to 0-100 using min-max within the window
        v_min = velocity_raw.min()
        v_max = velocity_raw.max()
        if v_max != v_min:
            df[col_name] = ((velocity_raw - v_min) / (v_max - v_min)) * 100
        else:
            df[col_name] = 50.0  # No change → midpoint

    df = df.reset_index()
    logger.info(f"Computed velocity for windows: {windows}")
    return df


def get_latest_velocity(
    sentiment_df: pd.DataFrame,
    window_minutes: int = 60,
) -> float:
    """Get the most recent velocity value for a given window."""
    df = compute_velocity(sentiment_df, windows=[window_minutes])
    col = f"velocity_{window_minutes}m"
    if col in df.columns and len(df) > 0:
        return float(df[col].iloc[-1])
    return 50.0
