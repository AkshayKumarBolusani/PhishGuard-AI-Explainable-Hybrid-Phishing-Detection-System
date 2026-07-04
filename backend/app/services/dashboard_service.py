"""PhishGuard AI — Dashboard Service"""

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.scan_repository import ScanRepository


class DashboardService:
    def __init__(self):
        self.scan_repo = ScanRepository()
        self.feedback_repo = FeedbackRepository()

    def get_statistics(self, user_id: str | None = None) -> dict:
        stats = self.scan_repo.get_statistics(user_id)
        rows = self.scan_repo.find_by_user(user_id)

        now = datetime.now(timezone.utc)
        today = now.date()
        week_ago = today - timedelta(days=7)

        daily = sum(1 for r in rows if self._parse_date(r) == today)
        weekly = sum(1 for r in rows if self._parse_date(r) and self._parse_date(r) >= week_ago)

        stats["daily_scans"] = daily
        stats["weekly_scans"] = weekly
        return stats

    def get_trends(self, user_id: str | None = None, days: int = 30) -> list[dict]:
        rows = self.scan_repo.find_by_user(user_id)

        now = datetime.now(timezone.utc).date()
        start = now - timedelta(days=days)
        trends: dict[str, dict] = {}

        for i in range(days + 1):
            d = (start + timedelta(days=i)).isoformat()
            trends[d] = {"date": d, "safe": 0, "suspicious": 0, "phishing": 0, "total": 0}

        for row in rows:
            d = self._parse_date(row)
            if d and d >= start:
                key = d.isoformat()
                if key in trends:
                    cls = row.get("classification", "safe")
                    trends[key][cls] = trends[key].get(cls, 0) + 1
                    trends[key]["total"] += 1

        return list(trends.values())

    def get_attack_types(self, user_id: str | None = None) -> list[dict]:
        rows = self.scan_repo.find_by_user(user_id)

        type_counts: dict[str, int] = defaultdict(int)
        for row in rows:
            indicators = row.get("indicators", [])
            if isinstance(indicators, str):
                try:
                    indicators = json.loads(indicators)
                except (json.JSONDecodeError, TypeError):
                    indicators = []

            categories = {i.get("category", "unknown") for i in indicators if isinstance(i, dict)}
            for cat in categories:
                type_counts[cat] += 1

        return sorted(
            [{"attack_type": k, "count": v} for k, v in type_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:15]

    def get_feedback_stats(self) -> dict:
        return self.feedback_repo.get_accuracy_stats()

    def _parse_date(self, row: dict):
        try:
            return datetime.fromisoformat(row.get("created_at", "")).date()
        except (ValueError, TypeError):
            return None
