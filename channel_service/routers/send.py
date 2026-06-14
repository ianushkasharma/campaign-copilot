from fastapi import APIRouter, BackgroundTasks, status

from channel_service.schemas import SendRequest, SendResponse
from channel_service.services import ChannelSimulatorService

router = APIRouter(tags=["send"])


@router.post(
    "/send",
    response_model=SendResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Send a simulated channel message",
    description=(
        "Creates a local channel communication event, then simulates delivery "
        "and engagement outcomes in the background. Each event update is sent "
        "to the CRM service through POST /receipt."
    ),
)
def send_message(payload: SendRequest, background_tasks: BackgroundTasks) -> SendResponse:
    service = ChannelSimulatorService()
    event = service.create_send_event(payload)
    background_tasks.add_task(service.process_send, event.event_id)
    return SendResponse(
        event_id=event.event_id,
        campaign_id=event.campaign_id,
        recipient=event.recipient,
        channel=event.channel,
        status=event.status,
        message="Message accepted for simulated delivery.",
    )
