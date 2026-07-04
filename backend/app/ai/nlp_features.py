"""
PhishGuard AI — NLP Feature Extraction

Extracts linguistic features using spaCy and TextBlob: named entities, sentiment,
urgency score, readability, action verbs, imperative language detection.
"""

import re
import math
import structlog

logger = structlog.get_logger(__name__)

# Attempt to load spaCy — graceful fallback if not available
_nlp = None
def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            try:
                _nlp = spacy.load("en_core_web_sm")
            except OSError:
                _nlp = spacy.blank("en")
                logger.info("spacy_model_not_found", msg="Using blank English model")
        except ImportError:
            logger.info("spacy_not_installed")
            _nlp = False
    return _nlp


URGENCY_WORDS = {
    "immediately", "urgent", "urgently", "asap", "now", "today", "hurry",
    "quickly", "fast", "rush", "deadline", "expire", "expiring", "expires",
    "limited", "final", "last", "warning", "alert", "critical", "important",
    "action required", "time sensitive", "don't delay", "act now",
}

ACTION_VERBS = {
    "click", "verify", "confirm", "update", "validate", "submit", "enter",
    "provide", "download", "open", "send", "transfer", "pay", "purchase",
    "buy", "call", "contact", "reply", "respond", "forward", "share",
    "sign", "login", "log in", "register", "activate", "enable", "reset",
}

IMPERATIVE_STARTERS = {
    "click", "verify", "confirm", "update", "enter", "provide", "download",
    "open", "send", "call", "contact", "reply", "submit", "forward",
    "do not", "don't", "please", "kindly", "ensure", "make sure",
}


class NLPFeatureExtractor:
    """Extracts NLP features from email text."""

    def extract(self, text: str) -> dict:
        """Extract all NLP features from the given text."""
        nlp = _get_nlp()

        entities = self._extract_entities(text, nlp)
        action_verbs = self._find_action_verbs(text)
        imperatives = self._find_imperative_sentences(text)
        sentiment = self._analyze_sentiment(text)
        urgency = self._compute_urgency_score(text)
        readability = self._compute_readability(text)
        emotion = self._detect_emotion(text)

        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

        return {
            "entities": entities,
            "action_verbs": action_verbs,
            "imperative_sentences": imperatives[:10],
            "sentiment": sentiment,
            "urgency_score": urgency,
            "readability_score": readability,
            "emotion": emotion,
            "word_count": len(words),
            "sentence_count": len(sentences),
        }

    def _extract_entities(self, text: str, nlp) -> dict[str, list[str]]:
        """Extract named entities grouped by type."""
        entities: dict[str, list[str]] = {
            "organizations": [], "people": [], "money": [],
            "dates": [], "locations": [], "emails": [],
            "phone_numbers": [], "urls": [],
        }

        # Regex-based extraction (always works)
        email_pattern = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
        entities["emails"] = list(set(email_pattern.findall(text)))

        phone_pattern = re.compile(r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,15}')
        entities["phone_numbers"] = list(set(phone_pattern.findall(text)))[:5]

        url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
        entities["urls"] = list(set(url_pattern.findall(text)))

        # spaCy NER
        if nlp and nlp is not False:
            try:
                doc = nlp(text[:5000])  # Limit length for performance
                for ent in doc.ents:
                    if ent.label_ == "ORG":
                        entities["organizations"].append(ent.text)
                    elif ent.label_ == "PERSON":
                        entities["people"].append(ent.text)
                    elif ent.label_ in ("MONEY", "CARDINAL"):
                        if "$" in ent.text or any(c.isdigit() for c in ent.text):
                            entities["money"].append(ent.text)
                    elif ent.label_ == "DATE":
                        entities["dates"].append(ent.text)
                    elif ent.label_ in ("GPE", "LOC"):
                        entities["locations"].append(ent.text)
            except Exception as e:
                logger.warning("ner_extraction_failed", error=str(e))

        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))[:10]

        return entities

    def _find_action_verbs(self, text: str) -> list[str]:
        """Find action verbs commonly used in phishing."""
        text_lower = text.lower()
        found = [verb for verb in ACTION_VERBS if verb in text_lower]
        return sorted(set(found))

    def _find_imperative_sentences(self, text: str) -> list[str]:
        """Find sentences that start with imperative verbs."""
        sentences = [s.strip() for s in re.split(r'[.!?\n]+', text) if s.strip()]
        imperatives = []
        for sentence in sentences:
            first_word = sentence.split()[0].lower() if sentence.split() else ""
            if first_word in IMPERATIVE_STARTERS:
                imperatives.append(sentence[:150])
        return imperatives

    def _analyze_sentiment(self, text: str) -> dict[str, float]:
        """Analyze sentiment polarity and subjectivity."""
        try:
            from textblob import TextBlob
            blob = TextBlob(text[:3000])
            return {
                "polarity": round(blob.sentiment.polarity, 4),
                "subjectivity": round(blob.sentiment.subjectivity, 4),
            }
        except ImportError:
            return {"polarity": 0.0, "subjectivity": 0.0}

    def _compute_urgency_score(self, text: str) -> float:
        """Compute urgency score based on urgency keyword density."""
        text_lower = text.lower()
        words = text_lower.split()
        if not words:
            return 0.0

        urgency_count = sum(1 for w in URGENCY_WORDS if w in text_lower)
        score = min(1.0, urgency_count / 5.0)  # Normalize
        return round(score, 4)

    def _compute_readability(self, text: str) -> float:
        """Compute Flesch-Kincaid readability score."""
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        if not sentences or not words:
            return 0.0

        syllable_count = sum(self._count_syllables(w) for w in words)
        avg_sentence_len = len(words) / len(sentences)
        avg_syllables = syllable_count / len(words)

        # Flesch Reading Ease
        score = 206.835 - (1.015 * avg_sentence_len) - (84.6 * avg_syllables)
        return round(max(0, min(100, score)), 2)

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower().strip(".,!?;:'\"")
        if len(word) <= 3:
            return 1
        vowels = "aeiouy"
        count = 0
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if word.endswith("e"):
            count = max(1, count - 1)
        return max(1, count)

    def _detect_emotion(self, text: str) -> str:
        """Simple rule-based emotion detection."""
        text_lower = text.lower()
        fear_words = {"afraid", "scared", "threat", "danger", "warning", "risk", "suspend", "terminate", "locked"}
        anger_words = {"angry", "furious", "complaint", "unacceptable", "fraud"}
        joy_words = {"congratulations", "winner", "prize", "reward", "free", "bonus"}
        trust_words = {"trusted", "verified", "official", "secure", "legitimate"}

        scores = {
            "fear": sum(1 for w in fear_words if w in text_lower),
            "anger": sum(1 for w in anger_words if w in text_lower),
            "joy": sum(1 for w in joy_words if w in text_lower),
            "trust": sum(1 for w in trust_words if w in text_lower),
        }

        max_emotion = max(scores, key=scores.get)
        if scores[max_emotion] == 0:
            return "neutral"
        return max_emotion
