"""PhishGuard AI — Feedback Service"""
from app.repositories.feedback_repository import FeedbackRepository


class FeedbackService:
    def __init__(self):
        self.feedback_repo = FeedbackRepository()

    def submit_feedback(self, scan_id: str, user_id: str, is_correct: bool,
                        correct_label: str = "", feedback_text: str = "") -> dict:
        record = self.feedback_repo.create({
            "scan_id": scan_id, "user_id": user_id, "is_correct": is_correct,
            "correct_label": correct_label, "feedback_text": feedback_text,
        })
        return record

    def get_feedback(self, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
        return self.feedback_repo.get_all(page=page, page_size=page_size)

    def get_scan_feedback(self, scan_id: str) -> list[dict]:
        return self.feedback_repo.get_by_scan_id(scan_id)
