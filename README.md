# Campaign Copilot

Campaign Copilot is an AI-native marketing CRM built for internship evaluation. It demonstrates full-stack product thinking across data modeling, campaign planning, AI agents, analytics, monitoring, and recruiter-friendly documentation.

## What It Does

Campaign Copilot helps a marketer:

- Explore customers and audience segments.
- Ask for audiences in natural language.
- Generate campaign plans with Gemini-powered agents.
- Predict campaign performance before launch.
- Simulate channel delivery and callbacks.
- Monitor campaign events live.
- Analyze completed campaigns with AI insights.
- Score customers using RFM, health, and engagement metrics.

## Evaluation Highlights

- 5,000 seeded customers and 20,000 seeded orders.
- Clean FastAPI backend with routers, schemas, services, repositories, and SQLAlchemy models.
- Streamlit frontend with dashboard, audience explorer, campaign planner, monitor, and AI insights pages.
- Gemini-backed agents with deterministic fallbacks for reliable demos.
- Separate Channel Simulator service using async background tasks and CRM callbacks.
- Analytics layer with RFM Analysis, Customer Health Score, Engagement Score, Campaign Success Score, and best performing audience leaderboard.
- AI-generated segment names for leaderboard audiences.
- Recruiter-ready docs, deployment guide, architecture diagram, and 5-minute demo script.

## Tech Stack

- Frontend: Streamlit, Plotly, pandas
- Backend: FastAPI
- Database: SQLite + SQLAlchemy
- AI: Gemini
- Services:
  - CRM Service
  - Channel Simulator Service

## Project Structure

```text
campaign-copilot/
|-- crm_service/
|   |-- agents/
|   |-- routers/
|   |-- models/
|   |-- schemas/
|   |-- services/
|   |-- repositories/
|   `-- utils/
|-- channel_service/
|-- streamlit_app/
|-- shared/
|-- data/
|-- docs/
|-- tests/
|-- seed.py
|-- requirements.txt
|-- .env.example
`-- README.md
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py
```

Run CRM:

```bash
uvicorn crm_service.main:app --host 127.0.0.1 --port 8001 --reload
```

Run Channel Simulator:

```bash
uvicorn channel_service.main:app --host 127.0.0.1 --port 8002 --reload
```

Run Streamlit:

```bash
streamlit run streamlit_app/app.py
```

## App URLs

- Streamlit app: `http://127.0.0.1:8501`
- CRM OpenAPI docs: `http://127.0.0.1:8001/docs`
- Channel Simulator OpenAPI docs: `http://127.0.0.1:8002/docs`

## Main Features

### Dashboard

- Customer metrics
- Loyalty and channel charts
- RFM score table
- Customer Health Score
- Engagement Score

### Audience Explorer

Example:

```text
Find inactive customers who spent more than 5000
```

AudienceAgent converts the request into filters, queries SQLite, and returns audience size, reasoning, and customer preview.

### Campaign Copilot

Example:

```text
Bring back inactive customers.
```

CampaignPlannerAgent returns:

- Goal understanding
- Recommended audience
- Audience reasoning
- Recommended channel
- Recommended offer
- Personalized message
- Expected performance

### Campaign Prediction Engine

Inputs:

- Audience characteristics
- Channel
- Offer

Outputs:

- Predicted open rate
- Predicted click rate
- Predicted conversion rate
- Predicted revenue

### Campaign Monitor

Reads from `campaign_events` and shows:

- Messages Sent
- Delivered
- Opened
- Clicked
- Purchased
- Failed
- Progress bars
- Live refresh
- Event timeline

### AI Insights Engine

After campaign completion, InsightsAgent generates:

- What happened
- Why it happened
- Best segment
- Worst segment
- Best channel
- Revenue generated
- Recommended next action

### Analytics for Evaluation

- RFM Analysis
- Customer Health Score
- Engagement Score
- Campaign Success Score
- AI-generated segment names
- Best performing audience leaderboard

## Important Endpoints

- `POST /audiences/query`
- `POST /campaign-copilot/plan`
- `POST /predictions/campaign`
- `GET /campaign-monitor`
- `POST /ai-insights/analyze`
- `GET /analytics/customer-scores`
- `GET /analytics/campaign-success`
- `GET /analytics/audience-leaderboard`
- `POST /send-campaign`
- `POST /receipt`
- Channel Simulator: `POST /send`

## Documentation

- [Architecture Diagram](docs/architecture_diagram.md)
- [Architecture Notes](docs/architecture.md)
- [Deployment Guide](docs/deployment_guide.md)
- [5-Minute Demo Script](docs/demo_script.md)

## Why This Is Internship-Ready

This project shows more than CRUD. It demonstrates product reasoning, backend architecture, AI integration, analytics modeling, frontend UX, and demo readiness. The code is intentionally modular so each feature can be explained in an interview: agents handle AI, services handle use cases, repositories handle persistence, and Streamlit turns the backend into a usable product.
