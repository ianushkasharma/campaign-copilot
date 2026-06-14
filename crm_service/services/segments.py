from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crm_service.models import Segment
from crm_service.repositories import SegmentRepository
from crm_service.schemas import SegmentCreate, SegmentUpdate


class DuplicateSegmentError(Exception):
    pass


class SegmentService:
    def __init__(self, db: Session) -> None:
        self.repository = SegmentRepository(db)

    def create_segment(self, data: SegmentCreate) -> Segment:
        try:
            return self.repository.create(data)
        except IntegrityError as exc:
            raise DuplicateSegmentError("A segment with this name already exists.") from exc

    def list_segments(self, limit: int, offset: int) -> tuple[list[Segment], int]:
        return self.repository.list(limit=limit, offset=offset)

    def get_segment(self, segment_id: int) -> Segment | None:
        return self.repository.get(segment_id)

    def update_segment(self, segment: Segment, data: SegmentUpdate) -> Segment:
        try:
            return self.repository.update(segment, data)
        except IntegrityError as exc:
            raise DuplicateSegmentError("A segment with this name already exists.") from exc

    def delete_segment(self, segment: Segment) -> None:
        self.repository.delete(segment)
