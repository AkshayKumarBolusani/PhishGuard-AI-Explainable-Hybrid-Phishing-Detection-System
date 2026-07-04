"""PhishGuard AI — Dashboard & Feedback Schemas"""
from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_scans: int = 0
    safe_count: int = 0
    suspicious_count: int = 0
    phishing_count: int = 0
    average_risk_score: float = 0.0
    daily_scans: int = 0
    weekly_scans: int = 0


class ThreatTrend(BaseModel):
    date: str
    safe: int = 0
    suspicious: int = 0
    phishing: int = 0
    total: int = 0


class AttackTypeCount(BaseModel):
    attack_type: str
    count: int


class FeedbackInput(BaseModel):
    scan_id: str
    is_correct: bool
    correct_label: str = ""
    feedback_text: str = ""


class FeedbackResponse(BaseModel):
    id: str
    scan_id: str
    is_correct: bool
    correct_label: str
    feedback_text: str
    created_at: str


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    models: dict[str, str] = {}
    uptime_seconds: float = 0.0
