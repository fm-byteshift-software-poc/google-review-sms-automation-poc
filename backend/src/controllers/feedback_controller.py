"""
Feedback Controller.
Handles HTTP request/response logic for feedback submission and retrieval.
"""

from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

from src.services.feedback_service import FeedbackService


class FeedbackCreateRequest(BaseModel):
    """Request body for submitting feedback."""
    submission_id: str
    satisfaction: str = Field(..., pattern="^(yes|no)$")
    private_feedback: Optional[str] = None


class FeedbackRecordResponse(BaseModel):
    """Standard feedback object in response."""
    id: str
    submission_id: str
    satisfaction: str
    private_feedback: Optional[str] = None
    alert_email_sent: bool
    created_at: str


class FeedbackActionResponse(BaseModel):
    """Response wrapper for feedback actions."""
    success: bool
    feedback: FeedbackRecordResponse


class FeedbackController:
    def __init__(self, db):
        self.db = db
        self.service = FeedbackService(db)

    async def create(self, payload: FeedbackCreateRequest) -> FeedbackActionResponse:
        try:
            result = self.service.create_feedback(
                submission_id=payload.submission_id,
                satisfaction=payload.satisfaction,
                private_feedback=payload.private_feedback
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def list(self, limit: int = 50) -> List[FeedbackRecordResponse]:
        try:
            return self.service.get_feedbacks(limit=limit)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_id(self, feedback_id: str) -> Optional[FeedbackRecordResponse]:
        try:
            return self.service.get_feedback_by_id(feedback_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
# """
# Feedback Controller.
# Handles HTTP request/response logic for feedback submission.
# """

# from fastapi import HTTPException
# from pydantic import BaseModel, Field
# from typing import Optional


# from src.repositories.database import get_db
# from src.services.feedback_service import FeedbackService


# class FeedbackCreateRequest(BaseModel):
#     """Request body for submitting feedback."""
#     submission_id: str
#     satisfaction: str = Field(..., pattern="^(yes|no)$")
#     private_feedback: Optional[str] = None


# class FeedbackResponse(BaseModel):
#     """Standard feedback object in response."""
#     id: str
#     submission_id: str
#     satisfaction: str
#     private_feedback: Optional[str] = None
#     alert_email_sent: bool


# class FeedbackActionResponse(BaseModel):
#     """Response wrapper for feedback actions."""
#     success: bool
#     feedback: FeedbackResponse


# class FeedbackController:
#     def __init__(self, db):
#         self.db = db
#         self.service = FeedbackService(db)

#     async def create(self, payload: FeedbackCreateRequest) -> FeedbackActionResponse:
#         try:
#             result = self.service.create_feedback(
#                 submission_id=payload.submission_id,
#                 satisfaction=payload.satisfaction,
#                 private_feedback=payload.private_feedback
#             )
#             return result
#         except ValueError as e:
#             raise HTTPException(status_code=400, detail=str(e))
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=str(e))