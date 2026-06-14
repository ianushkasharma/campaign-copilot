import json

from sqlalchemy.orm import Session

from crm_service.models import CampaignEvent, Communication
from crm_service.repositories import CampaignRepository, CommunicationRepository, CustomerRepository, SegmentRepository
from crm_service.schemas import ReceiptRequest, SendCampaignRequest


class CampaignNotFoundError(Exception):
    pass


class SegmentNotFoundError(Exception):
    pass


class RecipientNotFoundError(Exception):
    pass


class InvalidSegmentCriteriaError(Exception):
    pass


class CommunicationService:
    def __init__(self, db: Session) -> None:
        self.campaigns = CampaignRepository(db)
        self.customers = CustomerRepository(db)
        self.segments = SegmentRepository(db)
        self.communications = CommunicationRepository(db)

    def send_campaign(self, data: SendCampaignRequest) -> list[Communication]:
        campaign = self.campaigns.get(data.campaign_id)
        if campaign is None:
            raise CampaignNotFoundError("Campaign not found.")

        recipients = []
        if data.customer_ids:
            recipients = self.customers.get_many(data.customer_ids)
        elif data.segment_id is not None:
            segment = self.segments.get(data.segment_id)
            if segment is None:
                raise SegmentNotFoundError("Segment not found.")
            recipients = self.customers.list_for_segment(self._parse_criteria(segment.criteria_json))
        else:
            recipients = self.customers.list_for_segment(criteria=None, limit=1000)

        if not recipients:
            raise RecipientNotFoundError("No matching recipients found.")

        return self.communications.create_campaign_sends(
            campaign_id=campaign.campaign_id,
            channel=campaign.channel,
            customers=recipients,
            subject=data.subject,
            message=data.message,
        )

    def record_receipt(self, data: ReceiptRequest) -> CampaignEvent:
        campaign = self.campaigns.get(data.campaign_id)
        if campaign is None:
            raise CampaignNotFoundError("Campaign not found.")

        if data.customer_id is not None and self.customers.get(data.customer_id) is None:
            raise RecipientNotFoundError("Customer not found.")

        metadata_json = json.dumps(data.metadata) if data.metadata is not None else None
        return self.communications.create_event(
            campaign_id=data.campaign_id,
            customer_id=data.customer_id,
            event_type=data.event_type,
            metadata_json=metadata_json,
        )

    def _parse_criteria(self, criteria_json: str | None) -> dict[str, object] | None:
        if not criteria_json:
            return None
        try:
            parsed = json.loads(criteria_json)
        except json.JSONDecodeError as exc:
            raise InvalidSegmentCriteriaError("Segment criteria_json must be valid JSON.") from exc
        if not isinstance(parsed, dict):
            raise InvalidSegmentCriteriaError("Segment criteria_json must decode to a JSON object.")
        return parsed
