from __future__ import annotations

from dataclasses import dataclass

from .infrai_client import InfraiClient, SmsReceipt


@dataclass(frozen=True)
class ReleaseEvent:
    release_id: str
    service: str
    status: str
    operator_phone: str
    diagnostics: str
    notified: bool = False


def notify_release_failure(event: ReleaseEvent, client: InfraiClient) -> SmsReceipt | None:
    """Send one concise diagnostic when a release changes to failed."""
    if event.status != "failed" or event.notified:
        return None
    body = f"{event.service} release {event.release_id} failed: {event.diagnostics}"
    return client.send_sms(event.operator_phone, body, request_id=f"release:{event.release_id}")
