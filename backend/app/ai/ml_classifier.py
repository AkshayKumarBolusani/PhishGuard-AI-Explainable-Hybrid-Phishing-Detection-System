"""
PhishGuard AI — TF-IDF + Classical ML Classifier

Provides TF-IDF vectorization with Logistic Regression and Random Forest classifiers.
Includes feature importance extraction for explainability.
"""


import numpy as np
import structlog
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

LABEL_MAP = {0: "safe", 1: "suspicious", 2: "phishing"}
REVERSE_LABEL_MAP = {"safe": 0, "suspicious": 1, "phishing": 2}


class MLClassifier:
    """TF-IDF + classical ML classifier with explainability."""

    def __init__(self):
        self.settings = get_settings()
        self.model_dir = self.settings.model_save_path
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self.tfidf = TfidfVectorizer(
            max_features=10000, ngram_range=(1, 2), min_df=2, max_df=0.95,
            strip_accents="unicode", sublinear_tf=True,
        )
        self.lr_model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            C=1.0,
        )
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_leaf=2,
            class_weight="balanced",
            n_jobs=-1,
        )
        self.is_trained = False
        self._try_load()

    def _try_load(self) -> None:
        """Attempt to load pre-trained models from disk."""
        try:
            import joblib
            tfidf_path = self.model_dir / "tfidf_vectorizer.joblib"
            lr_path = self.model_dir / "lr_model.joblib"
            rf_path = self.model_dir / "rf_model.joblib"

            if tfidf_path.exists() and lr_path.exists():
                self.tfidf = joblib.load(tfidf_path)
                self.lr_model = joblib.load(lr_path)
                if rf_path.exists():
                    self.rf_model = joblib.load(rf_path)
                self.is_trained = True
                logger.info("ml_models_loaded")
        except Exception as e:
            logger.warning("ml_models_load_failed", error=str(e))

    def train(self, texts: list[str], labels: list[int]) -> dict:
        """Train both classifiers; evaluate with stratified k-fold CV, then fit on full data."""
        import joblib
        from sklearn.model_selection import StratifiedKFold, cross_val_score

        from app.ai.model_metrics import save_model_metrics

        logger.info("ml_training_started", samples=len(texts))

        X = self.tfidf.fit_transform(texts)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        lr_f1_scores = cross_val_score(self.lr_model, X, labels, cv=cv, scoring="f1_weighted")
        lr_acc_scores = cross_val_score(self.lr_model, X, labels, cv=cv, scoring="accuracy")
        rf_f1_scores = cross_val_score(self.rf_model, X, labels, cv=cv, scoring="f1_weighted")
        rf_acc_scores = cross_val_score(self.rf_model, X, labels, cv=cv, scoring="accuracy")

        self.lr_model.fit(X, labels)
        self.rf_model.fit(X, labels)
        self.is_trained = True

        joblib.dump(self.tfidf, self.model_dir / "tfidf_vectorizer.joblib")
        joblib.dump(self.lr_model, self.model_dir / "lr_model.joblib")
        joblib.dump(self.rf_model, self.model_dir / "rf_model.joblib")

        def _cv_stats(scores) -> dict[str, float]:
            return {
                "mean": round(float(scores.mean()), 3),
                "std": round(float(scores.std()), 3),
            }

        lr_f1 = _cv_stats(lr_f1_scores)
        lr_acc = _cv_stats(lr_acc_scores)
        rf_f1 = _cv_stats(rf_f1_scores)
        rf_acc = _cv_stats(rf_acc_scores)

        save_model_metrics({
            "dataset": {
                "samples": len(texts),
                "safe": labels.count(0),
                "suspicious": labels.count(1),
                "phishing": labels.count(2),
            },
            "evaluation": {
                "method": "stratified_k_fold",
                "folds": 5,
                "random_state": 42,
                "note": (
                    "Metrics are 5-fold cross-validation mean ± std on the 130-email demonstration dataset. "
                    "Models are trained on all samples after evaluation. "
                    "Intended for pipeline validation and architecture testing — not a production-trained model."
                ),
            },
            "models": {
                "logistic_regression": {
                    "f1_weighted": lr_f1["mean"],
                    "f1_std": lr_f1["std"],
                    "accuracy": lr_acc["mean"],
                    "accuracy_std": lr_acc["std"],
                    "vectorizer": "TF-IDF (10k features, bigrams)",
                },
                "random_forest": {
                    "f1_weighted": rf_f1["mean"],
                    "f1_std": rf_f1["std"],
                    "accuracy": rf_acc["mean"],
                    "accuracy_std": rf_acc["std"],
                    "estimators": 100,
                    "max_depth": 12,
                },
                "distilbert": {
                    "f1_weighted": None,
                    "status": "configurable",
                    "note": "Set USE_TRANSFORMER=true; requires additional training data and higher compute",
                },
            },
            "ensemble": {
                "method": "weighted_voting",
                "weights_without_transformer": {"rule_engine": 0.35, "ml_classifier": 0.65},
                "weights_with_transformer": {"rule_engine": 0.25, "ml_classifier": 0.35, "transformer": 0.40},
                "confidence_calibration": "probability normalization after weighted sum",
            },
        })

        report = {
            "logistic_regression": {"f1_weighted": lr_f1, "accuracy": lr_acc},
            "random_forest": {"f1_weighted": rf_f1, "accuracy": rf_acc},
            "cv_folds": 5,
        }
        logger.info(
            "ml_training_completed",
            lr_f1=f"{lr_f1['mean']}±{lr_f1['std']}",
            rf_f1=f"{rf_f1['mean']}±{rf_f1['std']}",
        )
        return report

    def predict(self, text: str) -> dict:
        """Predict classification with probabilities."""
        if not self.is_trained:
            return self._fallback_predict(text)

        X = self.tfidf.transform([text])
        lr_probs = self.lr_model.predict_proba(X)[0]
        rf_probs = self.rf_model.predict_proba(X)[0]

        # Ensemble average
        avg_probs = (lr_probs + rf_probs) / 2
        label_idx = int(np.argmax(avg_probs))

        return {
            "classification": LABEL_MAP[label_idx],
            "confidence": float(np.max(avg_probs)),
            "probabilities": {LABEL_MAP[i]: float(avg_probs[i]) for i in range(len(avg_probs))},
            "lr_probabilities": {LABEL_MAP[i]: float(lr_probs[i]) for i in range(len(lr_probs))},
            "rf_probabilities": {LABEL_MAP[i]: float(rf_probs[i]) for i in range(len(rf_probs))},
        }

    def get_feature_importance(self, text: str, top_n: int = 15) -> list[dict]:
        """Extract the most important features (words) driving the prediction."""
        if not self.is_trained:
            return []

        X = self.tfidf.transform([text])
        feature_names = self.tfidf.get_feature_names_out()

        # Use LR coefficients for the predicted class
        predicted_class = self.lr_model.predict(X)[0]
        if len(self.lr_model.classes_) > 2:
            coefficients = self.lr_model.coef_[predicted_class]
        else:
            coefficients = self.lr_model.coef_[0]

        # Get non-zero feature indices from the input
        nonzero_indices = X.nonzero()[1]
        feature_scores = []
        for idx in nonzero_indices:
            feature_scores.append({
                "feature": feature_names[idx],
                "tfidf_score": float(X[0, idx]),
                "coefficient": float(coefficients[idx]),
                "importance": float(abs(coefficients[idx]) * X[0, idx]),
            })

        feature_scores.sort(key=lambda x: x["importance"], reverse=True)
        return feature_scores[:top_n]

    def _fallback_predict(self, text: str) -> dict:
        """Simple keyword-based fallback when model is not trained."""
        text_lower = text.lower()
        phishing_keywords = [
            "urgent", "verify", "suspend", "click here", "password",
            "account", "security", "confirm", "unauthorized", "immediately",
            "gift card", "wire transfer", "bitcoin", "won", "lottery",
        ]
        matches = sum(1 for kw in phishing_keywords if kw in text_lower)
        ratio = min(1.0, matches / 5.0)

        if ratio > 0.6:
            return {"classification": "phishing", "confidence": 0.5 + ratio * 0.3,
                    "probabilities": {"safe": 0.1, "suspicious": 0.2, "phishing": 0.7}}
        elif ratio > 0.2:
            return {"classification": "suspicious", "confidence": 0.4 + ratio * 0.2,
                    "probabilities": {"safe": 0.25, "suspicious": 0.5, "phishing": 0.25}}
        else:
            return {"classification": "safe", "confidence": 0.7,
                    "probabilities": {"safe": 0.75, "suspicious": 0.2, "phishing": 0.05}}
