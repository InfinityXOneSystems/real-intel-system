"""Helper to write ingest records to GCS with ADC fallback to local file system.

Provides `write_to_gcs_or_local(bucket, object_name, data_bytes)` which attempts
to upload bytes to GCS using `google.cloud.storage`. If that library or credentials
are missing, writes to `local_ingest/<bucket>/<object_name>` and returns the local path.
"""

import json
import logging
import os
import time
from typing import Tuple

logger = logging.getLogger(__name__)


def write_to_gcs_or_local(
    bucket: str,
    object_name: str,
    data_bytes: bytes,
    retries: int = 3,
    backoff: float = 1.0,
) -> Tuple[bool, str]:
    """Try uploading `data_bytes` to GCS path 'gs://<bucket>/<object_name>' with retries.

    Returns (True, gcs_url) on success, or (False, local_path) on fallback.
    """
    try:
        from google.cloud import storage

        client = storage.Client()
        bucket_obj = client.bucket(bucket)
        blob = bucket_obj.blob(object_name)

        last_exc = None
        for attempt in range(1, retries + 1):
            try:
                blob.upload_from_string(data_bytes)
                gcs_url = f"gs://{bucket}/{object_name}"
                logger.info("Uploaded to %s", gcs_url)
                return True, gcs_url
            except Exception as e:
                last_exc = e
                wait = backoff * (2 ** (attempt - 1))
                logger.warning(
                    "GCS upload attempt %d failed: %s; retrying in %.1fs",
                    attempt,
                    e,
                    wait,
                )
                time.sleep(wait)
        logger.exception("GCS upload failed after retries", exc_info=last_exc)
    except Exception:
        logger.exception("GCS upload missing or library not available")

    # Fallback to local file
    local_dir = os.path.join("local_ingest", bucket)
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, object_name.replace("/", "_"))
    with open(local_path, "wb") as f:
        f.write(data_bytes)
    return False, local_path
