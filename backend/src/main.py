"""
Main Application Entry Point.
All internal imports use the 'src.' prefix as requested.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

# ==========================================
# Internal Imports (src. prefix)
# ==========================================
from src.routes.submission_router import router as submission_router
from src.routes.feedback_router import router as feedback_router
from src.routes.review_reply_router import router as review_reply_router

from src.repositories.database import SessionLocal, Base, engine
from src.middlewares.auth import APIKeyMiddleware
from src.config.settings import settings

from src.repositories.submission_repository import SubmissionRecord
from src.repositories.feedback_repository import FeedbackRecord
from src.repositories.review_reply_repository import ReviewReplyRecord

# ==========================================
# Security Scheme for Swagger UI
# ==========================================
# REQUIRED: This dependency renders the "Authorize" button in Swagger.
# auto_error=False prevents FastAPI from blocking the request,
# allowing our custom Middleware to handle the actual auth logic.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# ==========================================
# Application Initialization
# ==========================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    description="PoC for Google Review Workflow with Suppression Logic & AI Replies.",
    dependencies=[Depends(api_key_header)]  # Enables Swagger Authorize button
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Auth Middleware (Handles actual 401/403 logic)
app.add_middleware(APIKeyMiddleware, expected_key=settings.API_KEY.get_secret_value())

# Register Routers
app.include_router(submission_router)
app.include_router(feedback_router)
app.include_router(review_reply_router)

# ==========================================
# Seed Data Helper
# ==========================================
def seed_database():
    """Populates the database with required seed data."""
    db = SessionLocal()
    try:
        # Prevent duplicate seeding
        if db.query(SubmissionRecord).count() > 0:
            print("✅ Database already seeded.")
            return

        print("🌱 Seeding database...")

        # 1. Submissions
        sophia_sub = SubmissionRecord(first_name="Sophia", phone_number="+15550000003", status="satisfied", sms_sent=True, google_review_url=settings.GOOGLE_REVIEW_URL)
        daniel_sub = SubmissionRecord(first_name="Daniel", phone_number="+15550000004", status="dissatisfied", sms_sent=True, google_review_url=settings.GOOGLE_REVIEW_URL)

        submissions = [
            SubmissionRecord(first_name="Emma", phone_number="+15550000001", status="pending", sms_sent=True, google_review_url=settings.GOOGLE_REVIEW_URL),
            SubmissionRecord(first_name="Lucas", phone_number="+15550000002", status="suppressed", suppression_reason="Contacted within 90-day suppression window", google_review_url=settings.GOOGLE_REVIEW_URL),
            SubmissionRecord(first_name="Olivia", phone_number="+15550000005", status="pending", sms_sent=True, google_review_url=settings.GOOGLE_REVIEW_URL),
            SubmissionRecord(first_name="Noah", phone_number="+15550000006", status="suppressed", suppression_reason="Contacted within 90-day suppression window", google_review_url=settings.GOOGLE_REVIEW_URL),
            sophia_sub,
            daniel_sub
        ]
        db.add_all(submissions)
        db.flush()  # Assigns IDs for FK relationships

        # 2. Feedback
        db.add(FeedbackRecord(submission_id=sophia_sub.id, satisfaction="yes", private_feedback="Loved the service!", alert_email_sent=True))
        db.add(FeedbackRecord(submission_id=daniel_sub.id, satisfaction="no", private_feedback="The waiting time was too long.", alert_email_sent=True))

        # 3. Review Replies
        db.add(ReviewReplyRecord(customer_name="Emma", star_rating=5, review_text="Excellent service!", generated_reply="Thank you Emma.", moderation_status="auto-approved"))
        db.add(ReviewReplyRecord(customer_name="Lucas", star_rating=1, review_text="Terrible experience.", generated_reply="We are sorry to hear that Lucas.", moderation_status="requires-approval"))

        db.commit()
        print(f"✅ Database seeded successfully with {len(submissions)} submissions.")

    except Exception as e:
        print(f"❌ Seed Error: {e}")
        db.rollback()
    finally:
        db.close()

# ==========================================
# Startup Event
# ==========================================
@app.on_event("startup")
def startup_event():
    """Initialize DB tables and seed data on startup."""
    print(f"🚀 Starting {settings.APP_NAME}...")
    Base.metadata.create_all(bind=engine)
    seed_database()
    print(f"✅ Ready at http://0.0.0.0:8000")

@app.get("/health")
async def health_check():
    return {"status": "ok"}