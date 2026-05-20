"""
Resend Service Layer.
Wrapper around Resend SDK for transactional email dispatch.
Handles alert emails for dissatisfied feedback with simulation fallback.
"""

import resend
import logging
from src.config.settings import settings


class ResendService:
    """
    Service for sending alert emails via Resend.
    """

    def __init__(self):
        """
        Initialize Resend SDK if API key is present.
        Falls back to simulation mode for local/PoC testing.
        """
        self.is_simulation = True
        
        if settings.RESEND_API_KEY:
            try:
                resend.api_key = settings.RESEND_API_KEY
                self.is_simulation = False
                logging.info("✅ Resend SDK initialized successfully.")
            except Exception as e:
                logging.error(f"❌ Failed to initialize Resend SDK: {e}")
                logging.warning("️ Falling back to SIMULATION mode.")
        else:
            logging.warning("⚠️ RESEND_API_KEY not configured. Running in SIMULATION mode.")

    def send_alert_email(self, to: str, subject: str, body_html: str) -> tuple[bool, str]:
        """
        Send an alert email to the specified recipient.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body_html: HTML content of the email.

        Returns:
            tuple: (success: bool, message_id: str)
        """
        if self.is_simulation:
            # Simulation Logic for PoC
            logging.info(f"📧 [SIMULATION] Email to {to} | Subject: {subject}")
            logging.debug(f"   Body preview: {body_html[:100]}...")
            return True, "sim-email-" + to.split("@")[0]
        
        # Real Resend Logic
        try:
            email = resend.Emails.send({
                "from": f"onboarding@resend.dev",
                "to": [to],
                "subject": subject,
                "html": body_html
            })
            logging.info(f"✅ Alert email sent via Resend. ID: {email.id}")
            return True, email.id
        except Exception as e:
            logging.error(f"❌ Resend API Error: {e}")
            return False, ""