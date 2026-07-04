"""
PhishGuard AI — Sender Analysis Engine

Analyzes email sender for typosquatting, display name mismatches,
free provider detection, and domain reputation scoring.
"""

import re

import structlog

logger = structlog.get_logger(__name__)

FREE_EMAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "mail.com", "protonmail.com", "zoho.com", "icloud.com", "yandex.com",
    "gmx.com", "tutanota.com", "fastmail.com", "hushmail.com",
    "live.com", "msn.com", "inbox.com", "ymail.com", "rocketmail.com",
}

BRAND_DOMAINS = {
    "paypal.com": ["paypa1.com", "paypaI.com", "paypal-security.com", "paypal.tk"],
    "apple.com": ["app1e.com", "apple-id.com", "apple-support.tk"],
    "microsoft.com": ["micros0ft.com", "microsoft-security.com", "microsft.com"],
    "google.com": ["g00gle.com", "google-security.com", "googIe.com"],
    "amazon.com": ["amaz0n.com", "amazon-delivery.com", "arnazon.com"],
    "netflix.com": ["netfIix.com", "netflix-billing.com", "netfl1x.com"],
    "chase.com": ["chase-secure.com", "chase-banking.tk"],
    "bankofamerica.com": ["bankofamerica-secure.com", "bankofamer1ca.com"],
}


class SenderAnalyzer:
    """Analyzes email sender for suspicious characteristics."""

    def analyze(self, sender_email: str, display_name: str = "") -> dict:
        """Full sender analysis."""
        result = {
            "email": sender_email,
            "display_name": display_name,
            "domain": "",
            "is_free_provider": False,
            "is_display_name_mismatch": False,
            "is_typosquatting": False,
            "spoofed_domain": "",
            "trust_score": 100.0,
            "spf_status": "not_checked",
            "dkim_status": "not_checked",
            "dmarc_status": "not_checked",
            "reasons": [],
        }

        # Extract domain
        match = re.search(r'@([\w.-]+)', sender_email)
        if not match:
            result["reasons"].append("Invalid email format — no domain found")
            result["trust_score"] = 20.0
            return result

        domain = match.group(1).lower()
        result["domain"] = domain

        # Check free email provider
        if domain in FREE_EMAIL_PROVIDERS:
            result["is_free_provider"] = True
            result["reasons"].append(f"Sent from free email provider: {domain}")
            result["trust_score"] -= 15

        # Check display name mismatch
        if display_name:
            result["is_display_name_mismatch"] = self._check_display_name_mismatch(
                display_name, sender_email, domain
            )
            if result["is_display_name_mismatch"]:
                result["reasons"].append(
                    f'Display name "{display_name}" does not match sender domain "{domain}"'
                )
                result["trust_score"] -= 25

        # Check typosquatting
        spoofed = self._check_typosquatting(domain)
        if spoofed:
            result["is_typosquatting"] = True
            result["spoofed_domain"] = spoofed
            result["reasons"].append(
                f'Domain "{domain}" appears to impersonate "{spoofed}" (typosquatting)'
            )
            result["trust_score"] -= 40

        # Clamp trust score
        result["trust_score"] = max(0, min(100, result["trust_score"]))

        return result

    def _check_display_name_mismatch(self, display_name: str, email: str, domain: str) -> bool:
        """Check if the display name suggests a different organization than the actual sender."""
        display_lower = display_name.lower()

        # Check if display name contains a brand but email is from a different domain
        for brand_domain in BRAND_DOMAINS:
            brand_name = brand_domain.split(".")[0]
            if brand_name in display_lower and domain != brand_domain:
                return True

        # Check if display name looks like an email address different from actual
        email_in_display = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', display_name)
        return bool(
            email_in_display and email_in_display.group(0).lower() != email.lower()
        )

    def _check_typosquatting(self, domain: str) -> str:
        """Check if domain is a known typosquat of a legitimate brand."""
        # Direct known typosquat check
        for legit_domain, typosquats in BRAND_DOMAINS.items():
            if domain in [t.lower() for t in typosquats]:
                return legit_domain

        # Levenshtein distance check
        for legit_domain in BRAND_DOMAINS:
            if domain != legit_domain and self._levenshtein(domain, legit_domain) <= 2:
                return legit_domain

        return ""

    def _levenshtein(self, s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                curr_row.append(min(prev_row[j + 1] + 1, curr_row[j] + 1, prev_row[j] + (c1 != c2)))
            prev_row = curr_row
        return prev_row[-1]
