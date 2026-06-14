# Campaign Copilot Architecture Diagram

```mermaid
flowchart LR
    User["Marketing User"] --> UI["Streamlit Frontend"]

    UI --> CRM["CRM FastAPI Service"]
    UI --> Analytics["Analytics APIs"]
    UI --> Planner["Campaign Copilot APIs"]

    CRM --> DB[("SQLite Database")]
    Analytics --> DB
    Planner --> DB

    Planner --> Gemini["Gemini API"]
    CRM --> Gemini

    CRM --> Channel["Channel Simulator FastAPI Service"]
    Channel --> CRMReceipt["CRM /receipt Callback"]
    CRMReceipt --> DB

    subgraph CRM_Service["CRM Service Clean Architecture"]
        Routers["Routers"]
        Schemas["Schemas"]
        Services["Services"]
        Repositories["Repositories"]
        Models["SQLAlchemy Models"]
        Routers --> Services --> Repositories --> Models
    end

    CRM --> CRM_Service
```

## Key Design Points

- Streamlit is the operator UI.
- FastAPI exposes CRM, AI planning, analytics, monitoring, and insights endpoints.
- SQLAlchemy models own the persistence layer.
- Gemini is isolated behind agents so the app still works with deterministic fallbacks.
- Channel Simulator runs as a separate FastAPI service and sends event callbacks to CRM.
- Analytics endpoints compute RFM, customer health, engagement, campaign success, and audience leaderboards.
