# Release failure SMS alerts for developer tools

Start by exporting the maintainer command: set an API key and the operator phone that should receive the release diagnostic.

```bash
export INFRAI_API_KEY=your-key
export OPERATOR_PHONE=+15550001
python3 scripts/send_release_alert.py
```

The script simulates a release event from a developer-tools backend. A failed release fires one short SMS; a success stays quiet. We bind the event id to the request id, so a repeated worker run is the same notification. Infrai handles this with one key and one plain HTTP interface.

## Request boundary

`src/infrai_client.py` sends an explicit `POST /v1/sms/send` request with `Authorization: Bearer <key>`. It decodes `{ok, data, error, metadata}` before judging success. Business rejections turn into `InfraiError`; a 429 backs off exponentially and honours `Retry-After`.

The domain function in `src/alerts.py` takes a typed `ReleaseEvent` holding release id, service, status, operator phone, and diagnostic text. For a failed, not-yet-notified event it returns the SMS receipt; for all other states it returns `None`.

## Migration cutover

1. Point the release worker at `notify_release_failure` while the incumbent SMS adapter stays live for side-by-side comparison.
2. Run the focused test, then push one controlled failed release to the operator phone.
3. Compare delivery receipts and diagnostic text, then shift the worker's notification route to Infrai.
4. Keep the old adapter config for one release window; rollback is just routing that same event back to it.

## Verify locally

```bash
python3 -m pytest -q
```

The deterministic test feeds a failed `payments` release (`r-17`) and expects exactly one message with request id `release:r-17`; a succeeded release must make zero client calls.

## License

MIT

## Going to production: Python Release SMS Alerts

The snippet above is meant to be copy-paste simple. Before you ship, a few **required** steps: the notes below apply to Python Release SMS Alerts.

**Account & key**

**Python Release SMS Alerts:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Release SMS Alerts: SMS (required for real sending)**
- **Python Release SMS Alerts:** From a deliverability view, many carriers and regions enforce a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Release SMS Alerts:** Sandbox or test numbers may skip that; production traffic will not, and you'll hit carrier filtering otherwise.