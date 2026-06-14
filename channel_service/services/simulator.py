import asyncio
import random

import httpx
from sqlalchemy import select

from channel_service.models import ChannelCommunicationEvent
from channel_service.repositories import ChannelEventRepository
from channel_service.schemas import SendRequest
from shared.config import settings
from shared.database import SessionLocal


DELIVERED = "DELIVERED"
FAILED = "FAILED"
OPENED = "OPENED"
CLICKED = "CLICKED"
PURCHASED = "PURCHASED"

OPEN_PROBABILITIES = {
    "whatsapp": 0.70,
    "email": 0.35,
    "sms": 0.50,
    "push": 0.45,
    "phone": 0.30,
}

DELIVERY_PROBABILITIES = {
    "whatsapp": 0.94,
    "email": 0.90,
    "sms": 0.92,
    "push": 0.88,
    "phone": 0.82,
}

CLICK_AFTER_OPEN_PROBABILITY = 0.28
PURCHASE_AFTER_CLICK_PROBABILITY = 0.12
MAX_DELIVERY_ATTEMPTS = 3


class ChannelSimulatorService:
    def __init__(self) -> None:
        self.min_delay = settings.channel_min_delay_seconds
        self.max_delay = settings.channel_max_delay_seconds
        if self.max_delay < self.min_delay:
            self.max_delay = self.min_delay

    def create_send_event(self, data: SendRequest):
        with SessionLocal() as db:
            repository = ChannelEventRepository(db)
            return repository.create_pending(data)

    async def process_send(self, event_id: int) -> None:
        with SessionLocal() as db:
            repository = ChannelEventRepository(db)
            event = repository.get(event_id)
            if event is None:
                return

            delivered = False
            attempts = 0

            for attempt in range(1, MAX_DELIVERY_ATTEMPTS + 1):
                attempts = attempt
                await self._delay()
                if self._happens(self._delivery_probability(event.channel)):
                    delivered = True
                    break

            if not delivered:
                repository.update_status(event, FAILED, attempts=attempts)
                await self._send_receipt(event.campaign_id, event.recipient, event.channel, FAILED)
                return

            repository.update_status(event, DELIVERED, attempts=attempts)
            await self._send_receipt(event.campaign_id, event.recipient, event.channel, DELIVERED)

            if not self._happens(self._open_probability(event.channel)):
                return

            await self._delay()
            repository.update_status(event, OPENED)
            await self._send_receipt(event.campaign_id, event.recipient, event.channel, OPENED)

            if not self._happens(CLICK_AFTER_OPEN_PROBABILITY):
                return

            await self._delay()
            repository.update_status(event, CLICKED)
            await self._send_receipt(event.campaign_id, event.recipient, event.channel, CLICKED)

            if not self._happens(PURCHASE_AFTER_CLICK_PROBABILITY):
                return

            await self._delay()
            repository.update_status(event, PURCHASED)
            await self._send_receipt(event.campaign_id, event.recipient, event.channel, PURCHASED)

    async def _send_receipt(
        self,
        campaign_id: int,
        recipient: str,
        channel: str,
        event_type: str,
    ) -> None:
        payload = {
            "campaign_id": campaign_id,
            "event_type": event_type,
            "metadata": {
                "recipient": recipient,
                "channel": channel,
                "source": "channel_simulator",
            },
        }

        retries = max(settings.channel_callback_retries, 1)
        last_error = None

        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.post(settings.crm_receipt_url, json=payload)
                    response.raise_for_status()
                return
            except httpx.HTTPError as exc:
                last_error = str(exc)
                if attempt < retries:
                    await asyncio.sleep(min(2**attempt, 10))

        with SessionLocal() as db:
            repository = ChannelEventRepository(db)
            event = self._find_latest_event(db, campaign_id, recipient, channel)
            if event is not None:
                repository.update_status(event, event.status, last_error=last_error)

    def _find_latest_event(self, db, campaign_id: int, recipient: str, channel: str):
        return db.scalars(
            select(ChannelCommunicationEvent)
            .where(ChannelCommunicationEvent.campaign_id == campaign_id)
            .where(ChannelCommunicationEvent.recipient == recipient)
            .where(ChannelCommunicationEvent.channel == channel)
            .order_by(ChannelCommunicationEvent.event_id.desc())
            .limit(1)
        ).first()

    async def _delay(self) -> None:
        await asyncio.sleep(random.uniform(self.min_delay, self.max_delay))

    def _delivery_probability(self, channel: str) -> float:
        return DELIVERY_PROBABILITIES.get(channel.lower(), 0.85)

    def _open_probability(self, channel: str) -> float:
        return OPEN_PROBABILITIES.get(channel.lower(), 0.40)

    def _happens(self, probability: float) -> bool:
        return random.random() <= probability
