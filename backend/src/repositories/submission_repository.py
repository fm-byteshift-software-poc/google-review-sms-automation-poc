"""
Submission Repository.
Data access layer for the Submission domain entity.
Handles persistence, retrieval, and suppression window checks.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import Column, String, Enum, Boolean, DateTime, func, select, and_, desc
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import Session

from src.repositories.database import Base
from src.models.submission import Submission, SubmissionStatus


# ==============================================================================
# SQLAlchemy ORM Model (Persistence Layer)
# ==============================================================================
class SubmissionRecord(Base):
    """SQLAlchemy table definition for submissions."""
    __tablename__ = "submissions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    first_name = Column(String(80), nullable=False)
    phone_number = Column(String(50), nullable=False, index=True)
    status = Column(
        Enum("pending", "suppressed", "satisfied", "dissatisfied", name="submission_status"),
        nullable=False,
        default="pending"
    )
    suppression_reason = Column(String(255), nullable=True)
    google_review_url = Column(String(500), nullable=False)
    sms_sent = Column(Boolean, nullable=False, default=False)
    sms_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ✅ REMOVIDO: relationship com Feedback para evitar erro de mapper no PoC
    # O feedback é carregado via query separada quando necessário


# ==============================================================================
# Repository Pattern Implementation
# ==============================================================================
class SubmissionRepository:
    """
    Repository for managing Submission persistence.
    Decouples domain logic from SQLAlchemy specifics.
    """

    def __init__(self, db: Session):
        self.db = db

    # --- Query Methods ---

    def get_by_id(self, submission_id: str) -> Optional[Submission]:
        stmt = select(SubmissionRecord).where(SubmissionRecord.id == submission_id)
        record = self.db.execute(stmt).scalar_one_or_none()
        return self._to_domain(record) if record else None

    def list_recent(self, limit: int = 5) -> List[Submission]:
        stmt = select(SubmissionRecord).order_by(desc(SubmissionRecord.created_at)).limit(limit)
        records = self.db.execute(stmt).scalars().all()
        return [self._to_domain(r) for r in records]

    def get_last_successful_sms(self, phone_number: str, window_days: int = 90) -> Optional[SubmissionRecord]:
        """
        Checks suppression rule:
        Returns the most recent submission where sms_sent=True within the last N days.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=window_days)
        stmt = select(SubmissionRecord).where(
            and_(
                SubmissionRecord.phone_number == phone_number,
                SubmissionRecord.sms_sent == True,
                SubmissionRecord.sms_sent_at >= cutoff_date
            )
        ).order_by(desc(SubmissionRecord.sms_sent_at)).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

    # --- Command Methods ---

    def create(self, submission: Submission) -> Submission:
        record = SubmissionRecord(
            id=submission.id,
            first_name=submission.first_name,
            phone_number=submission.phone_number,
            status=submission.status.value if isinstance(submission.status, SubmissionStatus) else submission.status,
            suppression_reason=submission.suppression_reason,
            google_review_url=submission.google_review_url,
            sms_sent=submission.sms_sent,
            sms_sent_at=submission.sms_sent_at,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._to_domain(record)

    def update(self, submission: Submission) -> Submission:
        stmt = select(SubmissionRecord).where(SubmissionRecord.id == submission.id)
        record = self.db.execute(stmt).scalar_one_or_none()
        if not record:
            raise ValueError(f"Submission {submission.id} not found")

        record.status = submission.status.value if isinstance(submission.status, SubmissionStatus) else submission.status
        record.suppression_reason = submission.suppression_reason
        record.sms_sent = submission.sms_sent
        record.sms_sent_at = submission.sms_sent_at
        record.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(record)
        return self._to_domain(record)

    # --- Mapper Helpers ---

    @staticmethod
    def _to_domain(record: SubmissionRecord) -> Submission:
        return Submission(
            id=record.id,
            first_name=record.first_name,
            phone_number=record.phone_number,
            status=SubmissionStatus(record.status),
            suppression_reason=record.suppression_reason,
            google_review_url=record.google_review_url,
            sms_sent=record.sms_sent,
            sms_sent_at=record.sms_sent_at,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )