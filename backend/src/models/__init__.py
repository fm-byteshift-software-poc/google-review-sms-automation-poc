"""
Domain Models Package.
Exposes core business entities to the rest of the application.
"""

from .submission import Submission, SubmissionStatus

__all__ = [
    "Submission",
    "SubmissionStatus",
]