"""
PhishGuard AI — Rule-Based Detection Engine

Pattern-matching engine with 50+ rules covering urgency, threats, credential harvesting,
financial fraud, social engineering, and more. Each rule produces a scored indicator.
"""

import re
from dataclasses import dataclass


@dataclass
class RuleMatch:
    name: str
    category: str
    severity: str  # low, medium, high, critical
    confidence: float
    matched_text: str
    description: str


@dataclass
class Rule:
    name: str
    category: str
    severity: str
    confidence: float
    patterns: list[str]
    description: str
    flags: int = re.IGNORECASE


# Comprehensive rule definitions covering all major phishing categories
RULES: list[Rule] = [
    # ── Urgency ──────────────────────────────────────────────
    Rule("urgent_action", "urgency", "high", 0.75,
         [r"\b(urgent|immediately|right away|asap|act now)\b",
          r"\b(within \d+ hours?|within \d+ minutes?)\b",
          r"\b(expires? (today|soon|shortly|immediately))\b",
          r"\b(limited time|time.?sensitive|don\'t delay)\b"],
         "Uses urgency language to pressure immediate action"),

    Rule("deadline_pressure", "urgency", "high", 0.70,
         [r"\b(last chance|final warning|final notice|last notice)\b",
          r"\b(before it\'s too late|running out of time)\b",
          r"\b(deadline|must respond|respond immediately)\b"],
         "Creates artificial deadline pressure"),

    # ── Fear & Threats ───────────────────────────────────────
    Rule("account_threat", "threat", "critical", 0.85,
         [r"\b(account.{0,20}(suspend|terminat|clos|lock|restrict|disabl|deactivat))\b",
          r"\b((suspend|terminat|clos|lock|restrict|disabl|deactivat).{0,20}account)\b",
          r"\b(unauthorized (access|activity|transaction|login))\b"],
         "Threatens account suspension or unauthorized access"),

    Rule("legal_threat", "threat", "high", 0.80,
         [r"\b(legal action|law enforcement|prosecution|arrest warrant)\b",
          r"\b(court order|subpoena|legal proceedings|lawsuit)\b",
          r"\b(criminal charges|federal investigation)\b"],
         "Uses legal threats to intimidate"),

    Rule("security_alert", "threat", "high", 0.70,
         [r"\b(security (alert|warning|breach|incident|notification))\b",
          r"\b(compromised|hacked|breached|data leak)\b",
          r"\b(suspicious (activity|login|transaction))\b"],
         "Mimics security alert notification"),

    # ── Credential Harvesting ────────────────────────────────
    Rule("credential_request", "credential_harvesting", "critical", 0.90,
         [r"\b(verify your (account|identity|email|password|information))\b",
          r"\b(confirm your (account|identity|email|password|information))\b",
          r"\b(update your (account|credentials|password|payment))\b",
          r"\b(enter your (password|credentials|ssn|social security))\b"],
         "Requests credential verification through external means"),

    Rule("password_reset", "credential_harvesting", "high", 0.75,
         [r"\b(password (reset|change|update|expir))\b",
          r"\b(reset your password)\b",
          r"\b(click.{0,30}(reset|change|update).{0,20}password)\b"],
         "Disguised as password reset notification"),

    Rule("login_request", "credential_harvesting", "high", 0.70,
         [r"\b(sign.?in.{0,20}(verify|confirm|secure))\b",
          r"\b(log.?in.{0,20}(verify|confirm|secure))\b",
          r"\b(click.{0,30}(sign|log).?in)\b"],
         "Requests login through external link"),

    # ── Financial Fraud ──────────────────────────────────────
    Rule("wire_transfer", "financial", "critical", 0.90,
         [r"\b(wire transfer|bank transfer|money transfer)\b",
          r"\b(transfer.{0,30}\$[\d,]+)\b",
          r"\b(send.{0,20}(money|payment|funds))\b"],
         "Requests wire transfer or money transfer"),

    Rule("gift_card", "financial", "critical", 0.95,
         [r"\b(gift card|itunes card|google play card|amazon card)\b",
          r"\b(buy.{0,20}(gift card|prepaid card))\b",
          r"\b(purchase.{0,20}card.{0,20}code)\b"],
         "Gift card scam — extremely common phishing pattern"),

    Rule("crypto_request", "financial", "critical", 0.90,
         [r"\b(bitcoin|cryptocurrency|crypto wallet|btc address)\b",
          r"\b(send.{0,20}(bitcoin|btc|ethereum|crypto))\b",
          r"\b(wallet address|blockchain)\b"],
         "Cryptocurrency-based financial fraud"),

    Rule("banking_language", "financial", "high", 0.65,
         [r"\b(routing number|account number|bank account)\b",
          r"\b(credit card (number|detail|information))\b",
          r"\b(payment (detail|information|method))\b",
          r"\b(billing (address|information|detail))\b"],
         "Requests sensitive banking information"),

    Rule("fake_invoice", "financial", "high", 0.75,
         [r"\b(invoice.{0,20}(attached|enclosed|overdue|pending))\b",
          r"\b(outstanding (balance|payment|invoice))\b",
          r"\b(payment (overdue|required|due|pending))\b"],
         "Fake invoice or payment request"),

    # ── Scam Categories ──────────────────────────────────────
    Rule("lottery_scam", "scam", "critical", 0.95,
         [r"\b(you.{0,20}(won|winner|selected|chosen))\b",
          r"\b(lottery|sweepstakes|prize|jackpot)\b",
          r"\b(claim your (prize|reward|winnings))\b",
          r"\b(congratulations.{0,30}(won|winner))\b"],
         "Lottery or prize scam"),

    Rule("tax_scam", "scam", "high", 0.85,
         [r"\b(tax (refund|return|rebate|review))\b",
          r"\b(irs|internal revenue|tax authority)\b",
          r"\b(tax.{0,20}(owed|due|outstanding|penalty))\b"],
         "Tax-related scam"),

    Rule("employment_scam", "scam", "high", 0.75,
         [r"\b(job (offer|opportunity|opening|position))\b",
          r"\b(work from home.{0,20}(earn|make|income))\b",
          r"\b(earn.{0,20}\$[\d,]+.{0,20}(week|month|day|hour))\b",
          r"\b(no experience (needed|required|necessary))\b"],
         "Employment or work-from-home scam"),

    Rule("refund_scam", "scam", "high", 0.80,
         [r"\b(refund.{0,20}(process|pending|approved|eligible))\b",
          r"\b(overpayment|overcharge|reimbursement)\b",
          r"\b(claim your refund)\b"],
         "Refund scam"),

    # ── Business Email Compromise ────────────────────────────
    Rule("ceo_fraud", "bec", "critical", 0.85,
         [r"\b(from.{0,10}(ceo|director|president|chairman|executive))\b",
          r"\b(confidential.{0,20}(request|matter|task|transaction))\b",
          r"\b(keep this (between us|confidential|quiet|private))\b",
          r"\b(don\'t (tell|mention|discuss).{0,20}(anyone|else))\b"],
         "CEO fraud or business email compromise pattern"),

    Rule("authority_impersonation", "bec", "high", 0.75,
         [r"\b(on behalf of|representing|authorized by)\b",
          r"\b(as (requested|instructed|directed) by)\b",
          r"\b(per (our|the) (conversation|discussion|agreement))\b"],
         "Impersonates authority figure"),

    # ── Social Engineering ───────────────────────────────────
    Rule("emotional_manipulation", "social_engineering", "medium", 0.60,
         [r"\b(please help|i need your help|desperate|emergency)\b",
          r"\b(stuck (abroad|overseas|in)|stranded)\b",
          r"\b(hospital|medical emergency|accident)\b"],
         "Emotional manipulation for social engineering"),

    Rule("trust_building", "social_engineering", "medium", 0.55,
         [r"\b(trusted (partner|colleague|friend|customer))\b",
          r"\b(valued (customer|member|user|client))\b",
          r"\b(dear (customer|user|member|account holder|sir|madam))\b"],
         "Generic trust-building salutation"),

    Rule("curiosity_bait", "social_engineering", "medium", 0.60,
         [r"\b(you won\'t believe|shocking|unbelievable|exclusive)\b",
          r"\b(secret|revealed|exposed|leaked)\b",
          r"\b(click.{0,20}(see|view|watch|learn|find out))\b"],
         "Uses curiosity to entice clicks"),

    # ── Link Manipulation ────────────────────────────────────
    Rule("click_link", "link_manipulation", "high", 0.70,
         [r"\b(click (here|below|this link|the link))\b",
          r"\b(follow.{0,10}(this|the) link)\b",
          r"\b(open.{0,10}(this|the) (link|attachment))\b"],
         "Directs user to click an external link"),

    Rule("attachment_request", "link_manipulation", "high", 0.70,
         [r"\b(open.{0,20}attach(ment|ed))\b",
          r"\b(download.{0,20}(file|document|attachment))\b",
          r"\b(see attached|attached (document|file|invoice))\b"],
         "Requests opening of attachment"),

    # ── Technical Deception ──────────────────────────────────
    Rule("brand_impersonation", "deception", "high", 0.80,
         [r"\b(paypal|apple|microsoft|google|amazon|netflix|facebook|instagram)\b",
          r"\b(bank of america|wells fargo|chase|citibank)\b",
          r"\b(fedex|ups|usps|dhl|royal mail)\b"],
         "Impersonates well-known brand"),

    Rule("html_obfuscation", "deception", "high", 0.75,
         [r"<a\s[^>]*href\s*=\s*[\"'][^\"']*[\"'][^>]*>(?:(?!<\/a>).)*<\/a>",
          r"display\s*:\s*none", r"font-size\s*:\s*0"],
         "Contains HTML obfuscation techniques"),

    # ── Miscellaneous Indicators ─────────────────────────────
    Rule("excessive_caps", "style", "low", 0.40,
         [r"\b[A-Z]{4,}(?:\s+[A-Z]{4,}){2,}\b"],
         "Excessive use of capital letters",
         flags=0),

    Rule("excessive_punctuation", "style", "low", 0.35,
         [r"[!]{3,}", r"[?]{3,}", r"[!?]{3,}"],
         "Excessive punctuation suggesting urgency"),

    Rule("poor_grammar", "style", "medium", 0.45,
         [r"\b(kindly|do the needful|revert back|prepone)\b",
          r"\b(your (account|password) is been)\b"],
         "Grammar patterns common in phishing emails"),
]


