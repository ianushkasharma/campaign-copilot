from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import httpx
except ImportError:
    httpx = None

try:
    import requests
except ImportError:
    requests = None

from streamlit_app.settings import default_crm_base_url


class CRMClient:
    DEFAULT_TIMEOUT_SECONDS = 5

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or default_crm_base_url()

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def list_customers(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self._request("GET", "/customers", params={"limit": limit, "offset": offset})

    def list_campaigns(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self._request("GET", "/campaigns", params={"limit": limit, "offset": offset})

    def list_segments(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self._request("GET", "/segments", params={"limit": limit, "offset": offset})

    def create_campaign(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/campaigns", json=payload)

    def create_segment(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/segments", json=payload)

    def query_audience(self, query: str, preview_limit: int = 10) -> dict[str, Any]:
        return self._request(
            "POST",
            "/audiences/query",
            json={"query": query, "preview_limit": preview_limit},
        )

    def plan_campaign(self, goal: str, preview_limit: int = 5) -> dict[str, Any]:
        return self._request(
            "POST",
            "/campaign-copilot/plan",
            json={"goal": goal, "preview_limit": preview_limit},
        )

    def predict_campaign(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/predictions/campaign", json=payload)

    def send_campaign(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/send-campaign", json=payload)

    def campaign_monitor(self, campaign_id: int | None = None, limit: int = 100) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if campaign_id is not None:
            params["campaign_id"] = campaign_id
        return self._request("GET", "/campaign-monitor", params=params)

    def analyze_campaign(self, campaign_id: int) -> dict[str, Any]:
        return self._request("POST", "/ai-insights/analyze", json={"campaign_id": campaign_id})

    def customer_scores(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return self._request("GET", "/analytics/customer-scores", params={"limit": limit, "offset": offset})

    def campaign_success(self, campaign_id: int | None = None) -> dict[str, Any]:
        params = {}
        if campaign_id is not None:
            params["campaign_id"] = campaign_id
        return self._request("GET", "/analytics/campaign-success", params=params)

    def audience_leaderboard(self, campaign_id: int | None = None) -> dict[str, Any]:
        params = {}
        if campaign_id is not None:
            params["campaign_id"] = campaign_id
        return self._request("GET", "/analytics/audience-leaderboard", params=params)

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if httpx is not None:
            try:
                with httpx.Client(timeout=self.DEFAULT_TIMEOUT_SECONDS) as client:
                    response = client.request(method, url, **kwargs)
                    response.raise_for_status()
                    if response.content:
                        return response.json()
                    return {}
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(
                    f"Campaign Copilot request failed with status {exc.response.status_code}. Please try again."
                ) from exc
            except httpx.HTTPError as exc:
                raise RuntimeError("Could not connect to Campaign Copilot services.") from exc

        if requests is None:
            raise RuntimeError("Install httpx or requests to connect the Streamlit app to Campaign Copilot services.")

        try:
            request_kwargs = dict(kwargs)
            request_kwargs.setdefault("timeout", self.DEFAULT_TIMEOUT_SECONDS)
            response = requests.request(method, url, **request_kwargs)
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except requests.HTTPError as exc:
            status_code = exc.response.status_code if exc.response is not None else "unknown"
            raise RuntimeError(f"Campaign Copilot request failed with status {status_code}. Please try again.") from exc
        except requests.RequestException as exc:
            raise RuntimeError("Could not connect to Campaign Copilot services.") from exc
