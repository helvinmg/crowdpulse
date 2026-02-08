"""Layer 4: Confidence scoring engine."""

from app.core.constants import CONFIDENCE_WEIGHTS
from loguru import logger


def compute_confidence(
    model_certainty: float,
    data_sufficiency: float,
    signal_consistency: float,
) -> float:
    """Compute weighted confidence score.

    All inputs should be normalised to 0-1.

    Confidence = 0.4 * model_certainty + 0.3 * data_sufficiency + 0.3 * signal_consistency
    """
    score = (
        CONFIDENCE_WEIGHTS["model_certainty"] * _clamp(model_certainty)
        + CONFIDENCE_WEIGHTS["data_sufficiency"] * _clamp(data_sufficiency)
        + CONFIDENCE_WEIGHTS["signal_consistency"] * _clamp(signal_consistency)
    )
    logger.debug(
        f"Confidence: mc={model_certainty:.2f}, ds={data_sufficiency:.2f}, "
        f"sc={signal_consistency:.2f} → {score:.3f}"
    )
    return round(score, 4)


def estimate_data_sufficiency(
    comment_count: int,
    min_threshold: int = 10,
    ideal_threshold: int = 100,
) -> float:
    """Estimate data sufficiency based on comment volume.

    Returns 0-1 where 1 means ideal or above threshold.
    """
    if comment_count <= 0:
        return 0.0
    if comment_count >= ideal_threshold:
        return 1.0
    return comment_count / ideal_threshold


def estimate_signal_consistency(recent_labels: list[str]) -> float:
    """Estimate signal consistency from recent sentiment labels.

    Higher consistency = labels are more uniform across recent periods.
    Returns 0-1.
    """
    if not recent_labels:
        return 0.0

    from collections import Counter

    counts = Counter(recent_labels)
    total = len(recent_labels)
    max_freq = max(counts.values())
    return max_freq / total


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))
