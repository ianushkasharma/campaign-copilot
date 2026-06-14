from datetime import datetime, timezone

from sqlalchemy.orm import Session

from crm_service.models import CampaignEvent, Communication, Customer


class CommunicationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_campaign_sends(
        self,
        campaign_id: int,
        channel: str,
        customers: list[Customer],
        subject: str | None,
        message: str | None,
    ) -> list[Communication]:
        communications = [
            Communication(
                customer_id=customer.customer_id,
                campaign_id=campaign_id,
                channel=channel,
                subject=subject,
                message=message,
                sent_at=datetime.now(timezone.utc),
                status="sent",
            )
            for customer in customers
        ]
        self.db.add_all(communications)
        self.db.flush()
        events = [
            CampaignEvent(
                campaign_id=campaign_id,
                customer_id=customer.customer_id,
                event_type="SENT",
                event_time=datetime.now(timezone.utc),
                metadata_json=f'{{"channel": "{channel}", "source": "crm_service"}}',
            )
            for customer in customers
        ]
        self.db.add_all(events)
        self.db.commit()
        for communication in communications:
            self.db.refresh(communication)
        return communications

    def create_event(
        self,
        campaign_id: int,
        customer_id: int | None,
        event_type: str,
        metadata_json: str | None,
    ) -> CampaignEvent:
        event = CampaignEvent(
            campaign_id=campaign_id,
            customer_id=customer_id,
            event_type=event_type,
            event_time=datetime.now(timezone.utc),
            metadata_json=metadata_json,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
