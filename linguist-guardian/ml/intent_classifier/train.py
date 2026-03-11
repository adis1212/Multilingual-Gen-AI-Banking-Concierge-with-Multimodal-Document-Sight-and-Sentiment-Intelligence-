"""
Intent Classifier — Train a lightweight scikit-learn model for banking intent classification.
Uses TF-IDF + SVM as a fast fallback when GPT-4o is unavailable or for pre-filtering.
"""
import json
from pathlib import Path
from typing import Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import LinearSVC
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import cross_val_score
    import joblib
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

LABELS_PATH = Path(__file__).parent / "labels.json"
MODEL_PATH  = Path(__file__).parent / "intent_model.pkl"

_pipeline = None


def load_labels() -> dict:
    """Load intent labels and training samples."""
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def train(save: bool = True) -> dict:
    """
    Train an intent classification model.

    Returns:
        dict with keys: accuracy, num_samples, labels
    """
    if not HAS_SKLEARN:
        raise ImportError("scikit-learn is required. Install via: pip install scikit-learn")

    data = load_labels()
    samples = data.get("training_samples", [])

    if len(samples) < 5:
        raise ValueError(f"Need at least 5 training samples, got {len(samples)}")

    texts  = [s["text"]  for s in samples]
    labels = [s["label"] for s in samples]

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 5),
            max_features=5000,
            sublinear_tf=True,
        )),
        ("svm", LinearSVC(
            max_iter=2000,
            C=1.0,
            class_weight="balanced",
        )),
    ])

    # Cross-validation
    scores = cross_val_score(pipeline, texts, labels, cv=min(3, len(set(labels))), scoring="accuracy")
    mean_accuracy = float(scores.mean())

    # Train on full data
    pipeline.fit(texts, labels)

    if save:
        joblib.dump(pipeline, MODEL_PATH)
        print(f"✅ Intent model saved to {MODEL_PATH}")

    global _pipeline
    _pipeline = pipeline

    return {
        "accuracy": round(mean_accuracy, 3),
        "num_samples": len(samples),
        "labels": list(set(labels)),
        "model_path": str(MODEL_PATH) if save else None,
    }


def predict(text: str) -> dict:
    """
    Predict the intent of a given text.

    Returns:
        dict with keys: intent, confidence
    """
    global _pipeline

    if _pipeline is None:
        if MODEL_PATH.exists() and HAS_SKLEARN:
            _pipeline = joblib.load(MODEL_PATH)
        else:
            return {"intent": "other", "confidence": 0.0, "source": "fallback"}

    intent = _pipeline.predict([text])[0]

    # Get decision function scores for confidence estimate
    try:
        scores = _pipeline.decision_function([text])[0]
        if hasattr(scores, "__len__"):
            max_score = float(max(scores))
            confidence = min(1.0, max(0.0, (max_score + 1) / 2))
        else:
            confidence = min(1.0, max(0.0, (float(scores) + 1) / 2))
    except Exception:
        confidence = 0.5

    return {
        "intent": intent,
        "confidence": round(confidence, 3),
        "source": "ml_model",
    }


if __name__ == "__main__":
    print("🚀 Training intent classifier...")
    result = train()
    print(f"✅ Done! Accuracy: {result['accuracy']:.1%}")
    print(f"   Samples: {result['num_samples']}, Labels: {result['labels']}")

    # Quick test
    test_cases = [
        "I lost my credit card",
        "what is my balance",
        "I want a home loan",
        "KYC documents update",
    ]
    for t in test_cases:
        pred = predict(t)
        print(f"   '{t}' → {pred['intent']} ({pred['confidence']:.0%})")
