"""Fine-tune FinBERT on labeled Hinglish dataset using LoRA (PEFT).

Consumes JSONL output from labeler_llm.py or labeler_zeroshot.py.

Usage:
    python -m app.nlp.finetune --data data/labeled_llm.jsonl --epochs 3 --output models/finbert-hinglish
    python -m app.nlp.finetune --data data/labeled_llm.jsonl data/labeled_zeroshot.jsonl --epochs 5
"""

import json
import argparse
from pathlib import Path
from loguru import logger

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model, TaskType
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score

MODEL_NAME = "ProsusAI/finbert"
LABEL_MAP = {"positive": 0, "negative": 1, "neutral": 2}
ID_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}


def load_labeled_data(paths: list[str]) -> list[dict]:
    """Load labeled JSONL files and merge them."""
    records = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line.strip())
                if rec.get("label") in LABEL_MAP:
                    records.append(
                        {
                            "text": rec.get("text_cleaned") or rec.get("text", ""),
                            "label": LABEL_MAP[rec["label"]],
                        }
                    )
    logger.info(f"Loaded {len(records)} labeled samples from {len(paths)} file(s)")
    return records


def create_datasets(records: list[dict], test_size: float = 0.15, seed: int = 42):
    """Split into train/test and create HuggingFace Datasets."""
    train_recs, test_recs = train_test_split(
        records, test_size=test_size, random_state=seed, stratify=[r["label"] for r in records]
    )
    train_ds = Dataset.from_list(train_recs)
    test_ds = Dataset.from_list(test_recs)
    logger.info(f"Train: {len(train_ds)}, Test: {len(test_ds)}")
    return train_ds, test_ds


def tokenize_dataset(dataset: Dataset, tokenizer) -> Dataset:
    """Tokenize a dataset for FinBERT."""
    def tokenize_fn(batch):
        return tokenizer(batch["text"], truncation=True, max_length=512, padding="max_length")

    return dataset.map(tokenize_fn, batched=True, remove_columns=["text"])


def compute_metrics(eval_pred):
    """Compute F1 metrics for Trainer."""
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    macro_f1 = f1_score(labels, preds, average="macro")
    weighted_f1 = f1_score(labels, preds, average="weighted")
    return {"macro_f1": macro_f1, "weighted_f1": weighted_f1}


def finetune(
    data_paths: list[str],
    output_dir: str = "models/finbert-hinglish",
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-4,
    lora_r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.1,
    test_size: float = 0.15,
):
    """Full fine-tuning pipeline: load → split → tokenize → LoRA → train → evaluate → save."""
    # Load data
    records = load_labeled_data(data_paths)
    if len(records) < 50:
        logger.error(f"Only {len(records)} samples — need at least 50 for fine-tuning")
        return

    train_ds, test_ds = create_datasets(records, test_size=test_size)

    # Load model + tokenizer
    logger.info(f"Loading base model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=3
    )

    # Apply LoRA
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=lora_r,
        lora_alpha=lora_alpha,
        lora_dropout=lora_dropout,
        target_modules=["query", "value"],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Tokenize
    train_ds = tokenize_dataset(train_ds, tokenizer)
    test_ds = tokenize_dataset(test_ds, tokenizer)

    # Training args
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        logging_steps=10,
        report_to="none",
        fp16=torch.cuda.is_available(),
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        compute_metrics=compute_metrics,
    )

    # Train
    logger.info("Starting fine-tuning...")
    trainer.train()

    # Evaluate
    logger.info("Evaluating on test set...")
    results = trainer.evaluate()
    logger.info(f"Test results: {results}")

    # Detailed classification report
    preds_output = trainer.predict(test_ds)
    preds = np.argmax(preds_output.predictions, axis=-1)
    labels = preds_output.label_ids
    report = classification_report(
        labels, preds, target_names=list(LABEL_MAP.keys()), digits=4
    )
    logger.info(f"\nClassification Report:\n{report}")

    # Save
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    logger.info(f"Model saved to {output_path}")

    # Save report
    report_path = output_path / "eval_report.txt"
    with open(report_path, "w") as f:
        f.write(f"Test metrics: {results}\n\n")
        f.write(report)
    logger.info(f"Evaluation report saved to {report_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune FinBERT on Hinglish labeled data")
    parser.add_argument("--data", nargs="+", required=True, help="Path(s) to labeled JSONL files")
    parser.add_argument("--output", type=str, default="models/finbert-hinglish")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--test-size", type=float, default=0.15)
    args = parser.parse_args()

    finetune(
        data_paths=args.data,
        output_dir=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        test_size=args.test_size,
    )
