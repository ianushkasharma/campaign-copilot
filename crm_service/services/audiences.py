import logging

from sqlalchemy.orm import Session

from crm_service.agents import AudienceAgent
from crm_service.repositories import AudienceRepository
from crm_service.schemas import AudienceQueryRequest, AudienceQueryResponse

logger = logging.getLogger(__name__)


class AudienceService:
    def __init__(self, db: Session) -> None:
        self.agent = AudienceAgent()
        self.repository = AudienceRepository(db)

    def query_audience(self, data: AudienceQueryRequest) -> AudienceQueryResponse:
        try:
            agent_result = self.agent.build_filters(data.query)
        except Exception:
            logger.exception("Audience query failed in AI path. Falling back to local segmentation.")
            agent_result = self.agent.build_fallback_filters(data.query)

        filters = agent_result["filters"]
        reasoning = str(agent_result["reasoning"])

        audience_size, preview = self.repository.query_customers(
            filters=filters,
            preview_limit=data.preview_limit,
        )
        return AudienceQueryResponse(
            audience_size=audience_size,
            reasoning=reasoning,
            filters=filters,
            audience_preview=preview,
        )
