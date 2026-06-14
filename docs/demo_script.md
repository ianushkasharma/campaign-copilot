# 5-Minute Demo Script

## 0:00-0:30 - Product Setup

"Campaign Copilot is an AI-native marketing CRM that helps marketers find audiences, plan campaigns, simulate delivery, monitor results, and generate post-campaign insights."

Show:

- Streamlit dashboard
- CRM API docs
- Seeded customer dataset

## 0:30-1:15 - Audience Explorer

Open Audience Explorer.

Type:

```text
Find inactive customers who spent more than 5000
```

Explain:

- AudienceAgent converts natural language to filters.
- SQLAlchemy queries the customer database.
- The UI returns audience size, reasoning, and preview.

## 1:15-2:00 - Campaign Copilot

Open Campaign Copilot.

Type:

```text
Bring back inactive customers.
```

Explain:

- CampaignPlannerAgent understands the goal.
- It recommends audience, channel, offer, message, and expected performance.
- The prediction engine estimates open, click, conversion, and revenue.

## 2:00-2:45 - Customer Intelligence

Open Dashboard.

Show:

- RFM score
- Customer health score
- Engagement score
- Loyalty and channel charts

Explain:

- RFM uses recency, frequency, and monetary value.
- Health combines RFM and engagement.
- Engagement comes from campaign event history.

## 2:45-3:30 - Campaign Monitor

Open Campaign Monitor.

Show:

- Messages Sent
- Delivered
- Opened
- Clicked
- Purchased
- Failed
- Progress bars
- Event timeline

Explain:

- The monitor reads from `campaign_events`.
- Channel Simulator sends callbacks into CRM through `/receipt`.

## 3:30-4:20 - AI Insights

Open AI Insights.

Show:

- Post-campaign analysis
- Best segment
- Worst segment
- Best channel
- Revenue generated
- Recommended next action
- Audience leaderboard with AI-generated segment names

Explain:

- InsightsAgent uses campaign data and Gemini.
- Local fallbacks keep demos reliable without an API key.

## 4:20-5:00 - Architecture Close

Open `docs/architecture_diagram.md`.

Explain:

- Clean architecture: routers, schemas, services, repositories, models.
- Separate Channel Simulator service.
- SQLite and SQLAlchemy for fast local evaluation.
- Gemini isolated behind agents.
- Ready migration path to Postgres, auth, and cloud deployment.
