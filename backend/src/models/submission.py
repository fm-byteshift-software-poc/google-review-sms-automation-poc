"""
Domain entity for Submission.
Pure business object with NO SQLAlchemy or framework dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class SubmissionStatus(str, Enum):
    """Status values for submission lifecycle."""
    PENDING = "pending"
    SUPPRESSED = "suppressed"
    SATISFIED = "satisfied"
    DISSATISFIED = "dissatisfied"


@dataclass
class Submission:
    """
    Domain entity representing a customer review request submission.
    
    Business Rules:
    - Phone numbers can exist multiple times historically
    - Suppression applies when contacted within 90 days
    - Status transitions: pending -> (satisfied | dissatisfied | suppressed)
    """
    
    first_name: str
    phone_number: str
    google_review_url: str
    status: SubmissionStatus = SubmissionStatus.PENDING
    suppression_reason: Optional[str] = None
    sms_sent: bool = False
    sms_sent_at: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Set timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    def suppress(self, reason: str) -> None:
        """
        Apply suppression rule to this submission.
        """
        self.status = SubmissionStatus.SUPPRESSED
        self.suppression_reason = reason
        self.sms_sent = False
        self.updated_at = datetime.utcnow()

    def mark_sms_sent(self) -> None:
        """
        Mark SMS as sent with timestamp.
        """
        self.sms_sent = True
        self.sms_sent_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_satisfied(self) -> None:
        """
        Transition to satisfied status.
        """
        self.status = SubmissionStatus.SATISFIED
        self.updated_at = datetime.utcnow()

    def mark_dissatisfied(self) -> None:
        """
        Transition to dissatisfied status.
        """
        self.status = SubmissionStatus.DISSATISFIED
        self.updated_at = datetime.utcnow()

    def is_suppressed(self) -> bool:
        """
        Check if submission is suppressed.
        """
        return self.status == SubmissionStatus.SUPPRESSED

    def can_receive_sms(self) -> bool:
        """
        Business rule: Can this submission receive an SMS?
        """
        return self.status == SubmissionStatus.PENDING and not self.sms_sent