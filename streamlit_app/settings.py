import os


APP_NAME = os.getenv("APP_NAME", "Campaign Copilot")
CRM_SERVICE_HOST = os.getenv("CRM_SERVICE_HOST", "127.0.0.1")
CRM_SERVICE_PORT = int(os.getenv("CRM_SERVICE_PORT", "8001"))


def default_crm_base_url() -> str:
    return f"http://{CRM_SERVICE_HOST}:{CRM_SERVICE_PORT}"
