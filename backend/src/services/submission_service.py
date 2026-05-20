"""
Submission Service Layer.
Orchestrates business logic: suppression checks, state transitions, and actual SMS dispatch via Twilio.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from src.config.settings import settings
from src.models.submission import Submission, SubmissionStatus
from src.repositories.submission_repository import SubmissionRepository
from src.services.twilio_service import TwilioService


class SubmissionService:
    """
    High-level service for managing Submission workflows.
    Decouples business rules from HTTP handlers and integrates Twilio for SMS.
    """

    def __init__(self, db):
        self.repository = SubmissionRepository(db)
        self.twilio_service = TwilioService()

    def create_submission(self, first_name: str, phone_number: str) -> Dict[str, Any]:
        """
        Handles the submission creation workflow including the suppression logic check.
        If not suppressed, attempts to send SMS via Twilio.
        """
        window_days = settings.SUPPRESSION_WINDOW_DAYS
        last_successful = self.repository.get_last_successful_sms(phone_number, window_days)
        created_at = datetime.now(timezone.utc)

        if last_successful and last_successful.sms_sent_at:
            # Scenario: Suppressed
            # Ensure the database datetime is timezone-aware (UTC) to allow subtraction
            sent_at = last_successful.sms_sent_at
            if sent_at.tzinfo is None:
                sent_at = sent_at.replace(tzinfo=timezone.utc)

            delta = created_at - sent_at
            days_ago = delta.days
            message = f"Number already contacted {days_ago} days ago — suppression rule applied, no SMS sent."
            
            submission = Submission(
                first_name=first_name,
                phone_number=phone_number,
                status=SubmissionStatus.SUPPRESSED,
                suppression_reason="Contacted within 90-day suppression window",
                google_review_url=settings.GOOGLE_REVIEW_URL,
                sms_sent=False,
                sms_sent_at=None,
                created_at=created_at,
                updated_at=created_at
            )
            saved_submission = self.repository.create(submission)
            
            return {
                "status": "suppressed",
                "message": message,
                "submission": self._serialize_submission(saved_submission)
            }

        else:
            # Scenario: Accepted (Pending)
            sms_body = f"Hi {first_name}, thanks for visiting! Please leave us a review here: {settings.GOOGLE_REVIEW_URL}"
            
            sms_success, sms_sid = self.twilio_service.send_sms(phone_number, sms_body)
            
            submission = Submission(
                first_name=first_name,
                phone_number=phone_number,
                status=SubmissionStatus.PENDING,
                suppression_reason=None,
                google_review_url=settings.GOOGLE_REVIEW_URL,
                sms_sent=sms_success,
                sms_sent_at=datetime.now(timezone.utc) if sms_success else None,
                created_at=created_at,
                updated_at=created_at
            )
            
            saved_submission = self.repository.create(submission)
            
            response_status = "submitted" if sms_success else "error"
            response_message = "SMS scheduled successfully." if sms_success else "Failed to send SMS."

            return {
                "status": response_status,
                "message": response_message,
                "submission": self._serialize_submission(saved_submission)
            }

    def get_submissions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieves a list of recent submissions.
        """
        submissions = self.repository.list_recent(limit)
        return [self._serialize_submission(s) for s in submissions]

    def get_submission_by_id(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single submission by ID.
        """
        submission = self.repository.get_by_id(submission_id)
        if not submission:
            return None
        return self._serialize_submission(submission)

    def _serialize_submission(self, sub: Submission) -> Dict[str, Any]:
        """
        Internal helper to convert Domain Entity to Dict for API response.
        """
        return {
            "id": sub.id,
            "first_name": sub.first_name,
            "phone_number": sub.phone_number,
            "status": sub.status.value,
            "suppression_reason": sub.suppression_reason,
            "google_review_url": sub.google_review_url,
            "sms_sent": sub.sms_sent,
            "sms_sent_at": sub.sms_sent_at.isoformat() if sub.sms_sent_at else None,
            "created_at": sub.created_at.isoformat() if sub.created_at else None,
            "feedback": None 
        }