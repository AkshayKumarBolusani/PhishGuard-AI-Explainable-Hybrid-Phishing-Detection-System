"""
PhishGuard AI — Model Training Script

Trains TF-IDF + ML classifiers on seed data and produces evaluation metrics.
Run: python -m app.ai.models.train
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.ai.ml_classifier import MLClassifier
from app.ai.models.seed_data import get_seed_data


def train_models():
    """Train ML models on seed data and print evaluation report."""
    print("=" * 60)
    print("PhishGuard AI — Model Training")
    print("=" * 60)

    texts, labels = get_seed_data()
    print(f"\nTraining data: {len(texts)} samples")
    print(f"  Safe: {labels.count(0)}")
    print(f"  Suspicious: {labels.count(1)}")
    print(f"  Phishing: {labels.count(2)}")

    classifier = MLClassifier()
    report = classifier.train(texts, labels)

    print("\n" + "─" * 60)
    print("5-Fold Stratified Cross-Validation (mean ± std):")
    print("─" * 60)
    for model in ("logistic_regression", "random_forest"):
        f1 = report[model]["f1_weighted"]
        acc = report[model]["accuracy"]
        print(f"  {model.replace('_', ' ').title():22} — F1: {f1['mean']:.3f} ± {f1['std']:.3f}  "
              f"Accuracy: {acc['mean']:.3f} ± {acc['std']:.3f}")
    print("─" * 60)
    print("\nMetrics saved to:", classifier.model_dir / "model_metrics.json")
    print("Training complete!")

    return report


if __name__ == "__main__":
    train_models()
