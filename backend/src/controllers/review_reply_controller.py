"""
Review Reply Controller.
Handles HTTP request/response logic for AI reply generation.
"""

from fastapi import HTTPException
from pydantic import BaseModel, Field

from src.repositories.database import get_db
from src.services.review_reply_service import ReviewReplyService


class ReviewReplyGenerateRequest(BaseModel):
    """Request body for generating a review reply."""
    customer_name: str = Field(..., max_length=80)
    star_rating: int = Field(..., ge=1, le=5)
    review_text: str


class GeneratedReplyResponse(BaseModel):
    """Response containing the generated reply and moderation status."""
    generated_reply: str
    moderation_status: str


class ReviewReplyActionResponse(BaseModel):
    """Response wrapper for reply generation."""
    reply: GeneratedReplyResponse


class ReviewReplyController:
    def __init__(self, db):
        self.db = db
        self.service = ReviewReplyService(db)

    async def generate(self, payload: ReviewReplyGenerateRequest) -> ReviewReplyActionResponse:
        try:
            result = await self.service.generate_and_save(
                customer_name=payload.customer_name,
                star_rating=payload.star_rating,
                review_text=payload.review_text
            )
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))