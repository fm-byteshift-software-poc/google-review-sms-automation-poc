"""
Submission Router.
Defines the HTTP endpoints and maps them to the Controller layer.
"""

from fastapi import APIRouter, Depends
from typing import List

from sqlalchemy.orm import Session

from src.repositories.database import get_db
from src.controllers.submission_controller import (
    SubmissionController,
    SubmissionCreateRequest,
    SubmissionActionResponse,
    SubmissionResponse
)

# Router Configuration
# Prefix matches the API Contract (/api/submissions)
router = APIRouter(
    prefix="/api/submissions",
    tags=["Submissions"],
    responses={404: {"description": "Submission not found"}},
)


# Dependency Injection for the Controller
# This ensures a new Controller instance with a fresh DB session is created per request
def get_submission_controller(db: Session = Depends(get_db)) -> SubmissionController:
    return SubmissionController(db)


# ==============================================================================
# Endpoints
# ==============================================================================

@router.post("/", response_model=SubmissionActionResponse)
async def create_submission(
    payload: SubmissionCreateRequest,
    controller: SubmissionController = Depends(get_submission_controller)
):
    """
    Create a new submission.
    Checks suppression rules and schedules SMS if allowed.
    """
    return await controller.create(payload)


@router.get("/", response_model=List[SubmissionResponse])
async def list_submissions(
    controller: SubmissionController = Depends(get_submission_controller)
):
    """
    Retrieve a list of recent submissions.
    """
    return await controller.list()


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    controller: SubmissionController = Depends(get_submission_controller)
):
    """
    Retrieve a specific submission by ID.
    """
    return await controller.get_by_id(submission_id)