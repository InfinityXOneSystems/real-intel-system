"""Simple BigQuery helper to insert rows into a dataset.table using ADC.

This is a minimal wrapper. It will raise if google-cloud-bigquery is not available
or ADC is not configured. The calling code should handle fallback to Storage/local.
"""

import logging
import time
from typing import Dict, List

logger = logging.getLogger(__name__)


def insert_rows(
    project: str,
    dataset: str,
    table: str,
    rows: List[Dict],
    retries: int = 5,
    backoff: float = 1.0,
    max_backoff: float = 16.0,
) -> Dict:
    """Insert rows into BigQuery table with exponential backoff retries.

    Returns dict {'success': True} on success or {'success': False, 'errors': ...} on partial failure.
    Raises if fatal error after retries.
    """
    try:
        from google.api_core.exceptions import GoogleAPICallError, RetryError
        from google.cloud import bigquery
    except Exception:
        logger.exception("BigQuery client library not available")
        raise

    client = bigquery.Client(project=project)
    table_ref = client.dataset(dataset).table(table)

    attempt = 0
    while True:
        try:
            errors = client.insert_rows_json(table_ref, rows)
            if errors:
                logger.error("BigQuery insert errors: %s", errors)
                return {"success": False, "errors": errors}
            return {"success": True}
        except (GoogleAPICallError, RetryError) as e:
            attempt += 1
            if attempt > retries:
                logger.exception("BigQuery insert failed after retries")
                raise
            sleep_for = min(max_backoff, backoff * (2 ** (attempt - 1)))
            logger.warning(
                "BigQuery insert transient error, retry %d/%d in %.1fs: %s",
                attempt,
                retries,
                sleep_for,
                str(e),
            )
            time.sleep(sleep_for)
        except Exception:
            logger.exception("BigQuery insert unexpected error")
            raise
