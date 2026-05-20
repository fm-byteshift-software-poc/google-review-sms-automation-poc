"""
Review Reply Router.
Defines HTTP endpoints for AI-generated review replies.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.repositories.database import get_db
from src.controllers.review_reply_controller import (
    ReviewReplyController,
    ReviewReplyGenerateRequest,
    ReviewReplyActionResponse
)

router = APIRouter(
    prefix="/api/review-replies",
    tags=["Review Replies"],
    responses={404: {"description": "Not found"}},
)


def get_review_reply_controller(db: Session = Depends(get_db)) -> ReviewReplyController:
    return ReviewReplyController(db)


@router.post("/generate", response_model=ReviewReplyActionResponse)
async def generate_reply(
    payload: ReviewReplyGenerateRequest,
    controller: ReviewReplyController = Depends(get_review_reply_controller)
):
    """
    Generate an AI reply to a customer review.
    Applies moderation rules based on star rating.
    """
    return await controller.generate(payload)