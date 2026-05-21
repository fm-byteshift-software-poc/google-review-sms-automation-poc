"""
Review Reply Repository.
Data access layer for the Review Reply domain entity.
"""

import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Enum, DateTime, Text, func, select
from sqlalchemy.dialects.sqlite import CHAR
from sqlalchemy.orm import Session

from src.repositories.database import Base
from src.models.review_reply import ReviewReply, ModerationStatus


class ReviewReplyRecord(Base):
    """SQLAlchemy table definition for review replies."""
    __tablename__ = "review_replies"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String(255), nullable=False)
    star_rating = Column(String(1), nullable=False)  # Store as string for enum compatibility
    review_text = Column(Text, nullable=False)
    generated_reply = Column(Text, nullable=False)
    moderation_status = Column(Enum("auto-approved", "requires-approval", name="moderation_enum"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ReviewReplyRepository:
    """Repository for managing Review Reply persistence."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, reply: ReviewReply) -> ReviewReply:
        record = ReviewReplyRecord(
            id=reply.id,
            customer_name=reply.customer_name,
            star_rating=str(reply.star_rating),
            review_text=reply.review_text,
            generated_reply=reply.generated_reply,
            moderation_status=reply.moderation_status.value,
            created_at=reply.created_at
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._to_domain(record)

    def get_by_id(self, reply_id: str) -> Optional[ReviewReply]:
        stmt = select(ReviewReplyRecord).where(ReviewReplyRecord.id == reply_id)
        record = self.db.execute(stmt).scalar_one_or_none()
        return self._to_domain(record) if record else None

    def list_recent(self, limit: int = 50) -> List[ReviewReply]:
        stmt = select(ReviewReplyRecord).order_by(ReviewReplyRecord.created_at.desc()).limit(limit)
        records = self.db.execute(stmt).scalars().all()
        return [self._to_domain(r) for r in records]

    @staticmethod
    def _to_domain(record: ReviewReplyRecord) -> ReviewReply:
        return ReviewReply(
            id=record.id,
            customer_name=record.customer_name,
            star_rating=int(record.star_rating),
            review_text=record.review_text,
            generated_reply=record.generated_reply,
            moderation_status=ModerationStatus(record.moderation_status),
            created_at=record.created_at
        )

# """
# ReviewReply Repository.
# Minimal data access layer for AI-generated review replies.
# PoC-focused: basic CRUD + domain mapping.
# """

# import uuid
# from datetime import datetime
# from typing import Optional, List

# from sqlalchemy import Column, String, Integer, Enum, DateTime, Text, func, select, desc
# from sqlalchemy.dialects.sqlite import CHAR
# from sqlalchemy.orm import Session

# from src.repositories.database import Base
# from src.models.review_reply import ReviewReply, ModerationStatus


# # ==============================================================================
# # SQLAlchemy ORM Model (Persistence Layer)
# # ==============================================================================
# class ReviewReplyRecord(Base):
#     __tablename__ = "review_replies"

#     id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     customer_name = Column(String(80), nullable=False)
#     star_rating = Column(Integer, nullable=False)
#     review_text = Column(Text, nullable=False)
#     generated_reply = Column(Text, nullable=False)
#     moderation_status = Column(Enum("auto-approved", "requires-approval", name="moderation_enum"), nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())


# # ==============================================================================
# # Repository Implementation
# # ==============================================================================
# class ReviewReplyRepository:
#     def __init__(self, db: Session):
#         self.db = db

#     def create(self, reply: ReviewReply) -> ReviewReply:
#         record = ReviewReplyRecord(
#             id=reply.id,
#             customer_name=reply.customer_name,
#             star_rating=reply.star_rating,
#             review_text=reply.review_text,
#             generated_reply=reply.generated_reply,
#             moderation_status=reply.moderation_status.value,
#             created_at=reply.created_at
#         )
#         self.db.add(record)
#         self.db.commit()
#         self.db.refresh(record)
#         return self._to_domain(record)

#     def get_by_id(self, reply_id: str) -> Optional[ReviewReply]:
#         stmt = select(ReviewReplyRecord).where(ReviewReplyRecord.id == reply_id)
#         record = self.db.execute(stmt).scalar_one_or_none()
#         return self._to_domain(record) if record else None

#     def list_recent(self, limit: int = 10) -> List[ReviewReply]:
#         stmt = select(ReviewReplyRecord).order_by(desc(ReviewReplyRecord.created_at)).limit(limit)
#         records = self.db.execute(stmt).scalars().all()
#         return [self._to_domain(r) for r in records]

#     @staticmethod
#     def _to_domain(record: ReviewReplyRecord) -> ReviewReply:
#         return ReviewReply(
#             id=record.id,
#             customer_name=record.customer_name,
#             star_rating=record.star_rating,
#             review_text=record.review_text,
#             generated_reply=record.generated_reply,
#             moderation_status=ModerationStatus(record.moderation_status),
#             created_at=record.created_at
#         )