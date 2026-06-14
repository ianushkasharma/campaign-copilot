from sqlalchemy.orm import Session

from crm_service.agents import InsightsAgent
from crm_service.repositories import CampaignInsightsRepository, CampaignRepository
from crm_service.schemas import CampaignInsightsResponse


class CampaignInsightsNotFoundError(Exception):
    pass


class CampaignInsightsService:
    def __init__(self, db: Session) -> None:
        self.campaigns = CampaignRepository(db)
        self.repository = CampaignInsightsRepository(db)
        self.agent = InsightsAgent()

    def analyze(self, campaign_id: int) -> CampaignInsightsResponse:
        if self.campaigns.get(campaign_id) is None:
            raise CampaignInsightsNotFoundError("Campaign not found.")

        dataset = self.repository.campaign_dataset(campaign_id)
        insights = self.agent.analyze(dataset)
        summary = dataset.get("summary", {})
        if not isinstance(summary, dict):
            summary = {}

        return CampaignInsightsResponse(
            campaign_id=campaign_id,
            what_happened=str(insights["what_happened"]),
            why_it_happened=str(insights["why_it_happened"]),
            best_segment=insights["best_segment"],
            worst_segment=insights["worst_segment"],
            best_channel=insights["best_channel"],
            revenue_generated=float(insights["revenue_generated"]),
            recommended_next_action=str(insights["recommended_next_action"]),
            metrics={key: int(value) for key, value in summary.items()},
        )
