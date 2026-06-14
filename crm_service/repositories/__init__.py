"""CRM service repositories."""

from crm_service.repositories.audiences import AudienceRepository
from crm_service.repositories.analytics import AnalyticsRepository
from crm_service.repositories.campaigns import CampaignRepository
from crm_service.repositories.communications import CommunicationRepository
from crm_service.repositories.customers import CustomerRepository
from crm_service.repositories.insights import CampaignInsightsRepository
from crm_service.repositories.monitor import CampaignMonitorRepository
from crm_service.repositories.segments import SegmentRepository

__all__ = [
    "CampaignRepository",
    "AudienceRepository",
    "AnalyticsRepository",
    "CommunicationRepository",
    "CustomerRepository",
    "CampaignInsightsRepository",
    "CampaignMonitorRepository",
    "SegmentRepository",
]
