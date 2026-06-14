from sqlalchemy import func, select
from sqlalchemy.orm import Session

from crm_service.models import CampaignEvent


class CampaignMonitorRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def event_counts(self, campaign_id: int | None = None) -> dict[str, int]:
        statement = select(CampaignEvent.event_type, func.count()).group_by(CampaignEvent.event_type)
        if campaign_id is not None:
            statement = statement.where(CampaignEvent.campaign_id == campaign_id)

        rows = self.db.execute(statement).all()
        return {str(event_type).upper(): int(count) for event_type, count in rows}

    def timeline(self, campaign_id: int | None = None, limit: int = 100) -> list[CampaignEvent]:
        statement = select(CampaignEvent).order_by(CampaignEvent.event_time.desc(), CampaignEvent.event_id.desc())
        if campaign_id is not None:
            statement = statement.where(CampaignEvent.campaign_id == campaign_id)
        return list(self.db.scalars(statement.limit(limit)).all())
