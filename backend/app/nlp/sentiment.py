"""Layer 3: Sentiment analysis using FinBERT (with LoRA fine-tuning support)."""

from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel
import torch
import numpy as np
from loguru import logger

BASE_MODEL_NAME = "ProsusAI/finbert"
FINETUNED_MODEL_DIR = Path("models/finbert-hinglish")

_tokenizer = None
_model = None
_model_version = "finbert-base"


def load_model():
    """Load fine-tuned LoRA model if available, otherwise base FinBERT (lazy singleton)."""
    global _tokenizer, _model, _model_version
    if _tokenizer is None:
        if FINETUNED_MODEL_DIR.exists() and (FINETUNED_MODEL_DIR / "adapter_config.json").exists():
            logger.info(f"Loading fine-tuned model from {FINETUNED_MODEL_DIR}")
            _tokenizer = AutoTokenizer.from_pretrained(FINETUNED_MODEL_DIR)
            base_model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL_NAME, num_labels=3)
            _model = PeftModel.from_pretrained(base_model, str(FINETUNED_MODEL_DIR))
            _model_version = "finbert-hinglish-lora"
        else:
            logger.info(f"Fine-tuned model not found, loading base: {BASE_MODEL_NAME}")
            _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
            _model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL_NAME)
            _model_version = "finbert-base"
        _model.eval()
        logger.info(f"Sentiment model loaded: {_model_version}")
    return _tokenizer, _model


def get_model_version() -> str:
    """Return the currently loaded model version string."""
    return _model_version


def predict_sentiment(text: str) -> dict:
    """Predict sentiment for a single text.

    Returns:
        dict with keys: label (positive/negative/neutral), score (confidence 0-1)
    """
    tokenizer, model = load_model()
    labels = ["positive", "negative", "neutral"]

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

    probs_np = probs.numpy()[0]
    idx = int(np.argmax(probs_np))

    return {
        "label": labels[idx],
        "score": float(probs_np[idx]),
        "probabilities": {labels[i]: float(probs_np[i]) for i in range(3)},
    }


def predict_batch(texts: list[str], batch_size: int = 16) -> list[dict]:
    """Predict sentiment for a batch of texts."""
    tokenizer, model = load_model()
    labels = ["positive", "negative", "neutral"]
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        inputs = tokenizer(
            batch, return_tensors="pt", truncation=True, max_length=512, padding=True
        )

        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        for j in range(len(batch)):
            probs_np = probs[j].numpy()
            idx = int(np.argmax(probs_np))
            results.append(
                {
                    "label": labels[idx],
                    "score": float(probs_np[idx]),
                    "probabilities": {labels[k]: float(probs_np[k]) for k in range(3)},
                }
            )

    logger.info(f"Scored {len(results)} texts")
    return results
