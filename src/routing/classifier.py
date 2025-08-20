# classifier.py - document type detection
from transformers import pipeline
import torch

# ✅ Pick device: try GPU (cuda:0), else CPU (-1)
device = 0 if torch.cuda.is_available() else -1

# ✅ Safe loading with fallback
try:
    _classifier = pipeline(
        "zero-shot-classification",
        model="typeform/distilbert-base-uncased-mnli",
        device=device
    )
except RuntimeError as e:
    print("⚠️ CUDA OOM detected, falling back to CPU...")
    _classifier = pipeline(
        "zero-shot-classification",
        model="valhalla/distilbart-mnli-12-1",
        device=-1  # force CPU
    )

def classify_doc(text: str) -> str:
    """Return one of several broad document types."""
    labels = [
        "invoice",
        "bill",
        "prescription",
        "resume",
        "id card",
        "contract",
        "letter",
        "other"
    ]
    # Truncate long text to avoid memory issues
    sample = text[:800]
    res = _classifier(sample, candidate_labels=labels)
    return res["labels"][0]
