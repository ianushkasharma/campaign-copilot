from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crm_service.schemas import (
    ReceiptRequest,
    ReceiptResponse,
    SendCampaignRequest,
    SendCampaignResponse,
)
from crm_service.services import (
    CampaignNotFoundError,
    CommunicationService,
    InvalidSegmentCriteriaError,
    RecipientNotFoundError,
    SegmentNotFoundError,
)
from shared.database import get_db

router = APIRouter(tags=["communications"])


@router.post(
    "/send-campaign",
    response_model=SendCampaignResponse,
    summary="Send a campaign to a segment or explicit customer list",
)
def send_campaign(payload: SendCampaignRequest, db: Session = Depends(get_db)) -> SendCampaignResponse:
    service = CommunicationService(db)
    try:
        communications = service.send_campaign(payload)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SegmentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecipientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidSegmentCriteriaError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    first = communications[0]
    return SendCampaignResponse(
        campaign_id=first.campaign_id or payload.campaign_id,
        channel=first.channel,
        status="sent",
        recipients=len(communications),
        communication_ids=[communication.communication_id for communication in communications],
    )


@router.post(
    "/receipt",
    response_model=ReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a campaign event receipt",
)
def record_receipt(payload: ReceiptRequest, db: Session = Depends(get_db)) -> ReceiptResponse:
    service = CommunicationService(db)
    try:
        return service.record_receipt(payload)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecipientNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
