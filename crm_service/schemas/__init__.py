"""CRM service Pydantic schemas."""

from crm_service.schemas.audiences import AudienceQueryRequest, AudienceQueryResponse
from crm_service.schemas.analytics import (
    AudienceLeaderboardItem,
    AudienceLeaderboardResponse,
    CampaignSuccessResponse,
    CustomerScoreItem,
    CustomerScoresResponse,
    RFMScores,
)
from crm_service.schemas.campaign_plans import CampaignPlanRequest, CampaignPlanResponse
from crm_service.schemas.campaigns import CampaignCreate, CampaignListResponse, CampaignResponse, CampaignUpdate
from crm_service.schemas.communications import (
    ReceiptRequest,
    ReceiptResponse,
    SendCampaignRequest,
    SendCampaignResponse,
)
from crm_service.schemas.customers import CustomerCreate, CustomerListResponse, CustomerResponse, CustomerUpdate
from crm_service.schemas.insights import CampaignInsightsRequest, CampaignInsightsResponse, InsightDetail
from crm_service.schemas.monitor import CampaignEventItem, CampaignMonitorResponse, CampaignMonitorSummary
from crm_service.schemas.predictions import (
    AudienceCharacteristics,
    CampaignPredictionRequest,
    CampaignPredictionResponse,
    OfferInput,
)
from crm_service.schemas.segments import SegmentCreate, SegmentListResponse, SegmentResponse, SegmentUpdate

__all__ = [
    "CampaignCreate",
    "AudienceQueryRequest",
    "AudienceQueryResponse",
    "AudienceLeaderboardItem",
    "AudienceLeaderboardResponse",
    "CampaignPlanRequest",
    "CampaignPlanResponse",
    "CampaignListResponse",
    "CampaignEventItem",
    "CampaignMonitorResponse",
    "CampaignMonitorSummary",
    "CampaignResponse",
    "CampaignSuccessResponse",
    "CampaignUpdate",
    "CustomerCreate",
    "CustomerScoreItem",
    "CustomerScoresResponse",
    "AudienceCharacteristics",
    "CampaignPredictionRequest",
    "CampaignPredictionResponse",
    "CampaignInsightsRequest",
    "CampaignInsightsResponse",
    "CustomerListResponse",
    "CustomerResponse",
    "CustomerUpdate",
    "ReceiptRequest",
    "ReceiptResponse",
    "RFMScores",
    "OfferInput",
    "InsightDetail",
    "SegmentCreate",
    "SegmentListResponse",
    "SegmentResponse",
    "SegmentUpdate",
    "SendCampaignRequest",
    "SendCampaignResponse",
]
