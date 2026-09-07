from src.alerts import ReleaseEvent, notify_release_failure


class RecordingClient:
    def __init__(self):
        self.calls = []

    def send_sms(self, to, message, request_id):
        self.calls.append((to, message, request_id))
        return "receipt"


def test_failed_release_sends_diagnostic_once():
    client = RecordingClient()
    event = ReleaseEvent("r-17", "payments", "failed", "+15550001", "migration check failed")
    assert notify_release_failure(event, client) == "receipt"
    assert client.calls == [("+15550001", "payments release r-17 failed: migration check failed", "release:r-17")]


def test_successful_release_is_quiet():
    client = RecordingClient()
    event = ReleaseEvent("r-18", "payments", "succeeded", "+15550001", "all checks green")
    assert notify_release_failure(event, client) is None
    assert client.calls == []
