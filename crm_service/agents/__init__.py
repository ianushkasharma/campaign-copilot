"""AI agents for CRM workflows."""

from crm_service.agents.audience_agent import AudienceAgent
from crm_service.agents.campaign_planner_agent import CampaignPlannerAgent
from crm_service.agents.insights_agent import InsightsAgent
from crm_service.agents.segment_naming_agent import SegmentNamingAgent

__all__ = ["AudienceAgent", "CampaignPlannerAgent", "InsightsAgent", "SegmentNamingAgent"]
