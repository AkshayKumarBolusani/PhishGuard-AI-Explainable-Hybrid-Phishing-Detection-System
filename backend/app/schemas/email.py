"""
PhishGuard AI — Email Schemas

Pydantic models for email scan input, output, and all analysis sub-components.
"""

from typing import Any

from pydantic import BaseModel, Field


class EmailInput(BaseModel):
    """Input schema for a single email scan."""
    subject: str = Field(..., min_length=1, max_length=1000, description="Email subject line")
    sender: str = Field(..., min_length=1, max_length=500, description="Sender email address")
    receiver: str = Field("", max_length=500, description="Receiver email address")
    body: str = Field(..., min_length=1, max_length=50000, description="Email body content")

    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Urgent: Your account has been compromised",
                "sender": "security@paypa1.com",
                "receiver": "user@example.com",
                "body": "Dear valued customer, we detected unusual activity on your account. Click here to verify your identity immediately: http://paypa1-secure.tk/verify"
            }
        }


class BatchScanInput(BaseModel):
    """Input for batch email scanning."""
    emails: list[EmailInput] = Field(..., min_length=1, max_length=10)


class URLAnalysis(BaseModel):
    """Analysis result for a single URL found in the email."""
    original_url: str
    domain: str = ""
    tld: str = ""
    is_shortened: bool = False
    is_ip_address: bool = False
    is_https: bool = False
    is_homograph: bool = False
    suspicious_score: float = 0.0
    reasons: list[str] = []


class SenderAnalysis(BaseModel):
    """Analysis of the email sender."""
    email: str = ""
    display_name: str = ""
    domain: str = ""
    is_free_provider: bool = False
    is_display_name_mismatch: bool = False
    is_typosquatting: bool = False
    spoofed_domain: str = ""
    trust_score: float = 100.0
    spf_status: str = "not_checked"
    dkim_status: str = "not_checked"
    dmarc_status: str = "not_checked"
    reasons: list[str] = []


class NLPFeatures(BaseModel):
    """NLP features extracted from the email."""
    entities: dict[str, list[str]] = {}
    action_verbs: list[str] = []
    imperative_sentences: list[str] = []
    sentiment: dict[str, float] = {}
    urgency_score: float = 0.0
    readability_score: float = 0.0
    emotion: str = "neutral"
    word_count: int = 0
    sentence_count: int = 0


class SuspiciousIndicator(BaseModel):
    """A single detected suspicious indicator."""
    name: str
    category: str
    severity: str  # low, medium, high, critical
    confidence: float
    matched_text: str = ""
    description: str = ""


class TextHighlight(BaseModel):
    """A highlighted span of suspicious text."""
    start: int
    end: int
    text: str
    category: str
    severity: str


class ModelResult(BaseModel):
    """Result from a single AI model."""
    model_name: str
    classification: str
    confidence: float
    probabilities: dict[str, float] = {}
    latency_ms: float = 0.0
    features: dict[str, Any] = {}


class SecurityReport(BaseModel):
    """Full AI-generated security report."""
    executive_summary: str = ""
    risk_level: str = "low"
    threat_indicators: list[str] = []
    evidence: list[dict[str, str]] = []
    attack_type: str = "none"
    likely_goal: str = ""
    recommended_actions: list[str] = []
    user_advice: str = ""
    security_score: float = 100.0
    technical_notes: str = ""


class ScanResult(BaseModel):
    """Complete scan result returned to the frontend."""
    id: str
    classification: str  # safe, suspicious, phishing
    confidence: float
    risk_score: float
    probabilities: dict[str, float] = {}
    indicators: list[SuspiciousIndicator] = []
    urls_analysis: list[URLAnalysis] = []
    sender_analysis: SenderAnalysis = SenderAnalysis()
    nlp_features: NLPFeatures = NLPFeatures()
    explanation: str = ""
    security_report: SecurityReport = SecurityReport()
    highlights: list[TextHighlight] = []
    model_results: list[ModelResult] = []
    processing_time_ms: float = 0.0
    created_at: str = ""


class ScanListItem(BaseModel):
    """Abbreviated scan result for list views."""
    id: str
    subject: str
    sender: str
    classification: str
    confidence: float
    risk_score: float
    is_favorite: bool = False
    created_at: str = ""


class PaginatedScans(BaseModel):
    """Paginated list of scan results."""
    items: list[ScanListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
