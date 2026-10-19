"""
PhishGuard AI — LLM Explanation Generator

Generates security analyst-style explanations using an OpenAI-compatible LLM API.
Includes a sophisticated template-based mock fallback for offline operation.
"""

import json
from typing import Any

import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a senior cybersecurity analyst at a Security Operations Center (SOC).
Your task is to analyze an email and provide a detailed security assessment.

You must respond ONLY with valid JSON matching this exact schema:
{
    "executive_summary": "2-3 sentence summary of the threat assessment",
    "risk_level": "one of: critical, high, medium, low, safe",
    "threat_indicators": ["list of specific indicators found"],
    "evidence": [{"indicator": "name", "detail": "specific evidence from the email"}],
    "attack_type": "the type of attack (phishing, spear_phishing, bec, credential_harvesting, etc.)",
    "likely_goal": "what the attacker is trying to achieve",
    "recommended_actions": ["list of specific actions the user should take"],
    "user_advice": "plain-language advice for the end user",
    "security_score": 0-100 (100 being safest),
    "technical_notes": "any technical observations about the email"
}

Reference SPECIFIC text from the email in your evidence. Do not be generic."""


class LLMExplainer:
    """LLM-powered explanation generator with mock fallback."""

    def __init__(self):
        self.settings = get_settings()
        self.is_available = False
        self.client = None

        if self.settings.llm_provider != "mock" and self.settings.llm_api_key:
            self._init_client()

    def _init_client(self) -> None:
        """Initialize the OpenAI-compatible client."""
        try:
            self.is_available = True
            logger.info("llm_client_initialized", provider=self.settings.llm_provider)
        except Exception as e:
            logger.warning("llm_init_failed", error=str(e))

    async def generate_report(
        self, email_text: str, indicators: list[dict], classification: str,
        sender_info: dict | None = None, url_info: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Generate a security report. Uses real LLM or mock fallback."""
        if self.is_available and self.settings.llm_provider != "mock":
            return await self._llm_report(email_text, indicators, classification)
        return self._mock_report(email_text, indicators, classification, sender_info, url_info)

    async def _llm_report(self, email_text: str, indicators: list[dict], classification: str) -> dict:
        """Call the real LLM API."""
        try:
            import httpx

            # Sanitize input to prevent prompt injection
            sanitized_email = email_text[:3000].replace("```", "").replace("{{", "").replace("}}", "")
            indicator_summary = ", ".join([i.get("name", "") for i in indicators[:15]])

            user_prompt = f"""Analyze this email. Pre-classified as: {classification}
Detected indicators: {indicator_summary}

EMAIL CONTENT:
---
{sanitized_email}
---

Provide your JSON security assessment."""

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.settings.llm_base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.llm_api_key}",
                             "Content-Type": "application/json"},
                    json={
                        "model": self.settings.llm_model,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": self.settings.llm_temperature,
                        "max_tokens": self.settings.llm_max_tokens,
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # Parse JSON from response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                return json.loads(content.strip())

        except Exception as e:
            logger.error("llm_report_failed", error=str(e))
            return self._mock_report(email_text, indicators, classification)

    def _mock_report(
        self, email_text: str, indicators: list[dict], classification: str,
        sender_info: dict | None = None, url_info: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Generate a sophisticated template-based report using detected indicators."""

        # Build evidence from actual indicators
        evidence = []
        threat_indicators = []
        for ind in indicators:
            name = ind.get("name", "unknown")
            matched = ind.get("matched_text", "")
            desc = ind.get("description", "")
            threat_indicators.append(f"{name}: {desc}")
            if matched:
                evidence.append({"indicator": name, "detail": f'Found "{matched}" in the email'})

        # Analyze sender
        sender_issues = []
        if sender_info:
            if sender_info.get("is_typosquatting"):
                sender_issues.append(f"Sender domain appears to be typosquatting: {sender_info.get('domain', '')}")
            if sender_info.get("is_free_provider"):
                sender_issues.append("Email sent from a free email provider")
            if sender_info.get("is_display_name_mismatch"):
                sender_issues.append("Display name does not match the email address")

        # Analyze URLs
        url_issues = []
        if url_info:
            for url in url_info:
                reasons = url.get("reasons", [])
                if reasons:
                    url_issues.append(f"Suspicious URL: {url.get('original_url', '')[:80]} ({', '.join(reasons)})")

        # Build summary based on classification
        categories = list({ind.get("category", "") for ind in indicators})
        cat_str = ", ".join(categories[:3]) if categories else "general"

        if classification == "phishing":
            summary = f"This email exhibits strong phishing characteristics with indicators in {cat_str} categories. "
            if evidence:
                summary += f'The most concerning element is the use of "{evidence[0].get("detail", "")}" '
                summary += "which is a common tactic used to deceive recipients into revealing sensitive information."
            risk_level = "critical" if len(indicators) > 5 else "high"
            score = max(5, 30 - len(indicators) * 3)
            attack_type = self._determine_attack_type(indicators)
            goal = self._determine_goal(indicators)
        elif classification == "suspicious":
            summary = f"This email contains some suspicious elements in {cat_str} categories that warrant caution. "
            summary += "While not conclusively phishing, several indicators suggest potential social engineering."
            risk_level = "medium"
            score = max(30, 60 - len(indicators) * 5)
            attack_type = "potential_" + self._determine_attack_type(indicators)
            goal = "Possibly " + self._determine_goal(indicators).lower()
        else:
            summary = "This email appears to be legitimate. No significant phishing indicators were detected."
            risk_level = "safe"
            score = min(95, 85 + len(indicators))
            attack_type = "none"
            goal = "Legitimate communication"

        # Build recommended actions
        actions = self._build_recommendations(classification, indicators, url_info)

        # Build user advice
        if classification == "phishing":
            advice = "Do NOT click any links, download attachments, or reply to this email. Report it to your IT security team immediately. If you've already interacted with it, change your passwords and monitor your accounts."
        elif classification == "suspicious":
            advice = "Exercise caution with this email. Verify the sender through a separate communication channel before taking any requested action. Do not click links without verifying their destination."
        else:
            advice = "This email appears safe, but always remain vigilant. Verify unexpected requests through alternative channels."

        return {
            "executive_summary": summary,
            "risk_level": risk_level,
            "threat_indicators": threat_indicators[:10],
            "evidence": evidence[:8],
            "attack_type": attack_type,
            "likely_goal": goal,
            "recommended_actions": actions,
            "user_advice": advice,
            "security_score": score,
            "technical_notes": self._build_technical_notes(sender_issues, url_issues),
        }

    def _determine_attack_type(self, indicators: list[dict]) -> str:
        categories = [i.get("category", "") for i in indicators]
        if "credential_harvesting" in categories:
            return "credential_harvesting"
        if "bec" in categories:
            return "business_email_compromise"
        if "financial" in categories:
            return "financial_fraud"
        if "scam" in categories:
            return "scam"
        return "phishing"

    def _determine_goal(self, indicators: list[dict]) -> str:
        categories = [i.get("category", "") for i in indicators]
        if "credential_harvesting" in categories:
            return "Steal user credentials (username/password) for account takeover"
        if "financial" in categories:
            return "Extract money through fraudulent financial transactions"
        if "bec" in categories:
            return "Impersonate executive to authorize fraudulent transactions"
        if "scam" in categories:
            return "Deceive user into providing personal information or money"
        return "Manipulate user into taking harmful action"

    def _build_recommendations(self, classification: str, indicators: list[dict],
                                url_info: list[dict] | None) -> list[str]:
        actions = []
        if classification in ("phishing", "suspicious"):
            actions.append("Do not click any links in this email")
            actions.append("Do not download or open any attachments")
            actions.append("Report this email to your security team")
            actions.append("Verify the sender's identity through official channels")
            if any(i.get("category") == "credential_harvesting" for i in indicators):
                actions.append("Change your passwords if you have already entered credentials")
            if any(i.get("category") == "financial" for i in indicators):
                actions.append("Do not make any financial transactions based on this email")
        else:
            actions.append("No immediate action required")
            actions.append("Standard email hygiene practices apply")
        return actions

    def _build_technical_notes(self, sender_issues: list[str], url_issues: list[str]) -> str:
        notes = []
        if sender_issues:
            notes.append("Sender Analysis: " + "; ".join(sender_issues))
        if url_issues:
            notes.append("URL Analysis: " + "; ".join(url_issues[:3]))
        return " | ".join(notes) if notes else "No additional technical concerns identified."

    async def generate_explanation(self, email_text: str, indicators: list[dict],
                                    classification: str) -> str:
        """Generate a human-readable explanation string."""
        if not indicators:
            if classification == "safe":
                return "This email appears to be legitimate. No suspicious indicators were detected."
            return "Limited analysis available. Exercise standard caution."

        parts = []
        # Group indicators by category
        categories: dict[str, list[dict]] = {}
        for ind in indicators:
            cat = ind.get("category", "general")
            categories.setdefault(cat, []).append(ind)

        for cat, inds in categories.items():
            cat_name = cat.replace("_", " ").title()
            matched_texts = [f'"{i["matched_text"]}"' for i in inds if i.get("matched_text")]
            if matched_texts:
                parts.append(f"{cat_name}: This email contains {', '.join(matched_texts[:3])} "
                           f"which {'are' if len(matched_texts) > 1 else 'is'} "
                           f"commonly used in phishing attacks.")

        if parts:
            return " ".join(parts)
        return f"Email classified as {classification} based on {len(indicators)} detected indicators."

    @property
    def status(self) -> str:
        if self.is_available:
            return f"connected ({self.settings.llm_provider})"
        return "mock_fallback"
