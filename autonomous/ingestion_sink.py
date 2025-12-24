import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def write_records_to_gcs(
    records: List[Dict], bucket: str, path: str, dry_run: bool = True
) -> dict:
    """Write JSON records to GCS using storage_helper with local fallback."""
    if dry_run:
        logger.info(
            "Dry-run: would write %d records to gs://%s/%s", len(records), bucket, path
        )
        return {"success": True, "uri": f"gs://{bucket}/{path}", "dry_run": True}
    try:
        from services.real_estate_intelligence.autonomous.storage_helper import \
            write_to_gcs_or_local

        ok, uri = write_to_gcs_or_local(
            bucket, path, json.dumps(records).encode("utf-8")
        )
        if ok:
            res = {"success": True, "uri": uri, "dry_run": False}
            # Optionally insert into BigQuery if configured via env
            try:
                import os

                if os.getenv("AUTONOMY_INSERT_BIGQUERY", "false").lower() in (
                    "1",
                    "true",
                ):
                    from services.real_estate_intelligence.autonomous.bigquery_helper import \
                        insert_rows

                    project = os.getenv("AUTONOMY_BIGQUERY_PROJECT")
                    dataset = os.getenv("AUTONOMY_BIGQUERY_DATASET")
                    table = os.getenv("AUTONOMY_BIGQUERY_TABLE")
                    if project and dataset and table:
                        insert_res = insert_rows(project, dataset, table, records)
                        res["bigquery"] = insert_res
            except Exception:
                logger.exception("BigQuery insertion attempt failed")
            return res
        else:
            return {"success": True, "uri": f"file://{uri}", "dry_run": False}
    except Exception as e:
        logger.exception("Ingestion sink failed")
        return {"success": False, "error": str(e)}
