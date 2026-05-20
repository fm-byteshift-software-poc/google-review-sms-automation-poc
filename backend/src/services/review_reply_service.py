"""
Review Reply Service Layer.
Orchestrates LLM generation, moderation logic, and persistence.
PoC-focused: Simple flow from input -> AI -> Save -> Response.
"""

import logging
from typing import Dict, Any

from src.models.review_reply import ReviewReply
from src.repositories.review_reply_repository import ReviewReplyRepository
from src.services.openai_service import OpenAIService


class ReviewReplyService:
    """
    Service for handling AI review reply generation.
    """

    def __init__(self, db):
        self.repo = ReviewReplyRepository(db)
        self.ai_service = OpenAIService()

    async def generate_and_save(
        self,
        customer_name: str,
        star_rating: int,
        review_text: str
    ) -> Dict[str, Any]:
        """
        1. Calls OpenAI Service (HuggingFace Router) to generate reply.
        2. Creates ReviewReply entity (which applies moderation rules).
        3. Persists the reply.
        4. Returns the formatted response.
        """
        # 1. Generate text via LLM
        # We use the AI service to get the text content.
        # Note: OpenAIService also returns moderation status, but the Domain Entity 
        # is the source of truth for status based on star_rating.
        generated_text, _ = await self.ai_service.generate_reply(
            customer_name,
            star_rating,
            review_text
        )

        # 2. Create Domain Entity
        # The __post_init__ in ReviewReply automatically sets the moderation_status
        # based on the star_rating (1-2 = requires-approval, 4-5 = auto-approved).
        reply_entity = ReviewReply(
            customer_name=customer_name,
            star_rating=star_rating,
            review_text=review_text,
            generated_reply=generated_text
        )

        # 3. Persist
        try:
            saved_reply = self.repo.create(reply_entity)
        except Exception as e:
            logging.error(f"❌ Failed to save review reply: {e}")
            raise

        # 4. Return response matching API Contract
        return {
            "reply": {
                "generated_reply": saved_reply.generated_reply,
                "moderation_status": saved_reply.moderation_status.value
            }
        }