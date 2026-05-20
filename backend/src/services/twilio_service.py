"""
Twilio Service Layer.
Wrapper around Twilio SDK for SMS dispatch.
Handles simulation mode for PoC validation without real credentials.
"""

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from src.config.settings import settings
import logging


class TwilioService:
    """
    Service for sending SMS messages via Twilio.
    """

    def __init__(self):
        """
        Initialize Twilio Client if credentials are present.
        Otherwise, initialize in Simulation Mode to allow PoC testing.
        """
        self.is_simulation = True
        self.client = None

        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                self.is_simulation = False
                logging.info("✅ Twilio SDK initialized successfully.")
            except Exception as e:
                logging.error(f"❌ Failed to initialize Twilio SDK: {e}")
                logging.warning("⚠️  Falling back to SIMULATION mode.")

    def send_sms(self, to: str, body: str) -> tuple[bool, str]:
        """
        Send an SMS to the specified number.

        Args:
            to: Recipient phone number.
            body: Message content.

        Returns:
            tuple: (success: bool, message_sid: str)
        """
        if self.is_simulation:
            # Simulation Logic for PoC
            logging.info(f"📱 [SIMULATION] SMS to {to}: {body}")
            return True, "sim-msg-" + to[-4:]
        
        # Real Twilio Logic
        try:
            message = self.client.messages.create(
                body=body,
                from_=settings.TWILIO_FROM_NUMBER,
                to=to
            )
            logging.info(f"✅ SMS sent via Twilio. SID: {message.sid}")
            return True, message.sid
        except TwilioRestException as e:
            logging.error(f"❌ Twilio API Error: {e}")
            return False, ""