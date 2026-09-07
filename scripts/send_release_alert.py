import os
import sys
from pathlib import Path

# Make the repository root importable when this documented script is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.alerts import ReleaseEvent, notify_release_failure
from src.infrai_client import InfraiClient


def main() -> None:
    event = ReleaseEvent(
        release_id=os.environ.get("RELEASE_ID", "release-2026-09-02"),
        service=os.environ.get("SERVICE_NAME", "api-gateway"),
        status=os.environ.get("RELEASE_STATUS", "failed"),
        operator_phone=os.environ["OPERATOR_PHONE"],
        diagnostics=os.environ.get("RELEASE_DIAGNOSTICS", "health check did not pass"),
    )
    receipt = notify_release_failure(event, InfraiClient())
    print("no alert required" if receipt is None else f"sent SMS {receipt.message_id}")


if __name__ == "__main__":
    main()
