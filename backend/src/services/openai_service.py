"""
OpenAI Service Layer (HuggingFace Router Adapter).
Wrapper for LLM interactions using OpenAI-compatible client pointing to HuggingFace.
Handles review reply generation with rule-based moderation.
"""

import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from src.config.settings import settings

# System prompt for review reply generation
LLM_SYSTEM_PROMPT = """You are a professional customer service assistant for a business.
Generate a concise, warm, and professional reply to a customer review.
- Keep replies under 3 sentences
- Use the customer's name if provided
- Match the tone to the star rating (grateful for 4-5 stars, empathetic for 1-2 stars)
- Do not include placeholders like [Name] or [Company]
- Output ONLY the reply text, no JSON, no markdown, no explanations"""


class OpenAIService:
    """
    Service for LLM interactions via HuggingFace Router.
    Uses AsyncOpenAI client for compatibility with HuggingFace's OpenAI-compatible endpoint.
    """

    def __init__(self):
        """
        Initialize AsyncOpenAI client pointing to HuggingFace Router.
        Falls back to simulation mode if API token is not configured.
        """
        self.is_simulation = True
        self.client = None
        self.model = "meta-llama/Llama-3.1-8B-Instruct:cerebras"

        if settings.OPENAI_API_KEY:  # Reusing OPENAI_API_KEY env var for HF token
            try:
                self.client = AsyncOpenAI(
                    base_url="https://router.huggingface.co/v1",
                    api_key=settings.OPENAI_API_KEY
                )
                self.is_simulation = False
                logging.info(f"✅ OpenAI-compatible client initialized for model: {self.model}")
            except Exception as e:
                logging.error(f"❌ Failed to initialize LLM client: {e}")
                logging.warning("⚠️  Falling back to SIMULATION mode.")
        else:
            logging.warning("⚠️  OPENAI_API_KEY not configured. Running in SIMULATION mode.")

    async def generate_reply(
        self,
        customer_name: str,
        star_rating: int,
        review_text: str
    ) -> tuple[str, str]:
        """
        Generate a reply to a customer review and determine moderation status.

        Args:
            customer_name: Name of the customer who left the review
            star_rating: Integer rating from 1 to 5
            review_text: The full text of the customer's review

        Returns:
            tuple: (generated_reply: str, moderation_status: str)
            moderation_status is either "auto-approved" or "requires-approval"
        """
        # Rule-based moderation (per spec: 4-5 = auto, 1-2 = manual)
        if star_rating >= 4:
            moderation_status = "auto-approved"
        elif star_rating <= 2:
            moderation_status = "requires-approval"
        else:
            moderation_status = "auto-approved"  # 3 stars defaults to auto

        if self.is_simulation:
            # Simulation Logic for PoC
            reply = self._generate_simulated_reply(customer_name, star_rating, review_text)
            logging.info(f"🤖 [SIMULATION] Generated reply for {customer_name} ({star_rating}★): {reply[:50]}...")
            return reply, moderation_status
        
        # Real LLM Call via HuggingFace Router
        try:
            user_prompt = f"""Customer: {customer_name}
Rating: {star_rating}/5 stars
Review: {review_text}

Generate a professional reply:"""
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=150,
                temperature=0.7,
            )
            generated_reply = completion.choices[0].message.content.strip()
            logging.info(f"✅ LLM reply generated via HuggingFace Router")
            return generated_reply, moderation_status
            
        except Exception as e:
            logging.error(f"❌ LLM API Error: {e}")
            # Fallback to simulation on error to keep PoC functional
            reply = self._generate_simulated_reply(customer_name, star_rating, review_text)
            return reply, moderation_status
            
        finally:
            if self.client and not self.is_simulation:
                await self.client.close()

    def _generate_simulated_reply(self, name: str, rating: int, review: str) -> str:
        """
        Generate a deterministic simulated reply for PoC testing without API calls.
        """
        if rating >= 4:
            return f"Thank you {name} for your kind words and {rating}-star rating! We're thrilled you had a great experience."
        elif rating == 3:
            return f"Hi {name}, thanks for your feedback. We appreciate you taking the time to share your experience."
        else:
            return f"Hi {name}, we sincerely apologize for not meeting your expectations. Your feedback helps us improve, and we'd love the chance to make it right."

    async def close(self):
        """
        Explicitly close the async client if initialized.
        """
        if self.client and not self.is_simulation:
            await self.client.close()