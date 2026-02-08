"""Zero-shot FinBERT self-training labeler (free fallback).

Uses FinBERT's own predictions as pseudo-labels, keeping only high-confidence
predictions for fine-tuning. No API cost.

Usage:
    python -m app.nlp.labeler_zeroshot --source db --output data/labeled_zeroshot.jsonl --limit 1000
    python -m app.nlp.labeler_zeroshot --source file --input data/raw_comments.txt --output data/labeled_zeroshot.jsonl
"""

import json
import argparse
from pathlib import Path
from loguru import logger

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from app.nlp.preprocessor import clean_text

MODEL_NAME = "ProsusAI/finbert"
LABELS = ["positive", "negative", "neutral"]


def load_model():
    """Load FinBERT for zero-shot pseudo-labeling."""
    logger.info(f"Loading {MODEL_NAME} for zero-shot labeling...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def predict_batch(
    texts: list[str],
    tokenizer,
    model,
    batch_size: int = 32,
) -> list[dict]:
    """Run FinBERT inference and return labels + confidence."""
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        inputs = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        for j in range(len(batch)):
            probs_np = probs[j].numpy()
            idx = int(np.argmax(probs_np))
            results.append(
                {
                    "label": LABELS[idx],
                    "confidence": float(probs_np[idx]),
                    "probabilities": {LABELS[k]: float(probs_np[k]) for k in range(3)},
                }
            )

    return results


def label_from_db(
    output_path: str,
    limit: int = 1000,
    confidence_threshold: float = 0.85,
    batch_size: int = 32,
):
    """Pull posts from DB, pseudo-label with FinBERT, save high-confidence ones."""
    from app.core.database import SessionLocal
    from app.models.social_post import SocialPost

    db = SessionLocal()
    posts = db.query(SocialPost).limit(limit).all()
    db.close()

    if not posts:
        logger.warning("No posts found in DB")
        return

    texts = [p.raw_text for p in posts]
    _label_and_save(texts, output_path, confidence_threshold, batch_size)


def label_from_file(
    input_path: str,
    output_path: str,
    confidence_threshold: float = 0.85,
    batch_size: int = 32,
):
    """Read raw comments from file, pseudo-label with FinBERT, save high-confidence ones."""
    texts = Path(input_path).read_text(encoding="utf-8").strip().splitlines()
    texts = [t.strip() for t in texts if t.strip()]

    if not texts:
        logger.warning(f"No comments found in {input_path}")
        return

    _label_and_save(texts, output_path, confidence_threshold, batch_size)


def _label_and_save(
    texts: list[str],
    output_path: str,
    confidence_threshold: float,
    batch_size: int,
):
    """Core loop: clean → predict → filter → save JSONL."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    tokenizer, model = load_model()

    # Clean texts
    cleaned = [clean_text(t) for t in texts]

    # Predict
    logger.info(f"Running zero-shot inference on {len(cleaned)} texts...")
    predictions = predict_batch(cleaned, tokenizer, model, batch_size)

    # Filter and save
    total = 0
    kept = 0

    with open(output, "w", encoding="utf-8") as f:
        for raw, cleaned_t, pred in zip(texts, cleaned, predictions):
            total += 1
            conf = pred["confidence"]
            label = pred["label"]

            if conf >= confidence_threshold:
                record = {
                    "text": raw,
                    "text_cleaned": cleaned_t,
                    "label": label,
                    "confidence": round(conf, 4),
                    "source": "zeroshot_finbert",
                    "probabilities": {
                        k: round(v, 4) for k, v in pred["probabilities"].items()
                    },
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                kept += 1

    logger.info(
        f"Zero-shot labeling complete: {total} total, {kept} kept "
        f"(threshold={confidence_threshold}, kept_rate={kept/total*100:.1f}%)"
    )
    logger.info(f"Output saved to {output_path}")

    # Distribution summary
    _print_distribution(output_path)


def _print_distribution(path: str):
    """Print label distribution of the output file."""
    from collections import Counter

    counts = Counter()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            counts[rec["label"]] += 1

    total = sum(counts.values())
    logger.info("Label distribution:")
    for label in LABELS:
        c = counts.get(label, 0)
        pct = c / total * 100 if total else 0
        logger.info(f"  {label}: {c} ({pct:.1f}%)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zero-shot FinBERT pseudo-labeler")
    parser.add_argument("--source", choices=["db", "file"], default="db")
    parser.add_argument("--input", type=str, default=None, help="Input file (one comment per line)")
    parser.add_argument("--output", type=str, default="data/labeled_zeroshot.jsonl")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--threshold", type=float, default=0.85, help="Confidence threshold (higher = fewer but cleaner labels)")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()

    if args.source == "file":
        if not args.input:
            raise ValueError("--input required when --source=file")
        label_from_file(args.input, args.output, args.threshold, args.batch_size)
    else:
        label_from_db(args.output, args.limit, args.threshold, args.batch_size)
