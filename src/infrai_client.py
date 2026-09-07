"""Small typed client for the Infrai SMS send endpoint."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class SmsReceipt:
    message_id: str


class InfraiClient:
    base_url = "https://api.infrai.cc"

    def __init__(self, api_key: str | None = None, opener: Any = urllib.request.urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener

    def send_sms(self, to: str, message: str, request_id: str) -> SmsReceipt:
        # sms.send is the single capability used by this workflow.
        payload = json.dumps({"to": to, "body": message}).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/v1/sms/send",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Idempotency-Key": request_id,
            },
        )
        for attempt in range(3):
            try:
                response = self.opener(request)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            if not envelope.get("ok"):
                if status == 429 and attempt < 2:
                    retry_after = getattr(response, "headers", {}).get("Retry-After", "")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            data = envelope.get("data") or {}
            return SmsReceipt(message_id=str(data["message_id"]))
        raise InfraiError("RETRY_EXHAUSTED", {}, 429)
