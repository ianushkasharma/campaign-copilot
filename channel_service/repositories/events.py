from datetime import datetime, timezone

from sqlalchemy.orm import Session

from channel_service.models import ChannelCommunicationEvent
from channel_service.schemas import SendRequest


class ChannelEventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_pending(self, data: SendRequest) -> ChannelCommunicationEvent:
        event = ChannelCommunicationEvent(
            campaign_id=data.campaign_id,
            recipient=data.recipient,
            channel=data.channel.lower(),
            message=data.message,
            status="QUEUED",
            attempts=0,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get(self, event_id: int) -> ChannelCommunicationEvent | None:
        return self.db.get(ChannelCommunicationEvent, event_id)

    def update_status(
        self,
        event: ChannelCommunicationEvent,
        status: str,
        attempts: int | None = None,
        last_error: str | None = None,
    ) -> ChannelCommunicationEvent:
        event.status = status
        event.last_event_at = datetime.now(timezone.utc)
        if attempts is not None:
            event.attempts = attempts
        event.last_error = last_error
        self.db.commit()
        self.db.refresh(event)
        return event
