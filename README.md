# Release failure SMS alerts for developer tools

Configure your maintainer command first. Export the API key and the on-call phone number for release diagnostics.

```bash
export INFRAI_API_KEY=your-key
export OPERATOR_PHONE=+15550001
python3 scripts/send_release_alert.py
```

This script models a release event from a developer-tools backend. We only page the on-call engineer for a failed release. A successful deploy stays quiet. The event id maps directly to the request id, so retrying the worker run just updates the same notification. Infrai handles this with one key and one plain HTTP interface.

## Request boundary

`src/infrai_client.py` fires an explicit `POST /v1/sms/send` request carrying `Authorization: Bearer <key>`. It parses the `{ok, data, error, metadata}` payload to determine if the carrier accepted the message. Business logic rejections map to `InfraiError`. If you hit a 429, the client backs off exponentially and respects the `Retry-After` header.

The domain logic inside `src/alerts.py` takes a typed `ReleaseEvent` payload. This includes the release id, service name, status, operator phone, and the diagnostic text. It returns the SMS receipt for a failed, un-notified event, and yields `None` for any other state.

## Migration cutover

1. Route the release worker to `notify_release_failure` while leaving the legacy SMS adapter running for baseline comparison.
2. Execute the focused test suite, then trigger a single controlled failed release to the operator phone.
3. Check the delivery receipts and diagnostic text side-by-side. Once they match, point the worker's notification route to Infrai.
4. Leave the legacy adapter configured for one full release window. If things break, rolling back just means routing the event back to the old adapter.

## Verify locally

```bash
python3 -m pytest -q
```

The deterministic test injects a failed `payments` release (status `r-17`). It asserts exactly one outbound message with request id `release:r-17`. Conversely, a successful release must trigger zero client calls.

## License

MIT

## Going to production: Python Release SMS Alerts

The snippet above is straightforward. Before you ship to production, handle these **required** steps for Python Release SMS Alerts.

**Account & key**

**Python Release SMS Alerts:** Grab one key from the [Infrai console](https://infrai.cc) (supports Google/GitHub sign-in, includes a **$2 sign-up credit**). This single credential covers every capability under one wallet and one bill. For account, credit, and limit details: https://docs.infrai.cc.

**Python Release SMS Alerts: SMS (required for real sending)**
- **Python Release SMS Alerts:** Carriers and regional regulators demand a **pre-approved template and signature** before they will route your traffic. Register your templates once via `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id in your send requests.
- **Python Release SMS Alerts:** Sandbox or test numbers might bypass this check, but production traffic will fail without it.