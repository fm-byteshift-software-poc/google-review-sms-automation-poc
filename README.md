# Google Review Workflow PoC

Backend API that automates review request **WhatsApp messages**, enforces contact suppression, handles satisfaction feedback, and generates AI-moderated review responses.

## Tech Stack

- Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2
- Twilio (WhatsApp API), Resend (Email), HuggingFace Router (LLM)
- SQLite (Local persistence)

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure your credentials.
3. Run the server: `uvicorn src.main:app --reload`

## Environment Variables

| Variable                                                        | Description                                    |
| --------------------------------------------------------------- | ---------------------------------------------- |
| `API_KEY`                                                       | 12-character key for endpoint authentication   |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | Twilio credentials (WhatsApp Sender ID)        |
| `RESEND_API_KEY`, `RESEND_ALERT_EMAIL`                          | Resend email credentials                       |
| `OPENAI_API_KEY`                                                | HuggingFace Router token (LLM)                 |
| `GOOGLE_REVIEW_URL`                                             | Target Google review link                      |
| `SUPPRESSION_WINDOW_DAYS`                                       | Days to block duplicate messages (default: 90) |

## Testing

- Open Swagger UI: `http://localhost:8000/docs`
- Click **Authorize**, enter your 12-char `API_KEY`, and close the modal.
- Use **Try it out** on any endpoint to execute requests.

## Core Workflow

1. **WhatsApp Request:** `POST /api/submissions` sends a WhatsApp message or blocks via 90-day suppression rule.
2. **Feedback:** `POST /api/feedback` records satisfaction. `"no"` triggers an alert email via Resend.
3. **AI Reply:** `POST /api/review-replies/generate` creates LLM responses with rule-based moderation (auto-approved for 4-5 stars, requires approval for 1-2 stars).

## Notes

- Twilio, Resend, and LLM services automatically fallback to simulation mode if credentials are missing.
- SQLite database (`app.db`) and seed data are created automatically on first run.

---

## 👤 Maintained By

This project is developed and maintained by **FM ByteShift Software**

**Fernando Magalhães**  
CEO – FM ByteShift Software  
📞 (21) 97250-1546  
✉️ [contact@fmbyteshiftsoftware.com](mailto:contact@fmbyteshiftsoftware.com)  
🌐 [fmbyteshiftsoftware.com](https://fmbyteshiftsoftware.com)  
🏢 CNPJ: 62.145.022/0001-05 (Brazil)
