"""
PhishGuard AI — Suspicious Text Highlighter

Identifies and marks suspicious phrases with character offsets for frontend rendering.
"""

import re


HIGHLIGHT_PATTERNS = {
    "urgency": [
        r"\b(urgent|immediately|right away|act now|asap|hurry|quickly)\b",
        r"\b(within \d+ hours?|within \d+ minutes?|expires? (today|soon))\b",
        r"\b(last chance|final warning|don\'t delay|time.?sensitive)\b",
    ],
    "threat": [
        r"\b(suspend|terminat|clos|lock|restrict|disabl|deactivat)\w*\b",
        r"\b(unauthorized|compromised|breached|hacked|violation)\b",
        r"\b(legal action|law enforcement|prosecution)\b",
    ],
    "credential_request": [
        r"\b(verify your (account|identity|password|information))\b",
        r"\b(confirm your (account|identity|email|password))\b",
        r"\b(update your (account|credentials|password|payment))\b",
        r"\b(enter your (password|credentials|ssn))\b",
    ],
    "financial": [
        r"\b(wire transfer|bank transfer|gift card|bitcoin|cryptocurrency)\b",
        r"\$[\d,]+(\.\d{2})?\b",
        r"\b(payment|invoice|billing|routing number|account number)\b",
    ],
    "fake_offer": [
        r"\b(you (won|have won|are the winner|have been selected))\b",
        r"\b(lottery|sweepstakes|prize|jackpot|reward|free gift)\b",
        r"\b(congratulations)\b",
    ],
    "link": [
        r"\b(click (here|below|this link|the link))\b",
        r"\b(follow.{0,10}link|open.{0,10}link)\b",
        r"https?://[^\s<>\"]+",
    ],
    "scam": [
        r"\b(tax refund|irs|inheritance|prince|beneficiary)\b",
        r"\b(work from home.{0,20}earn|no experience needed)\b",
        r"\b(claim your|redeem your|collect your)\b",
    ],
}


class TextHighlighter:
    """Identifies suspicious text spans for frontend highlighting."""

    def __init__(self):
        self._compiled: dict[str, list[re.Pattern]] = {}
        for category, patterns in HIGHLIGHT_PATTERNS.items():
            self._compiled[category] = [re.compile(p, re.IGNORECASE) for p in patterns]

    def highlight(self, text: str) -> list[dict]:
        """Find all suspicious spans in the text."""
        highlights = []
        seen_ranges = set()

        severity_map = {
            "urgency": "high", "threat": "critical", "credential_request": "critical",
            "financial": "critical", "fake_offer": "high", "link": "medium", "scam": "high",
        }

        for category, patterns in self._compiled.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    start, end = match.start(), match.end()
                    # Avoid overlapping highlights
                    range_key = (start, end)
                    if range_key not in seen_ranges:
                        seen_ranges.add(range_key)
                        highlights.append({
                            "start": start,
                            "end": end,
                            "text": match.group(0),
                            "category": category,
                            "severity": severity_map.get(category, "medium"),
                        })

        highlights.sort(key=lambda h: h["start"])
        return highlights
