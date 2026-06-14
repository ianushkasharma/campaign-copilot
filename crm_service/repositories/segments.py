from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crm_service.models import Segment
from crm_service.schemas import SegmentCreate, SegmentUpdate


class SegmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: SegmentCreate) -> Segment:
        segment = Segment(**data.model_dump())
        self.db.add(segment)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(segment)
        return segment

    def list(self, limit: int, offset: int) -> tuple[list[Segment], int]:
        total = self.db.scalar(select(func.count()).select_from(Segment)) or 0
        segments = self.db.scalars(
            select(Segment)
            .order_by(Segment.segment_id)
            .limit(limit)
            .offset(offset)
        ).all()
        return list(segments), total

    def get(self, segment_id: int) -> Segment | None:
        return self.db.get(Segment, segment_id)

    def update(self, segment: Segment, data: SegmentUpdate) -> Segment:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(segment, field, value)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(segment)
        return segment

    def delete(self, segment: Segment) -> None:
        self.db.delete(segment)
        self.db.commit()
