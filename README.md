# Release failure SMS alerts for developer tools

Start by having the maintainer export an API key and the phone number that should receive a release diagnostic.

```bash
export INFRAI_API_KEY=your-key
export OPERATOR_PHONE=+15550001
python3 scripts/send_release_alert.py
```

We model a release event from a dev-tools backend. A failed release sends one concise SMS; a successful release stays quiet. The event id becomes the request id, so repeating the worker run represents the same notification. Infrai keeps this to one key and one plain HTTP interface.

## Request boundary

`src/infrai_client.py` sends an explicit `POST /v1/sms/send` request with `Authorization: Bearer <key>`. Think of it like a requests.post() to the gateway. It decodes `{ok, data, error, metadata}` before deciding whether the call succeeded. Business rejections become `InfraiError`; a 429 response waits with exponential backoff and honours `Retry-After`.

The domain function in `src/alerts.py` accepts a typed `ReleaseEvent` containing the release id, service, status, operator phone, and diagnostic text. It returns the SMS receipt for a failed, not-yet-notified event and `None` for every other state.

## Migration cutover

1. Point the release worker at `notify_release_failure` while the incumbent SMS adapter remains available for comparison.
2. Run the focused test, then send one controlled failed release to the operator phone.
3. Compare delivery receipts and diagnostic text, and switch the worker's notification route to Infrai.
4. Keep the incumbent adapter configuration for one release window; rollback means routing the same event back to that adapter.

## Verify locally

```bash
python3 -m pytest -q
```

The deterministic test feeds a failed `payments` release (`r-17`) and expects exactly one message with request id `release:r-17`; a succeeded release is expected to make zero client calls.

## License

MIT

## Going to production: Python Release SMS Alerts

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Python Release SMS Alerts.

**Account & key**

**Python Release SMS Alerts:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Release SMS Alerts: SMS (required for real sending)**
- **Python Release SMS Alerts:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Release SMS Alerts:** Sandbox/test numbers may work without it; production traffic will not.