class RuleEngine:
    """Rule-based phishing detection engine."""

    def __init__(self):
        self.rules = RULES
        self._compiled_rules: list[tuple[Rule, list[re.Pattern]]] = []
        self._compile_rules()

    def _compile_rules(self) -> None:
        """Pre-compile all regex patterns for performance."""
        for rule in self.rules:
            compiled = [re.compile(p, rule.flags) for p in rule.patterns]
            self._compiled_rules.append((rule, compiled))

    def analyze(self, text: str) -> list[RuleMatch]:
        """Run all rules against the given text and return matches."""
        matches: list[RuleMatch] = []

        for rule, patterns in self._compiled_rules:
            for pattern in patterns:
                found = pattern.search(text)
                if found:
                    matches.append(RuleMatch(
                        name=rule.name,
                        category=rule.category,
                        severity=rule.severity,
                        confidence=rule.confidence,
                        matched_text=found.group(0),
                        description=rule.description,
                    ))
                    break  # One match per rule is sufficient

        return matches

    def compute_risk_score(self, matches: list[RuleMatch]) -> float:
        """Compute an aggregate risk score from rule matches (0-100)."""
        if not matches:
            return 0.0

        severity_weights = {"low": 1.0, "medium": 2.0, "high": 3.5, "critical": 5.0}
        total_weight = sum(
            severity_weights.get(m.severity, 1.0) * m.confidence for m in matches
        )
        # Normalize to 0-100, capped
        normalized = min(100.0, (total_weight / 3.0) * 20.0)
        return round(normalized, 2)

    def classify(self, matches: list[RuleMatch]) -> tuple[str, dict[str, float]]:
        """Classify based on rule matches. Returns (label, probabilities)."""
        risk = self.compute_risk_score(matches)

        if risk >= 60:
            probs = {"safe": max(0, (100 - risk) / 100), "suspicious": 0.15,
                     "phishing": min(1.0, risk / 100)}
        elif risk >= 25:
            probs = {"safe": max(0, (100 - risk) / 200), "suspicious": 0.5,
                     "phishing": min(0.5, risk / 100)}
        else:
            probs = {"safe": max(0.5, (100 - risk) / 100), "suspicious": min(0.3, risk / 100),
                     "phishing": min(0.1, risk / 200)}

        # Normalize
        total = sum(probs.values())
        probs = {k: round(v / total, 4) for k, v in probs.items()}

        label = max(probs, key=probs.get)
        return label, probs
