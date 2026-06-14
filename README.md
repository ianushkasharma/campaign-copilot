# Campaign Copilot

Campaign Copilot is a full-stack marketing CRM and campaign management platform that combines customer analytics, audience segmentation, campaign planning, monitoring, and AI-assisted decision support.

The project demonstrates backend architecture, data modeling, analytics engineering, AI integration, and dashboard development using FastAPI, Streamlit, SQLite, and Gemini.

---

## Features

### Customer Analytics Dashboard

* Customer overview and business KPIs
* Revenue and order analytics
* Loyalty tier distribution
* Preferred communication channel analysis
* Customer engagement metrics
* Customer health scoring

### Audience Explorer

Convert natural language audience requests into structured customer filters.

Example:

```text
Find inactive customers who spent more than 5000
```

The system:

* Interprets the request
* Generates customer filters
* Queries the CRM database
* Returns audience size and customer preview

### Campaign Planning

Generate campaign recommendations based on customer audiences.

Outputs include:

* Campaign objective
* Target audience
* Recommended communication channel
* Suggested offer
* Marketing message
* Expected campaign performance

### Campaign Monitoring

Track campaign performance through:

* Messages sent
* Delivered
* Opened
* Clicked
* Purchased
* Failed

Includes:

* Live campaign metrics
* Event tracking
* Progress indicators
* Campaign timeline

### AI Insights

Analyze completed campaigns and generate actionable recommendations.

Insights include:

* Performance summary
* Best-performing audience
* Best-performing channel
* Revenue contribution
* Recommended next actions

### Customer Scoring & Analytics

The platform includes:

* RFM Analysis
* Customer Health Score
* Engagement Score
* Campaign Success Score
* Audience Performance Leaderboard

---

## Technology Stack

### Frontend

* Streamlit
* Plotly
* Pandas

### Backend

* FastAPI
* SQLAlchemy
* Pydantic

### Database

* SQLite

### AI

* Google Gemini

### Architecture

* CRM Service
* Channel Simulator Service
* Shared Analytics Layer

---

## Project Structure

```text
campaign-copilot/
│
├── crm_service/
│   ├── agents/
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   └── utils/
│
├── channel_service/
├── streamlit_app/
├── shared/
├── data/
├── docs/
├── tests/
│
├── seed.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Dataset

The project uses a seeded CRM dataset containing:

* 5,000 customers
* 20,000 orders

The synthetic dataset enables realistic testing of:

* Customer segmentation
* Campaign planning
* Analytics workflows
* Marketing performance simulations

---

## Installation

### Clone Repository

```bash
git clone https://github.com/ianushkasharma/campaign-copilot.git
cd campaign-copilot
```

### Create Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

```bash
copy .env.example .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### Seed Database

```bash
python seed.py
```

---

## Running the Application

### CRM Service

```bash
uvicorn crm_service.main:app --host 127.0.0.1 --port 8001 --reload
```

### Channel Simulator

```bash
uvicorn channel_service.main:app --host 127.0.0.1 --port 8002 --reload
```

### Streamlit Dashboard

```bash
streamlit run streamlit_app/app.py
```

---

## Application URLs

| Service              | URL                        |
| -------------------- | -------------------------- |
| Streamlit Dashboard  | http://127.0.0.1:8501      |
| CRM API Docs         | http://127.0.0.1:8001/docs |
| Channel Service Docs | http://127.0.0.1:8002/docs |

---

## API Endpoints

### Audience Management

```http
POST /audiences/query
```

### Campaign Planning

```http
POST /campaign-copilot/plan
```

### Campaign Prediction

```http
POST /predictions/campaign
```

### Campaign Monitoring

```http
GET /campaign-monitor
```

### AI Insights

```http
POST /ai-insights/analyze
```

### Analytics

```http
GET /analytics/customer-scores
GET /analytics/campaign-success
GET /analytics/audience-leaderboard
```

### Campaign Delivery

```http
POST /send-campaign
POST /receipt
POST /send
```

---

## Key Learnings

* Designed a modular FastAPI backend using routers, services, repositories, and SQLAlchemy models.
* Built customer segmentation workflows combining natural language requests with structured database filtering.
* Implemented interactive dashboards using Streamlit and Plotly.
* Developed customer analytics using RFM scoring, engagement metrics, and campaign performance indicators.
* Built asynchronous campaign event tracking and monitoring workflows.
* Integrated Gemini to support audience exploration and campaign planning tasks.

---

## Future Improvements

* Multi-channel campaign orchestration
* A/B testing framework
* Advanced predictive analytics
* Customer lifetime value prediction
* Automated campaign optimization
* Cloud deployment with PostgreSQL and Docker

---

## Author

Anushka Sharma

B.Tech Computer Science Engineering
SRM Institute of Science and Technology
