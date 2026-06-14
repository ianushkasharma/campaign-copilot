from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from crm_service.schemas import CampaignCreate, CampaignListResponse, CampaignResponse, CampaignUpdate
from crm_service.services import CampaignService
from shared.database import get_db

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post(
    "",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a campaign",
)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)) -> CampaignResponse:
    service = CampaignService(db)
    return service.create_campaign(payload)


@router.get(
    "",
    response_model=CampaignListResponse,
    summary="List campaigns",
)
def list_campaigns(
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> CampaignListResponse:
    service = CampaignService(db)
    campaigns, total = service.list_campaigns(limit=limit, offset=offset)
    return CampaignListResponse(items=campaigns, total=total, limit=limit, offset=offset)


@router.get(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Get a campaign by ID",
)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)) -> CampaignResponse:
    service = CampaignService(db)
    campaign = service.get_campaign(campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    return campaign


@router.patch(
    "/{campaign_id}",
    response_model=CampaignResponse,
    summary="Update a campaign",
)
def update_campaign(
    campaign_id: int,
    payload: CampaignUpdate,
    db: Session = Depends(get_db),
) -> CampaignResponse:
    service = CampaignService(db)
    campaign = service.get_campaign(campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    return service.update_campaign(campaign, payload)


@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a campaign",
)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)) -> None:
    service = CampaignService(db)
    campaign = service.get_campaign(campaign_id)
    if campaign is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found.")
    service.delete_campaign(campaign)
