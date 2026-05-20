"""
Domain entity for Feedback.
Pure business object with NO SQLAlchemy or framework dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class SatisfactionStatus(str, Enum):
    """Satisfaction values for customer feedback."""
    YES = "yes"
    NO = "no"


@dataclass
class Feedback:
    """
    Domain entity representing customer feedback on a submission.
    
    Business Rules:
    - One Submission can have at most one Feedback
    - If satisfaction="no", an alert email must be sent to operations
    - private_feedback is only collected when satisfaction="no"
    """
    
    submission_id: str
    satisfaction: SatisfactionStatus
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    private_feedback: Optional[str] = None
    alert_email_sent: bool = False
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def requires_alert(self) -> bool:
        """
        Business rule: Does this feedback require an operational alert?
        Returns True if satisfaction is "no" AND alert hasn't been sent yet.
        """
        return self.satisfaction == SatisfactionStatus.NO and not self.alert_email_sent

    def mark_alert_sent(self) -> None:
        """
        Mark that the alert email has been dispatched.
        """
        self.alert_email_sent = True

    def is_dissatisfied(self) -> bool:
        """
        Check if customer expressed dissatisfaction.
        """
        return self.satisfaction == SatisfactionStatus.NO

    def is_satisfied(self) -> bool:
        """
        Check if customer expressed satisfaction.
        """
        return self.satisfaction == SatisfactionStatus.YES