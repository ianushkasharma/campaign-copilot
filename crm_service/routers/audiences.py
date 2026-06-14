from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crm_service.schemas import AudienceQueryRequest, AudienceQueryResponse
from crm_service.services import AudienceService
from shared.database import get_db

router = APIRouter(prefix="/audiences", tags=["audiences"])


@router.post(
    "/query",
    response_model=AudienceQueryResponse,
    summary="Create an AI audience from natural language",
    description=(
        "Uses AudienceAgent with Gemini to convert a natural language request "
        "into customer filters, query the database, and return audience size, "
        "reasoning, and a customer preview."
    ),
)
def query_audience(payload: AudienceQueryRequest, db: Session = Depends(get_db)) -> AudienceQueryResponse:
    service = AudienceService(db)
    return service.query_audience(payload)
