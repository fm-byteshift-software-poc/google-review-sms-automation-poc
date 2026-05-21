
"""
Review Reply Service Layer.
Orchestrates AI reply generation and rule-based moderation.
"""

from typing import Optional, List, Dict, Any

from src.models.review_reply import ReviewReply, ModerationStatus
from src.repositories.review_reply_repository import ReviewReplyRepository


class ReviewReplyService:
    """
    High-level service for managing Review Reply workflows.
    Handles AI generation and moderation logic.
    """

    def __init__(self, db):
        self.repository = ReviewReplyRepository(db)

    def generate_reply(
        self,
        customer_name: str,
        star_rating: int,
        review_text: str
    ) -> Dict[str, Any]:
        """
        Generates an AI-powered reply and applies moderation rules.
        - 4-5 stars: Auto-approved
        - 1-2 stars: Requires approval
        - 3 stars: Auto-approved (neutral)
        """
        # Generate reply text (simulation or AI)
        generated_reply = self._generate_reply_text(customer_name, star_rating, review_text)
        
        # Determine moderation status
        if star_rating >= 4:
            moderation_status = ModerationStatus.AUTO_APPROVED
        elif star_rating <= 2:
            moderation_status = ModerationStatus.REQUIRES_APPROVAL
        else:
            moderation_status = ModerationStatus.AUTO_APPROVED

        # Create entity
        reply = ReviewReply(
            customer_name=customer_name,
            star_rating=star_rating,
            review_text=review_text,
            generated_reply=generated_reply,
            moderation_status=moderation_status
        )

        # Persist
        saved_reply = self.repository.create(reply)
        
        return self._serialize_reply(saved_reply)

    def get_reply_by_id(self, reply_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single review reply."""
        reply = self.repository.get_by_id(reply_id)
        if not reply:
            return None
        return self._serialize_reply(reply)

    def get_replies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent review replies."""
        replies = self.repository.list_recent(limit)
        return [self._serialize_reply(r) for r in replies]

    def _generate_reply_text(self, customer_name: str, star_rating: int, review_text: str) -> str:
        """
        Generates a contextual reply.
        In production, this would call an LLM API.
        """
        if star_rating >= 4:
            return f"Thank you {customer_name} for your wonderful feedback! We're thrilled you enjoyed your experience with us. We look forward to serving you again soon!"
        elif star_rating <= 2:
            return f"Dear {customer_name}, we sincerely apologize for not meeting your expectations. Your feedback is important to us, and we'd like to make this right. Please reach out to us directly so we can address your concerns."
        else:
            return f"Thank you {customer_name} for your feedback. We appreciate you taking the time to share your experience and will use your input to improve our service."

    @staticmethod
    def _serialize_reply(reply: ReviewReply) -> Dict[str, Any]:
        """Converts Domain Entity to Dict."""
        return {
            "id": reply.id,
            "customer_name": reply.customer_name,
            "star_rating": reply.star_rating,
            "review_text": reply.review_text,
            "generated_reply": reply.generated_reply,
            "moderation_status": reply.moderation_status.value,
            "created_at": reply.created_at.isoformat() if reply.created_at else None
        }
# """
# Review Reply Service Layer.
# Orchestrates LLM generation, moderation logic, and persistence.
# PoC-focused: Simple flow from input -> AI -> Save -> Response.
# """

# import logging
# from typing import Dict, Any

# from src.models.review_reply import ReviewReply
# from src.repositories.review_reply_repository import ReviewReplyRepository
# from src.services.openai_service import OpenAIService


# class ReviewReplyService:
#     """
#     Service for handling AI review reply generation.
#     """

#     def __init__(self, db):
#         self.repo = ReviewReplyRepository(db)
#         self.ai_service = OpenAIService()

#     async def generate_and_save(
#         self,
#         customer_name: str,
#         star_rating: int,
#         review_text: str
#     ) -> Dict[str, Any]:
#         """
#         1. Calls OpenAI Service (HuggingFace Router) to generate reply.
#         2. Creates ReviewReply entity (which applies moderation rules).
#         3. Persists the reply.
#         4. Returns the formatted response.
#         """
#         # 1. Generate text via LLM
#         # We use the AI service to get the text content.
#         # Note: OpenAIService also returns moderation status, but the Domain Entity 
#         # is the source of truth for status based on star_rating.
#         generated_text, _ = await self.ai_service.generate_reply(
#             customer_name,
#             star_rating,
#             review_text
#         )

#         # 2. Create Domain Entity
#         # The __post_init__ in ReviewReply automatically sets the moderation_status
#         # based on the star_rating (1-2 = requires-approval, 4-5 = auto-approved).
#         reply_entity = ReviewReply(
#             customer_name=customer_name,
#             star_rating=star_rating,
#             review_text=review_text,
#             generated_reply=generated_text
#         )

#         # 3. Persist
#         try:
#             saved_reply = self.repo.create(reply_entity)
#         except Exception as e:
#             logging.error(f"❌ Failed to save review reply: {e}")
#             raise

#         # 4. Return response matching API Contract
#         return {
#             "reply": {
#                 "generated_reply": saved_reply.generated_reply,
#                 "moderation_status": saved_reply.moderation_status.value
#             }
#         }