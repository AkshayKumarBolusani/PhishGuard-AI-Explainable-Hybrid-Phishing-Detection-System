"""
PhishGuard AI — Transformer-Based Classifier

Uses DistilBERT (or optionally RoBERTa/DeBERTa) for deep semantic classification.
Gracefully falls back to ML classifier if transformers are not installed.
"""

import structlog
from app.core.config import get_settings

logger = structlog.get_logger(__name__)


class TransformerClassifier:
    """Transformer-based email classifier with optional GPU support."""

    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self.tokenizer = None
        self.is_available = False
        self.model_name = self.settings.transformer_model_name

        if self.settings.use_transformer:
            self._try_load()

    def _try_load(self) -> None:
        """Attempt to load transformer model."""
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            import torch

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name, num_labels=3,
                id2label={0: "safe", 1: "suspicious", 2: "phishing"},
                label2id={"safe": 0, "suspicious": 1, "phishing": 2},
            )
            self.model.eval()
            self.is_available = True
            logger.info("transformer_loaded", model=self.model_name)
        except ImportError:
            logger.info("transformers_not_installed", msg="Using ML classifier fallback")
        except Exception as e:
            logger.warning("transformer_load_failed", error=str(e))

    def predict(self, text: str) -> dict:
        """Predict using transformer model or return empty result."""
        if not self.is_available:
            return self._unavailable_result()

        try:
            import torch

            inputs = self.tokenizer(
                text, return_tensors="pt", truncation=True,
                max_length=512, padding=True,
            )
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

            label_map = {0: "safe", 1: "suspicious", 2: "phishing"}
            probs_dict = {label_map[i]: float(probs[i]) for i in range(3)}
            predicted_idx = int(torch.argmax(probs))

            return {
                "classification": label_map[predicted_idx],
                "confidence": float(probs[predicted_idx]),
                "probabilities": probs_dict,
            }
        except Exception as e:
            logger.error("transformer_prediction_failed", error=str(e))
            return self._unavailable_result()

    def _unavailable_result(self) -> dict:
        """Return a result indicating the transformer is not available."""
        return {
            "classification": "unknown",
            "confidence": 0.0,
            "probabilities": {"safe": 0.33, "suspicious": 0.33, "phishing": 0.34},
            "available": False,
        }

    @property
    def status(self) -> str:
        return "loaded" if self.is_available else "not_available"
