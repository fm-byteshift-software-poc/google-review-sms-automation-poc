"""
Submission Controller.
Handles HTTP request/response logic, Pydantic validation, and routes calls to the Service layer.
"""

from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional

from src.repositories.database import get_db
from src.services.submission_service import SubmissionService


# ==============================================================================
# Pydantic Schemas (Data Transfer Objects)
# ==============================================================================

class SubmissionCreateRequest(BaseModel):
    """Request body for creating a new submission."""
    first_name: str = Field(..., max_length=80, description="Customer first name")
    phone_number: str = Field(..., description="Customer phone number")


class SubmissionResponse(BaseModel):
    """Standard submission object in response."""
    id: str
    first_name: str
    phone_number: str
    status: str
    suppression_reason: Optional[str] = None
    google_review_url: Optional[str] = None
    sms_sent: bool
    sms_sent_at: Optional[str] = None
    created_at: str
    feedback: Optional[dict] = None


class SubmissionActionResponse(BaseModel):
    """Response wrapper for submission actions."""
    status: str
    message: str
    submission: SubmissionResponse


# ==============================================================================
# Controller Implementation
# ==============================================================================

class SubmissionController:
    """
    FastAPI Controller for Submission endpoints.
    """

    def __init__(self, db):
        self.db = db
        self.service = SubmissionService(db)

    async def create(self, payload: SubmissionCreateRequest):
        """
        Handles POST /api/submissions
        1. Validates input
        2. Calls Service to check suppression rules
        3. Returns appropriate response based on service result
        """
        try:
            result = self.service.create_submission(
                first_name=payload.first_name,
                phone_number=payload.phone_number
            )
            # The service returns a dict matching the API contract perfectly
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def list(self):
        """
        Handles GET /api/submissions
        Returns a list of recent submissions.
        """
        try:
            submissions = self.service.get_submissions()
            return submissions
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_id(self, submission_id: str):
        """
        Handles GET /api/submissions/{id}
        Returns a single submission details.
        """
        submission = self.service.get_submission_by_id(submission_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        return submission