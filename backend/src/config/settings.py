from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, field_validator
from pathlib import Path
import secrets
import string
import os

class Settings(BaseSettings):
    APP_NAME: str = "Google Review Workflow PoC"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # Security
    API_KEY: SecretStr = Field(default_factory=lambda: "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12)))
    
    # Database - AVALIADO APÓS carregamento do .env via property
    _db_path: str = ""
    
    # External Services
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_FROM_NUMBER: str | None = None
    RESEND_API_KEY: str | None = None
    RESEND_ALERT_EMAIL: str | None = None
    OPENAI_API_KEY: str | None = None
    
    # Business Logic
    GOOGLE_REVIEW_URL: str = "https://g.page/r/YOUR_REVIEW_LINK/review"
    SUPPRESSION_WINDOW_DAYS: int = 90

    model_config = {
        "env_file": str(Path.cwd() / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }

    @field_validator("API_KEY", mode="before")
    @classmethod
    def validate_api_key_length(cls, v):
        if isinstance(v, str) and len(v) != 12:
            raise ValueError("API_KEY must be exactly 12 characters")
        return v
    
    @property
    def DATABASE_URL(self) -> str:
        """Lazy evaluation to ensure cwd is correct at runtime."""
        if not self._db_path:
            self._db_path = f"sqlite:///{Path.cwd() / 'app.db'}"
        return self._db_path

# ⚡ INSTÂNCIA GLOBAL
settings = Settings()

# 🔍 LOG CIRÚRGICO COMPLETO (Mascarado para segurança)
def mask(s: str | None, visible: int = 4) -> str:
    if not s: return "⚠️ NOT SET"
    if len(s) <= visible: return "*" * len(s)
    return s[:visible] + "*" * (len(s) - visible)

print("\n" + "=" * 70)
print(" 🔐 STARTUP: Environment Variables Loaded")
print("=" * 70)
print(f"📁 .env file path      : {Path.cwd() / '.env'}")
print(f"✅ .env exists?         : {os.path.exists(Path.cwd() / '.env')}")
print(f"🔑 API_KEY             : '{settings.API_KEY.get_secret_value()}' (len={len(settings.API_KEY.get_secret_value())})")
print(f"📱 TWILIO_ACCOUNT_SID  : {mask(settings.TWILIO_ACCOUNT_SID)}")
print(f"🔐 TWILIO_AUTH_TOKEN   : {mask(settings.TWILIO_AUTH_TOKEN)}")
print(f"📞 TWILIO_FROM_NUMBER  : {settings.TWILIO_FROM_NUMBER or '⚠️ NOT SET'}")
print(f"📧 RESEND_API_KEY      : {mask(settings.RESEND_API_KEY)}")
print(f"🤖 OPENAI_API_KEY      : {mask(settings.OPENAI_API_KEY)}")
print(f"🔗 GOOGLE_REVIEW_URL   : {settings.GOOGLE_REVIEW_URL}")
print("=" * 70 + "\n")

# ⚠️ ALERTA SE TWILIO ESTIVER INCOMPLETO
if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
    print("⚠️  WARNING: Twilio credentials incomplete. SMS will run in SIMULATION mode.\n")
elif not settings.TWILIO_FROM_NUMBER:
    print("⚠️  WARNING: TWILIO_FROM_NUMBER not set. SMS may fail.\n")
else:
    print("✅ Twilio credentials appear complete. Attempting real SMS...\n")