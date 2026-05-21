"""
Feedback Service Layer.
Orchestrates feedback branching, state updates, and alert email dispatch.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from src.config.settings import settings
from src.models.feedback import Feedback, SatisfactionStatus
from src.models.submission import SubmissionStatus
from src.repositories.feedback_repository import FeedbackRepository
from src.repositories.submission_repository import SubmissionRepository
from src.services.resend_service import ResendService


class FeedbackService:
    """
    High-level service for managing Feedback workflows.
    Handles branching logic based on satisfaction status.
    """

    def __init__(self, db):
        self.feedback_repo = FeedbackRepository(db)
        self.submission_repo = SubmissionRepository(db)
        self.resend_service = ResendService()

    def create_feedback(
        self, 
        submission_id: str, 
        satisfaction: str, 
        private_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Records feedback and triggers branching logic.
        If 'no', sends an alert email.
        Updates the linked Submission status accordingly.
        """
        # 1. Check if submission exists
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            raise ValueError(f"Submission {submission_id} not found")

        # 2. Check 1:1 constraint
        existing_feedback = self.feedback_repo.get_by_submission_id(submission_id)
        if existing_feedback:
            raise ValueError("Feedback already exists for this submission.")

        # 3. Create Feedback Entity
        feedback = Feedback(
            submission_id=submission_id,
            satisfaction=SatisfactionStatus(satisfaction),
            private_feedback=private_feedback
        )

        # 4. Branching Logic
        if feedback.satisfaction == SatisfactionStatus.NO:
            # Alert Branch
            self._trigger_alert_email(submission, private_feedback)
            feedback.mark_alert_sent()
            
            # Update Submission Status
            submission.status = SubmissionStatus.DISSATISFIED
            self.submission_repo.update(submission)
            
        elif feedback.satisfaction == SatisfactionStatus.YES:
            # Happy Path Branch
            submission.status = SubmissionStatus.SATISFIED
            self.submission_repo.update(submission)

        # 5. Persist
        saved_feedback = self.feedback_repo.create(feedback)
        
        return {
            "success": True,
            "feedback": self._serialize_feedback(saved_feedback)
        }

    def get_feedback_by_id(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single feedback record."""
        feedback = self.feedback_repo.get_by_id(feedback_id)
        if not feedback:
            return None
        return self._serialize_feedback(feedback)

    def get_feedbacks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent feedback records."""
        records = self.feedback_repo.list_recent(limit)
        return [self._serialize_feedback(r) for r in records]

    def _trigger_alert_email(self, submission, private_feedback: Optional[str]):
        """Internal helper to dispatch email alert."""
        if not hasattr(settings, 'RESEND_API_KEY') or not settings.RESEND_API_KEY:
            print(f"[SIMULATION] Email Alert: Dissatisfied customer {submission.first_name}")
            return

        alert_to = getattr(settings, 'RESEND_ALERT_EMAIL', "alerts@poc-review.dev")
        subject = f"Dissatisfied Customer Alert: {submission.first_name}"
        body_html = (
            f"<h3>Customer Dissatisfaction Alert</h3>"
            f"<p><b>Name:</b> {submission.first_name}</p>"
            f"<p><b>Phone:</b> {submission.phone_number}</p>"
            f"<p><b>Feedback:</b> {private_feedback or 'No private feedback provided'}</p>"
            f"<p><em>This is an automated PoC alert.</em></p>"
        )
        
        success, _ = self.resend_service.send_alert_email(
            to=alert_to,
            subject=subject,
            body_html=body_html
        )
        
        if not success:
            print("WARNING: Failed to send alert email via Resend.")

    @staticmethod
    def _serialize_feedback(fb: Feedback) -> Dict[str, Any]:
        """Converts Domain Entity to Dict."""
        return {
            "id": fb.id,
            "submission_id": fb.submission_id,
            "satisfaction": fb.satisfaction.value,
            "private_feedback": fb.private_feedback,
            "alert_email_sent": fb.alert_email_sent,
            "created_at": fb.created_at.isoformat() if fb.created_at else None
        }

# """
# Feedback Service Layer.
# Orchestrates feedback submission, status branching, and alert email dispatch.
# PoC-focused: minimal validation, direct integration with ResendService.
# """

# import logging
# from typing import Optional

# from src.config.settings import settings
# from src.models.feedback import Feedback, SatisfactionStatus
# from src.models.submission import SubmissionStatus
# from src.repositories.feedback_repository import FeedbackRepository
# from src.repositories.submission_repository import SubmissionRepository
# from src.services.resend_service import ResendService


# class FeedbackService:
#     """
#     Service for handling customer feedback workflow.
#     Manages 1:1 relationship with Submission and triggers operational alerts.
#     """

#     def __init__(self, db):
#         self.feedback_repo = FeedbackRepository(db)
#         self.submission_repo = SubmissionRepository(db)
#         self.resend_service = ResendService()

#     def create_feedback(
#         self,
#         submission_id: str,
#         satisfaction: str,
#         private_feedback: Optional[str] = None
#     ) -> dict:
#         """
#         Processes feedback submission and triggers appropriate workflow.

#         Returns:
#             Dict matching the POST /api/feedback response contract.
#         """
#         # 1. Validate submission exists
#         submission = self.submission_repo.get_by_id(submission_id)
#         if not submission:
#             raise ValueError("Submission not found")

#         # 2. Enforce 1:1 constraint
#         existing_feedback = self.feedback_repo.get_by_submission_id(submission_id)
#         if existing_feedback:
#             raise ValueError("Feedback already exists for this submission")

#         # 3. Create domain entity
#         feedback = Feedback(
#             submission_id=submission_id,
#             satisfaction=SatisfactionStatus.YES if satisfaction == "yes" else SatisfactionStatus.NO,
#             private_feedback=private_feedback
#         )

#         # 4. Branch: Dissatisfied => Trigger Alert Email
#         if feedback.requires_alert():
#             alert_to = settings.RESEND_ALERT_EMAIL if hasattr(settings, "RESEND_ALERT_EMAIL") else "alerts@poc-review.dev"
#             subject = f"Dissatisfied Customer Alert: {submission.first_name}"
#             body_html = (
#                 f"<h3>Customer Dissatisfaction Alert</h3>"
#                 f"<p><b>Name:</b> {submission.first_name}</p>"
#                 f"<p><b>Phone:</b> {submission.phone_number}</p>"
#                 f"<p><b>Feedback:</b> {private_feedback or 'No private feedback provided'}</p>"
#                 f"<p><em>This is an automated PoC alert.</em></p>"
#             )
            
#             success, _ = self.resend_service.send_alert_email(
#                 to=alert_to,
#                 subject=subject,
#                 body_html=body_html
#             )
            
#             if success:
#                 feedback.mark_alert_sent()
#                 logging.info(f"✅ Alert email dispatched for submission {submission_id}")
#             else:
#                 logging.warning(f"⚠️  Alert email failed for submission {submission_id}. PoC continues without aborting.")

#         # 5. Update Submission Status based on satisfaction
#         if satisfaction == "yes":
#             submission.mark_satisfied()
#         else:
#             submission.mark_dissatisfied()

#         # 6. Persist changes
#         saved_feedback = self.feedback_repo.create(feedback)
#         self.submission_repo.update(submission)

#         # 7. Return API contract response
#         return {
#             "success": True,
#             "feedback": {
#                 "id": saved_feedback.id,
#                 "submission_id": saved_feedback.submission_id,
#                 "satisfaction": saved_feedback.satisfaction.value,
#                 "private_feedback": saved_feedback.private_feedback,
#                 "alert_email_sent": saved_feedback.alert_email_sent
#             }
#         }