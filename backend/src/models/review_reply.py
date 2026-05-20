from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
from typing import Optional

class ModerationStatus(str, Enum):
    AUTO_APPROVED = "auto-approved"
    REQUIRES_APPROVAL = "requires-approval"

@dataclass
class ReviewReply:
    customer_name: str
    star_rating: int
    review_text: str
    generated_reply: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    moderation_status: Optional[ModerationStatus] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not 1 <= self.star_rating <= 5:
            raise ValueError("star_rating must be between 1 and 5")

        if self.moderation_status is None:
            if self.star_rating >= 4:
                object.__setattr__(self, 'moderation_status', ModerationStatus.AUTO_APPROVED)
            elif self.star_rating <= 2:
                object.__setattr__(self, 'moderation_status', ModerationStatus.REQUIRES_APPROVAL)
            else:
                object.__setattr__(self, 'moderation_status', ModerationStatus.AUTO_APPROVED)

    def requires_human_review(self) -> bool:
        return self.moderation_status == ModerationStatus.REQUIRES_APPROVAL

    def is_auto_approved(self) -> bool:
        return self.moderation_status == ModerationStatus.AUTO_APPROVED

    def update_reply(self, new_reply: str) -> None:
        self.generated_reply = new_reply

    def override_moderation(self, new_status: ModerationStatus) -> None:
        object.__setattr__(self, 'moderation_status', new_status)