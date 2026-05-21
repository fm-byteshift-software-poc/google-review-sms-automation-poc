"""
Review Reply Router.
Defines HTTP endpoints for AI-generated review replies.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from src.repositories.database import get_db
from src.controllers.review_reply_controller import (
    ReviewReplyController,
    ReviewReplyGenerateRequest,
    ReviewReplyResponse
)

router = APIRouter(
    prefix="/api/review-replies",
    tags=["Review Replies"],
    responses={404: {"description": "Not found"}},
)


def get_controller(db: Session = Depends(get_db)) -> ReviewReplyController:
    return ReviewReplyController(db)


@router.post("/generate", response_model=ReviewReplyResponse, status_code=status.HTTP_201_CREATED)
async def generate_reply(
    payload: ReviewReplyGenerateRequest,
    controller: ReviewReplyController = Depends(get_controller)
):
    """
    Generate an AI-powered reply to a customer review.
    Applies rule-based moderation (auto-approve for 4-5 stars, requires approval for 1-2 stars).
    """
    return await controller.generate(payload)


@router.get("/", response_model=List[ReviewReplyResponse])
async def list_replies(
    limit: int = Query(default=50, ge=1, le=200),
    controller: ReviewReplyController = Depends(get_controller)
):
    """
    List recent generated review replies.
    """
    return await controller.list(limit=limit)


@router.get("/{reply_id}", response_model=ReviewReplyResponse)
async def get_reply(
    reply_id: str,
    controller: ReviewReplyController = Depends(get_controller)
):
    """
    Get a single review reply by ID.
    """
    result = await controller.get_by_id(reply_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found")
    return result

# """
# Review Reply Router.
# Defines HTTP endpoints for AI-generated review replies.
# """

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from src.repositories.database import get_db
# from src.controllers.review_reply_controller import (
#     ReviewReplyController,
#     ReviewReplyGenerateRequest,
#     ReviewReplyActionResponse
# )

# router = APIRouter(
#     prefix="/api/review-replies",
#     tags=["Review Replies"],
#     responses={404: {"description": "Not found"}},
# )


# def get_review_reply_controller(db: Session = Depends(get_db)) -> ReviewReplyController:
#     return ReviewReplyController(db)


# @router.post("/generate", response_model=ReviewReplyActionResponse)
# async def generate_reply(
#     payload: ReviewReplyGenerateRequest,
#     controller: ReviewReplyController = Depends(get_review_reply_controller)
# ):
#     """
#     Generate an AI reply to a customer review.
#     Applies moderation rules based on star rating.
#     """
#     return await controller.generate(payload)