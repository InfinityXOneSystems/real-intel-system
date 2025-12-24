Autonomy helpers
================

This folder contains helper modules used by the autonomy pipeline:

- `production_scorer.py` — deterministic heuristic scorer for leads.
- `secrets_helper.py` — centralized GCP Secret Manager accessor (cached).
- `storage_helper.py` — GCS upload with local fallback.
- `telephony_client.py` — resilient Twilio REST client (retries/backoff).
- `bigquery_helper.py` — minimal BigQuery insertion helper (ADC required).
- `tracing.py` — OpenTelemetry initialization helper.
- `sids_store.py` — secure SIDs/encrypted run metadata store (AES-GCM).

Run the unit tests in `tests/` with pytest. Ensure `gcloud` is configured
for secret access in non-dry runs if you want secret-backed key storage.
