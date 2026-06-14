from sqlalchemy.orm import Session

from crm_service.repositories import CampaignMonitorRepository
from crm_service.schemas import CampaignMonitorResponse, CampaignMonitorSummary


class CampaignMonitorService:
    def __init__(self, db: Session) -> None:
        self.repository = CampaignMonitorRepository(db)

    def get_monitor(self, campaign_id: int | None, limit: int) -> CampaignMonitorResponse:
        counts = self.repository.event_counts(campaign_id=campaign_id)
        timeline = self.repository.timeline(campaign_id=campaign_id, limit=limit)
        summary = CampaignMonitorSummary(
            messages_sent=counts.get("SENT", 0),
            delivered=counts.get("DELIVERED", 0),
            opened=counts.get("OPENED", 0),
            clicked=counts.get("CLICKED", 0),
            purchased=counts.get("PURCHASED", 0),
            failed=counts.get("FAILED", 0),
        )
        return CampaignMonitorResponse(
            campaign_id=campaign_id,
            summary=summary,
            timeline=timeline,
        )
