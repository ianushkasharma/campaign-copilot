# Deployment Guide

## Local Demo Deployment

1. Create and activate a virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Configure environment.

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

4. Seed demo data.

```bash
python seed.py
```

5. Start CRM API.

```bash
uvicorn crm_service.main:app --host 127.0.0.1 --port 8001 --reload
```

6. Start Channel Simulator.

```bash
uvicorn channel_service.main:app --host 127.0.0.1 --port 8002 --reload
```

7. Start Streamlit.

```bash
streamlit run streamlit_app/app.py
```

## URLs

- Streamlit: `http://127.0.0.1:8501`
- CRM API docs: `http://127.0.0.1:8001/docs`
- Channel Simulator docs: `http://127.0.0.1:8002/docs`

## Environment Variables

- `DATABASE_URL`: SQLite database path.
- `GEMINI_API_KEY`: Optional Gemini key for AI generation.
- `GEMINI_MODEL`: Gemini model name.
- `CRM_RECEIPT_URL`: Channel callback URL.
- `CHANNEL_CALLBACK_RETRIES`: Retry count for callbacks.

## Production Notes

- Replace SQLite with Postgres for concurrent production workloads.
- Add Alembic migrations.
- Add authentication and role-based access control.
- Move secrets to a cloud secret manager.
- Deploy CRM and Channel Simulator as separate services.
- Run Streamlit behind an authenticated reverse proxy.
- Add scheduled jobs for campaign lifecycle automation.
- Add observability with structured logs and metrics.
