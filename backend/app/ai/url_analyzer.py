"""
PhishGuard AI — URL Analysis Engine

Extracts and analyzes URLs from email text: domain parsing, shortener detection,
IP address URLs, homograph detection, suspicious TLD detection, reputation scoring.
"""

import re
from urllib.parse import urlparse
import structlog

logger = structlog.get_logger(__name__)

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "tiny.cc", "lnkd.in", "db.tt", "rb.gy",
    "cutt.ly", "shorturl.at", "t.ly", "v.gd", "qr.ae", "rebrand.ly",
}

SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".win", ".bid",
    ".click", ".link", ".work", ".date", ".racing", ".review", ".stream",
    ".party", ".gdn", ".science", ".accountant", ".loan", ".download",
    ".cricket", ".faith", ".trade", ".webcam",
}

TRUSTED_DOMAINS = {
    "google.com", "microsoft.com", "apple.com", "amazon.com", "paypal.com",
    "facebook.com", "twitter.com", "linkedin.com", "github.com", "netflix.com",
    "dropbox.com", "slack.com", "zoom.us", "adobe.com", "salesforce.com",
}

BRAND_DOMAINS = {
    "paypal": "paypal.com", "apple": "apple.com", "microsoft": "microsoft.com",
    "google": "google.com", "amazon": "amazon.com", "netflix": "netflix.com",
    "facebook": "facebook.com", "instagram": "instagram.com", "chase": "chase.com",
    "wellsfargo": "wellsfargo.com", "bankofamerica": "bankofamerica.com",
}


class URLAnalyzer:
    """Analyzes URLs extracted from email text for suspicious characteristics."""

    def __init__(self):
        self.url_pattern = re.compile(
            r'https?://[^\s<>"{}|\\^`\[\]]+|'
            r'www\.[^\s<>"{}|\\^`\[\]]+',
            re.IGNORECASE,
        )

    def extract_and_analyze(self, text: str) -> list[dict]:
        """Extract all URLs from text and analyze each one."""
        urls = self.url_pattern.findall(text)
        # Also extract from href attributes in HTML
        href_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
        urls.extend(href_pattern.findall(text))

        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return [self.analyze_url(url) for url in unique_urls[:20]]

    def analyze_url(self, url: str) -> dict:
        """Analyze a single URL for suspicious characteristics."""
        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        try:
            parsed = urlparse(url)
        except Exception:
            return {"original_url": url, "domain": "", "tld": "",
                    "suspicious_score": 0.5, "reasons": ["Failed to parse URL"]}

        domain = parsed.hostname or ""
        tld = ""
        try:
            import tldextract
            ext = tldextract.extract(url)
            domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
            tld = f".{ext.suffix}" if ext.suffix else ""
        except ImportError:
            parts = domain.rsplit(".", 1)
            tld = f".{parts[-1]}" if len(parts) > 1 else ""

        reasons = []
        score = 0.0

        # Check if IP address
        is_ip = bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', parsed.hostname or ""))
        if is_ip:
            reasons.append("URL uses IP address instead of domain name")
            score += 0.3

        # Check HTTPS
        is_https = parsed.scheme == "https"
        if not is_https:
            reasons.append("URL does not use HTTPS encryption")
            score += 0.1

        # Check shortener
        is_shortened = any(s in domain.lower() for s in SHORTENERS)
        if is_shortened:
            reasons.append("URL uses a URL shortening service")
            score += 0.2

        # Check suspicious TLD
        if any(domain.endswith(t) for t in SUSPICIOUS_TLDS):
            reasons.append(f"Suspicious top-level domain: {tld}")
            score += 0.25

        # Check homograph / typosquatting
        is_homograph = self._check_homograph(domain)
        if is_homograph:
            reasons.append("Domain may be using homograph/typosquatting attack")
            score += 0.35

        # Check for excessive subdomains
        subdomain_count = domain.count(".")
        if subdomain_count > 3:
            reasons.append(f"Unusual number of subdomains ({subdomain_count})")
            score += 0.15

        # Check for suspicious characters in path
        if "@" in url:
            reasons.append("URL contains @ symbol (potential redirect)")
            score += 0.3

        # Check URL length
        if len(url) > 200:
            reasons.append("Unusually long URL")
            score += 0.1

        # Check for data URI
        if "data:" in url.lower():
            reasons.append("Contains data URI scheme")
            score += 0.4

        return {
            "original_url": url[:500],
            "domain": domain,
            "tld": tld,
            "is_shortened": is_shortened,
            "is_ip_address": is_ip,
            "is_https": is_https,
            "is_homograph": is_homograph,
            "suspicious_score": round(min(1.0, score), 2),
            "reasons": reasons,
        }

    def _check_homograph(self, domain: str) -> bool:
        """Check if domain uses homograph characters or typosquatting."""
        # Check for confusable characters
        confusables = {"0": "o", "1": "l", "rn": "m", "vv": "w", "cl": "d"}
        domain_lower = domain.lower()

        for fake, real in confusables.items():
            if fake in domain_lower:
                for brand_key, brand_domain in BRAND_DOMAINS.items():
                    test = domain_lower.replace(fake, real)
                    if brand_key in test and domain_lower != brand_domain:
                        return True

        # Check Levenshtein distance to known brands
        for brand_domain in TRUSTED_DOMAINS:
            if domain_lower != brand_domain and self._levenshtein(domain_lower, brand_domain) <= 2:
                return True

        return False

    def _levenshtein(self, s1: str, s2: str) -> int:
        """Compute Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)

        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]
