"""Layer 4: Divergence engine — compares discussion volume vs delivery volume."""

import numpy as np
import pandas as pd
from loguru import logger


def compute_divergence(
    discussion_volume: pd.Series,
    delivery_volume: pd.Series,
) -> pd.Series:
    """Compute z-score based divergence between discussion volume and delivery volume.

    Both series should share the same datetime index (aligned by date/period).

    Returns:
        pd.Series of divergence z-scores. Positive = discussion outpacing delivery (hype),
        Negative = delivery outpacing discussion (quiet accumulation).
    """
    # Normalise each to z-scores independently
    dv_z = _zscore(discussion_volume)
    mv_z = _zscore(delivery_volume)

    divergence = dv_z - mv_z
    logger.info(f"Divergence computed: mean={divergence.mean():.3f}, std={divergence.std():.3f}")
    return divergence


def classify_divergence(z_score: float, threshold: float = 1.5) -> str:
    """Classify a divergence z-score into a directional label."""
    if z_score >= threshold:
        return "hype"
    elif z_score <= -threshold:
        return "panic"
    return "neutral"


def _zscore(series: pd.Series) -> pd.Series:
    """Compute z-score for a pandas Series, handling zero std."""
    mean = series.mean()
    std = series.std()
    if std == 0 or np.isnan(std):
        return pd.Series(0.0, index=series.index)
    return (series - mean) / std
