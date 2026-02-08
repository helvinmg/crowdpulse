"""AI-assisted labeling of Hinglish financial comments using Google Gemini API (free tier).

Free tier: 15 RPM, 1,500 requests/day, 1M tokens/min — more than enough for labeling.
Get your API key at: https://aistudio.google.com/apikey

Usage:
    python -m app.nlp.labeler_llm --source db --output data/labeled_llm.jsonl --limit 500
    python -m app.nlp.labeler_llm --source file --input data/raw_comments.txt --output data/labeled_llm.jsonl
"""

import json
import time
import argparse
from pathlib import Path
from loguru import logger

import google.generativeai as genai

from app.core.config import get_settings
from app.core.usage_tracker import record_usage, is_blocked

settings = get_settings()

SYSTEM_INSTRUCTION = """You are an expert financial sentiment annotator specializing in Indian stock market discussions written in Hinglish (Hindi-English mix).

Your task: classify each comment into exactly ONE label:
- positive: bullish, optimistic, excited about a stock/market (e.g. "RELIANCE toh rocket jaayega", "moon confirmed 🚀🚀")
- negative: bearish, fearful, angry, warning of losses (e.g. "sab doobega", "trap hai bhai mat lo", "💀💀")
- neutral: factual, question, unrelated, or mixed with no clear lean (e.g. "kya lagta hai aaj market?", "results kab aayenge?")

Rules:
1. Emojis carry sentiment: 🚀🔥💰 = positive, 💀📉😭 = negative, 🤔❓ = neutral
2. Sarcasm is common — "haan haan moon hi jaayega" is likely negative/sarcastic
3. Slang: "rocket", "moon", "multibagger" = positive; "trap", "doob", "scam" = negative
4. If genuinely ambiguous, label as neutral
5. Return ONLY valid JSON, no extra text"""

BATCH_PROMPT_TEMPLATE = """Label each comment below. Return a JSON array with one object per comment.

Comments:
{comments_block}

Return ONLY a JSON array like:
[{{"label": "positive", "confidence": 0.92}}, {{"label": "negative", "confidence": 0.85}}, ...]"""

DEFAULT_MODEL = "gemini-2.0-flash"

_gemini_model = None


def _get_model(api_key: str, model_name: str = DEFAULT_MODEL):
    """Initialize Gemini model (lazy singleton)."""
    global _gemini_model
    if _gemini_model is None:
        genai.configure(api_key=api_key)
        _gemini_model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048,
                response_mime_type="application/json",
            ),
        )
        logger.info(f"Gemini model initialized: {model_name}")
    return _gemini_model


def label_batch_gemini(
    texts: list[str],
    api_key: str,
    model_name: str = DEFAULT_MODEL,
    max_retries: int = 3,
) -> list[dict]:
    """Send a batch of texts to Gemini API for labeling."""
    if is_blocked("gemini"):
        logger.warning("Gemini API limit reached — returning neutral labels for batch")
        return [{"label": "neutral", "confidence": 0.0} for _ in texts]

    if not record_usage("gemini"):
        return [{"label": "neutral", "confidence": 0.0} for _ in texts]

    model = _get_model(api_key, model_name)
    comments_block = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    prompt = BATCH_PROMPT_TEMPLATE.format(comments_block=comments_block)

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            content = response.text.strip()

            # Handle markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            labels = json.loads(content)

            if len(labels) != len(texts):
                logger.warning(
                    f"Label count mismatch: got {len(labels)}, expected {len(texts)}. Retrying..."
                )
                continue

            return labels

        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)

    # Fallback: return neutral with low confidence
    logger.error(f"All {max_retries} attempts failed for batch of {len(texts)}")
    return [{"label": "neutral", "confidence": 0.0} for _ in texts]


def label_from_db(
    output_path: str,
    limit: int = 1000,
    batch_size: int = 20,
    confidence_threshold: float = 0.7,
    api_key: str | None = None,
    model_name: str = DEFAULT_MODEL,
):
    """Pull unlabeled posts from DB, label via Gemini, save to JSONL."""
    from app.core.database import SessionLocal
    from app.models.social_post import SocialPost

    api_key = api_key or settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env — get one free at https://aistudio.google.com/apikey")

    db = SessionLocal()
    posts = db.query(SocialPost).limit(limit).all()
    db.close()

    if not posts:
        logger.warning("No posts found in DB")
        return

    texts = [p.raw_text for p in posts]
    _label_and_save(texts, output_path, batch_size, confidence_threshold, api_key, model_name)


def label_from_file(
    input_path: str,
    output_path: str,
    batch_size: int = 20,
    confidence_threshold: float = 0.7,
    api_key: str | None = None,
    model_name: str = DEFAULT_MODEL,
):
    """Read raw comments from a text file (one per line), label via Gemini, save to JSONL."""
    api_key = api_key or settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env — get one free at https://aistudio.google.com/apikey")

    texts = Path(input_path).read_text(encoding="utf-8").strip().splitlines()
    texts = [t.strip() for t in texts if t.strip()]

    if not texts:
        logger.warning(f"No comments found in {input_path}")
        return

    _label_and_save(texts, output_path, batch_size, confidence_threshold, api_key, model_name)


def _label_and_save(
    texts: list[str],
    output_path: str,
    batch_size: int,
    confidence_threshold: float,
    api_key: str,
    model_name: str,
):
    """Core labeling loop: batch texts → Gemini → filter → save JSONL."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    kept = 0

    with open(output, "w", encoding="utf-8") as f:
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            labels = label_batch_gemini(batch, api_key, model_name)

            for text, lbl in zip(batch, labels):
                total += 1
                conf = lbl.get("confidence", 0)
                label = lbl.get("label", "neutral")

                if label not in ("positive", "negative", "neutral"):
                    label = "neutral"
                    conf = 0.0

                record = {
                    "text": text,
                    "label": label,
                    "confidence": round(conf, 4),
                    "source": "gemini",
                    "model": model_name,
                }

                if conf >= confidence_threshold:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    kept += 1

            logger.info(f"Batch {i//batch_size + 1}: {len(batch)} texts processed")
            # Gemini free tier: 15 RPM → 4 seconds between requests to be safe
            time.sleep(4)

    logger.info(
        f"Labeling complete: {total} total, {kept} kept (threshold={confidence_threshold})"
    )
    logger.info(f"Output saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini-based Hinglish comment labeler (free)")
    parser.add_argument("--source", choices=["db", "file"], default="db")
    parser.add_argument("--input", type=str, default=None, help="Input file (one comment per line)")
    parser.add_argument("--output", type=str, default="data/labeled_llm.jsonl")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    args = parser.parse_args()

    if args.source == "file":
        if not args.input:
            raise ValueError("--input required when --source=file")
        label_from_file(args.input, args.output, args.batch_size, args.threshold, model_name=args.model)
    else:
        label_from_db(args.output, args.limit, args.batch_size, args.threshold, model_name=args.model)
