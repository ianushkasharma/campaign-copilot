from sqlalchemy.orm import Session

from crm_service.models import Campaign
from crm_service.repositories import CampaignRepository
from crm_service.schemas import CampaignCreate, CampaignUpdate


class CampaignService:
    def __init__(self, db: Session) -> None:
        self.repository = CampaignRepository(db)

    def create_campaign(self, data: CampaignCreate) -> Campaign:
        return self.repository.create(data)

    def list_campaigns(self, limit: int, offset: int) -> tuple[list[Campaign], int]:
        return self.repository.list(limit=limit, offset=offset)

    def get_campaign(self, campaign_id: int) -> Campaign | None:
        return self.repository.get(campaign_id)

    def update_campaign(self, campaign: Campaign, data: CampaignUpdate) -> Campaign:
        return self.repository.update(campaign, data)

    def delete_campaign(self, campaign: Campaign) -> None:
        self.repository.delete(campaign)
