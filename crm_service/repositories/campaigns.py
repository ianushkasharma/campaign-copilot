from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from crm_service.models import Campaign
from crm_service.schemas import CampaignCreate, CampaignUpdate


class CampaignRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: CampaignCreate) -> Campaign:
        campaign = Campaign(**data.model_dump())
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def list(self, limit: int, offset: int) -> tuple[list[Campaign], int]:
        total = self.db.scalar(select(func.count()).select_from(Campaign)) or 0
        campaigns = self.db.scalars(
            select(Campaign)
            .order_by(Campaign.campaign_id)
            .limit(limit)
            .offset(offset)
        ).all()
        return list(campaigns), total

    def get(self, campaign_id: int) -> Campaign | None:
        return self.db.get(Campaign, campaign_id)

    def update(self, campaign: Campaign, data: CampaignUpdate) -> Campaign:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(campaign, field, value)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def delete(self, campaign: Campaign) -> None:
        self.db.delete(campaign)
        self.db.commit()
