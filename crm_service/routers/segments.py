from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from crm_service.schemas import SegmentCreate, SegmentListResponse, SegmentResponse, SegmentUpdate
from crm_service.services import DuplicateSegmentError, SegmentService
from shared.database import get_db

router = APIRouter(prefix="/segments", tags=["segments"])


@router.post(
    "",
    response_model=SegmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a segment",
)
def create_segment(payload: SegmentCreate, db: Session = Depends(get_db)) -> SegmentResponse:
    service = SegmentService(db)
    try:
        return service.create_segment(payload)
    except DuplicateSegmentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "",
    response_model=SegmentListResponse,
    summary="List segments",
)
def list_segments(
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    db: Session = Depends(get_db),
) -> SegmentListResponse:
    service = SegmentService(db)
    segments, total = service.list_segments(limit=limit, offset=offset)
    return SegmentListResponse(items=segments, total=total, limit=limit, offset=offset)


@router.get(
    "/{segment_id}",
    response_model=SegmentResponse,
    summary="Get a segment by ID",
)
def get_segment(segment_id: int, db: Session = Depends(get_db)) -> SegmentResponse:
    service = SegmentService(db)
    segment = service.get_segment(segment_id)
    if segment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found.")
    return segment


@router.patch(
    "/{segment_id}",
    response_model=SegmentResponse,
    summary="Update a segment",
)
def update_segment(
    segment_id: int,
    payload: SegmentUpdate,
    db: Session = Depends(get_db),
) -> SegmentResponse:
    service = SegmentService(db)
    segment = service.get_segment(segment_id)
    if segment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found.")
    try:
        return service.update_segment(segment, payload)
    except DuplicateSegmentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete(
    "/{segment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a segment",
)
def delete_segment(segment_id: int, db: Session = Depends(get_db)) -> None:
    service = SegmentService(db)
    segment = service.get_segment(segment_id)
    if segment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found.")
    service.delete_segment(segment)
