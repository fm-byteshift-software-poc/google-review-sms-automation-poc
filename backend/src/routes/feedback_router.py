"""
Feedback Router.
Defines HTTP endpoints for feedback submission.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from src.repositories.database import get_db
from src.controllers.feedback_controller import (
    FeedbackController,
    FeedbackCreateRequest,
    FeedbackActionResponse,
    FeedbackRecordResponse
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


@router.get("/", response_model=List[FeedbackRecordResponse])
async def list_feedback(
    limit: int = Query(default=50, ge=1, le=200),
    controller: FeedbackController = Depends(get_feedback_controller)
):
    """
    List recent feedback records.
    """
    return await controller.list(limit=limit)


@router.get("/{feedback_id}", response_model=FeedbackRecordResponse)
async def get_feedback(
    feedback_id: str,
    controller: FeedbackController = Depends(get_feedback_controller)
):
    """
    Get a single feedback record by ID.
    """
    result = await controller.get_by_id(feedback_id)
    if not result:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")
    return result
# """
# Feedback Router.
# Defines HTTP endpoints for feedback submission.
# """

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from src.repositories.database import get_db
# from src.controllers.feedback_controller import (
#     FeedbackController,
#     FeedbackCreateRequest,
#     FeedbackActionResponse
# )

# router = APIRouter(
#     prefix="/api/feedback",
#     tags=["Feedback"],
#     responses={404: {"description": "Not found"}},
# )


# def get_feedback_controller(db: Session = Depends(get_db)) -> FeedbackController:
#     return FeedbackController(db)


# @router.post("/", response_model=FeedbackActionResponse)
# async def create_feedback(
#     payload: FeedbackCreateRequest,
#     controller: FeedbackController = Depends(get_feedback_controller)
# ):
#     """
#     Submit feedback for a submission.
#     Branches: if 'no', triggers alert email.
#     """
#     return await controller.create(payload)