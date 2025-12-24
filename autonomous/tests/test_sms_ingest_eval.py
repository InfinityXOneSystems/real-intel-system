from services.real_estate_intelligence.autonomous.evaluation_harness import \
    run_scoring_pipeline
from services.real_estate_intelligence.autonomous.ingestion_sink import \
    write_records_to_gcs
from services.real_estate_intelligence.autonomous.sms_adapter import \
    send_sms_safe


def test_sms_dryrun():
    res = send_sms_safe("+17722090266", "test", from_number=None, dry_run=True)
    assert res["success"] is True
    assert res["dry_run"] is True


def test_ingest_dryrun():
    records = [{"id": 1}, {"id": 2}]
    res = write_records_to_gcs(records, "test-bucket", "path/out.json", dry_run=True)
    assert res["success"] is True
    assert res["dry_run"] is True


def test_eval_dryrun():
    records = [{"a": 1}]
    res = run_scoring_pipeline(records, dry_run=True)
    assert res["success"] is True
    assert res["dry_run"] is True
