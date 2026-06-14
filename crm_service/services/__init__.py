"""CRM service application services."""

from crm_service.services.audiences import AudienceService
from crm_service.services.analytics import AnalyticsService
from crm_service.services.campaigns import CampaignService
from crm_service.services.campaign_planner import CampaignPlannerService
from crm_service.services.communications import (
    CampaignNotFoundError,
    CommunicationService,
    InvalidSegmentCriteriaError,
    RecipientNotFoundError,
    SegmentNotFoundError,
)
from crm_service.services.customers import CustomerService, DuplicateCustomerError
from crm_service.services.insights import CampaignInsightsNotFoundError, CampaignInsightsService
from crm_service.services.monitor import CampaignMonitorService
from crm_service.services.predictions import CampaignPredictionEngine, CampaignPredictionService
from crm_service.services.segments import DuplicateSegmentError, SegmentService

__all__ = [
    "CampaignNotFoundError",
    "AudienceService",
    "AnalyticsService",
    "CampaignService",
    "CampaignPlannerService",
    "CampaignPredictionEngine",
    "CampaignPredictionService",
    "CampaignMonitorService",
    "CampaignInsightsNotFoundError",
    "CampaignInsightsService",
    "CommunicationService",
    "CustomerService",
    "DuplicateCustomerError",
    "DuplicateSegmentError",
    "InvalidSegmentCriteriaError",
    "RecipientNotFoundError",
    "SegmentNotFoundError",
    "SegmentService",
]
