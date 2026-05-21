# Google Review Workflow PoC

Full-stack application that automates review request WhatsApp messages, enforces contact suppression, handles satisfaction feedback, and generates AI-moderated review responses.

## Tech Stack

**Backend**

- Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic v2
- Twilio (WhatsApp API), Resend (Email), rule-based AI engine (LLM-ready)
- SQLite (local persistence)

**Frontend**

- React 19, TypeScript, Vite
- TailwindCSS 4, DaisyUI 5
- React Router DOM, Lucide React icons

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # configure your credentials
uvicorn src.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env  # set VITE_API_KEY
npm run dev
```

Access the app at `http://localhost:3000`. The Vite proxy forwards `/api` requests to `http://localhost:8000`.

## Environment Variables

### Backend (.env)

| Variable                                                        | Description                                           |
| --------------------------------------------------------------- | ----------------------------------------------------- |
| `API_KEY`                                                       | 12-character key for endpoint authentication          |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | Twilio WhatsApp credentials                           |
| `RESEND_API_KEY`, `RESEND_ALERT_EMAIL`                          | Resend email credentials                              |
| `GOOGLE_REVIEW_URL`                                             | Target Google review link (sent in WhatsApp messages) |
| `SUPPRESSION_WINDOW_DAYS`                                       | Days to block duplicate messages (default: 90)        |

### Frontend (.env)

| Variable       | Description                                           |
| -------------- | ----------------------------------------------------- |
| `VITE_API_KEY` | Same 12-character key used for backend authentication |

## Testing

**Backend API**

- Open Swagger UI: `http://localhost:8000/docs`
- Click **Authorize**, enter your `API_KEY`, and test endpoints directly

**Frontend UI**

- Navigate to `http://localhost:3000`
- Use the Submissions tab to send WhatsApp requests
- Use the Feedback tab to simulate customer responses
- Use the AI Replies tab to generate moderated review responses

## Core Workflow

1. **WhatsApp Request** (`POST /api/submissions`): Sends a WhatsApp message via Twilio or blocks via 90-day suppression rule. Phone numbers must use E.164 format with `whatsapp:` prefix (e.g., `whatsapp:+5521972501546`).

2. **Feedback Recording** (`POST /api/feedback`): Staff manually records customer satisfaction after offline interaction. `"no"` triggers an automated alert email via Resend.

3. **AI Reply Generation** (`POST /api/review-replies/generate`): Creates contextual review responses with rule-based moderation: auto-approved for 4-5 stars, requires manual review for 1-2 stars.

## Google Business Profile Integration Note

This PoC does not integrate the Google Business Profile API. The `GOOGLE_REVIEW_URL` is included in WhatsApp messages as a direct link to your public review page. Customer interaction with the link happens outside the system. The Feedback tab simulates the outcome of that interaction for workflow validation. Production integration with Google Business Profile can be added once core logic is validated.

## Simulation Mode

Twilio, Resend, and LLM services automatically fallback to simulation mode if credentials are missing or invalid. This allows full workflow testing without external API dependencies during development.

---

## 👤 Maintained By

This project is developed and maintained by **FM ByteShift Software**

**Fernando Magalhães**  
CEO – FM ByteShift Software  
📞 (21) 97250-1546  
✉️ [contact@fmbyteshiftsoftware.com](mailto:contact@fmbyteshiftsoftware.com)  
🌐 [fmbyteshiftsoftware.com](https://fmbyteshiftsoftware.com)  
🏢 CNPJ: 62.145.022/0001-05 (Brazil)
