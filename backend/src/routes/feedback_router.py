"""
Feedback Router.
Defines HTTP endpoints for feedback submission.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.repositories.database import get_db
from src.controllers.feedback_controller import (
    FeedbackController,
    FeedbackCreateRequest,
    FeedbackActionResponse
)

router = APIRouter(
    prefix="/api/feedback",
    tags=["Feedback"],
    responses={404: {"description": "Not found"}},
)


def get_feedback_controller(db: Session = Depends(get_db)) -> FeedbackController:
    return FeedbackController(db)


@router.post("/", response_model=FeedbackActionResponse)
async def create_feedback(
    payload: FeedbackCreateRequest,
    controller: FeedbackController = Depends(get_feedback_controller)
):
    """
    Submit feedback for a submission.
    Branches: if 'no', triggers alert email.
    """
    return await controller.create(payload)