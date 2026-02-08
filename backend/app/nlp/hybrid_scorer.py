"""Hybrid sentiment scorer: Gemini for Hinglish, FinBERT for English.

Routes posts based on language detection:
  - Hinglish / Hindi / mixed → Gemini API (better at understanding slang, emojis, code-switching)
  - Pure English → FinBERT (fast, free, no API dependency)
  - Fallback → FinBERT if Gemini is unavailable or rate-limited
"""

import re
from loguru import logger

from app.core.config import get_settings
from app.core.usage_tracker import is_blocked

settings = get_settings()

# Hindi/Devanagari Unicode range + common Hinglish patterns
_DEVANAGARI_RE = re.compile(r'[\u0900-\u097F]')
_HINGLISH_WORDS = {
    "hai", "hain", "nahi", "kya", "yeh", "woh", "bhai", "yaar", "abhi",
    "aaj", "kal", "kab", "kaise", "kyun", "accha", "theek", "bahut",
    "bohot", "paisa", "paise", "lakh", "crore", "karega", "karenge",
    "jayega", "jaayega", "aayega", "doobega", "giregi", "nikalega",
    "pakka", "sahi", "galat", "zabardast", "mast", "ekdum", "bilkul",
    "lagta", "lagega", "lagti", "dekho", "dekhna", "samjho", "bolo",
    "chalo", "chal", "arrey", "arre", "oye", "bro", "dost",
    "lelo", "karlo", "bhago", "ruko", "mat", "toh", "lekin",
    "wala", "waala", "wali", "waali", "mein", "pe", "ko", "ka", "ki",
    "ke", "se", "tak", "par", "aur", "ya", "jo", "jab", "tab",
    "phir", "fir", "bas", "sirf", "sab", "kuch", "koi",
    "laga", "lagao", "rakho", "chhoddo", "pakdo",
    "multibagger", "rocket", "moon", "trap",
}


def is_hinglish(text: str) -> bool:
    """Detect if text contains Hinglish or Hindi content."""
    # Check for Devanagari script
    if _DEVANAGARI_RE.search(text):
        return True

    # Check for common Hinglish words
    words = set(re.findall(r'[a-zA-Z]+', text.lower()))
    hinglish_count = len(words & _HINGLISH_WORDS)

    # If 2+ Hinglish words found, classify as Hinglish
    return hinglish_count >= 2


def score_texts_hybrid(texts: list[str], batch_size: int = 20) -> list[dict]:
    """Score a list of texts using Gemini for Hinglish and FinBERT for English.

    Returns list of dicts with keys: label, score, confidence, scorer
    """
    if not texts:
        return []

    # Classify each text
    hinglish_indices = []
    english_indices = []
    for i, text in enumerate(texts):
        if is_hinglish(text):
            hinglish_indices.append(i)
        else:
            english_indices.append(i)

    results = [None] * len(texts)
    gemini_available = bool(settings.GEMINI_API_KEY) and not is_blocked("gemini")

    # --- Score Hinglish texts with Gemini (or fallback to FinBERT) ---
    if hinglish_indices:
        hinglish_texts = [texts[i] for i in hinglish_indices]

        if gemini_available:
            logger.info(f"Scoring {len(hinglish_texts)} Hinglish texts with Gemini")
            hinglish_results = _score_with_gemini(hinglish_texts, batch_size)
        else:
            reason = "no API key" if not settings.GEMINI_API_KEY else "rate limited"
            logger.info(f"Gemini unavailable ({reason}), falling back to FinBERT for {len(hinglish_texts)} Hinglish texts")
            hinglish_results = _score_with_finbert(hinglish_texts)

        for idx, result in zip(hinglish_indices, hinglish_results):
            results[idx] = result

    # --- Score English texts with FinBERT ---
    if english_indices:
        english_texts = [texts[i] for i in english_indices]
        logger.info(f"Scoring {len(english_texts)} English texts with FinBERT")
        english_results = _score_with_finbert(english_texts)

        for idx, result in zip(english_indices, english_results):
            results[idx] = result

    logger.info(
        f"Hybrid scoring complete: {len(hinglish_indices)} Hinglish "
        f"({'Gemini' if gemini_available and hinglish_indices else 'FinBERT'}), "
        f"{len(english_indices)} English (FinBERT)"
    )
    return results


def _score_with_gemini(texts: list[str], batch_size: int = 20) -> list[dict]:
    """Score texts using Gemini API in batches."""
    import time
    from app.nlp.labeler_llm import label_batch_gemini

    api_key = settings.GEMINI_API_KEY
    all_results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        labels = label_batch_gemini(batch, api_key)

        for lbl in labels:
            label = lbl.get("label", "neutral")
            confidence = lbl.get("confidence", 0.0)
            if label not in ("positive", "negative", "neutral"):
                label = "neutral"
                confidence = 0.0
            all_results.append({
                "label": label,
                "score": confidence,
                "confidence": confidence,
                "scorer": "gemini",
            })

        # Gemini free tier: 15 RPM → 4 sec between batches
        if i + batch_size < len(texts):
            time.sleep(4)

    return all_results


def _score_with_finbert(texts: list[str]) -> list[dict]:
    """Score texts using FinBERT in batch."""
    from app.nlp.sentiment import predict_batch

    results = predict_batch(texts)
    return [
        {
            "label": r["label"],
            "score": r["score"],
            "confidence": r["score"],
            "scorer": "finbert",
        }
        for r in results
    ]
