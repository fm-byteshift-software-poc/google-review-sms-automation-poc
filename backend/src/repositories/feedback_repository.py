"""
Feedback Repository.
Data access layer for the Feedback domain entity.
Enforces 1:1 relationship with Submission and handles persistence.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Enum, Boolean, DateTime, ForeignKey, func, select, Text
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import Session, relationship

from src.repositories.database import Base
from src.repositories.submission_repository import SubmissionRecord
from src.models.feedback import Feedback, SatisfactionStatus


# ==============================================================================
# SQLAlchemy ORM Model (Persistence Layer)
# ==============================================================================
class FeedbackRecord(Base):
    """SQLAlchemy table definition for feedback."""
    __tablename__ = "feedbacks"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    submission_id = Column(
        CHAR(36), 
        ForeignKey("submissions.id"), 
        unique=True,  # Enforces 1:1 relationship
        nullable=False, 
        index=True
    )
    satisfaction = Column(Enum("yes", "no", name="satisfaction_enum"), nullable=False)
    private_feedback = Column(Text, nullable=True)
    alert_email_sent = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship back to SubmissionRecord
    # submission = relationship("SubmissionRecord", back_populates="feedback")


# ==============================================================================
# Repository Pattern Implementation
# ==============================================================================
class FeedbackRepository:
    """
    Repository for managing Feedback persistence.
    Decouples domain logic from SQLAlchemy specifics.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, feedback: Feedback) -> Feedback:
        """
        Persist a new feedback record.
        """
        record = FeedbackRecord(
            id=feedback.id,
            submission_id=feedback.submission_id,
            satisfaction=feedback.satisfaction.value,
            private_feedback=feedback.private_feedback,
            alert_email_sent=feedback.alert_email_sent,
            created_at=feedback.created_at
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._to_domain(record)

    def get_by_submission_id(self, submission_id: str) -> Optional[Feedback]:
        """
        Retrieve feedback associated with a specific submission.
        """
        stmt = select(FeedbackRecord).where(FeedbackRecord.submission_id == submission_id)
        record = self.db.execute(stmt).scalar_one_or_none()
        return self._to_domain(record) if record else None

    def update(self, feedback: Feedback) -> Feedback:
        """
        Update an existing feedback record.
        """
        stmt = select(FeedbackRecord).where(FeedbackRecord.id == feedback.id)
        record = self.db.execute(stmt).scalar_one_or_none()
        if not record:
            raise ValueError(f"Feedback {feedback.id} not found")

        record.satisfaction = feedback.satisfaction.value
        record.private_feedback = feedback.private_feedback
        record.alert_email_sent = feedback.alert_email_sent

        self.db.commit()
        self.db.refresh(record)
        return self._to_domain(record)

    @staticmethod
    def _to_domain(record: FeedbackRecord) -> Feedback:
        """
        Map SQLAlchemy record to Domain entity.
        """
        return Feedback(
            id=record.id,
            submission_id=record.submission_id,
            satisfaction=SatisfactionStatus(record.satisfaction),
            private_feedback=record.private_feedback,
            alert_email_sent=record.alert_email_sent,
            created_at=record.created_at
        )