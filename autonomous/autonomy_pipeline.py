import logging
from services.real_estate_intelligence.autonomous.telephony_adapter import make_call_safe
from services.real_estate_intelligence.autonomous.sms_adapter import send_sms_safe
from services.real_estate_intelligence.autonomous.ingestion_sink import write_records_to_gcs
from services.real_estate_intelligence.autonomous.evaluation_harness import run_scoring_pipeline
from services.real_estate_intelligence.autonomous.tracing import init_tracing
from integrations.mcp_client import MCPClient

logger = logging.getLogger(__name__)


def run_full_pipeline(sample_records, to_number, from_number=None, dry_run=True):
    tracer = init_tracing('autonomy-pipeline')
    results = {"dry_run": dry_run}

    with tracer.start_as_current_span('ingest'):
        ingest_res = write_records_to_gcs(sample_records, 'infinity-xone-telemetry', 'ingest/sample.json', dry_run=dry_run)
        results['ingest'] = ingest_res

    with tracer.start_as_current_span('scoring'):
        score_res = run_scoring_pipeline(sample_records, dry_run=dry_run)
        results['scoring'] = score_res

    with tracer.start_as_current_span('telephony'):
        call_res = make_call_safe(to_number, from_number=from_number, dry_run=dry_run)
        results['call'] = call_res
        sms_res = send_sms_safe(to_number, 'We found a property of interest. We will follow up by email.', from_number=from_number, dry_run=dry_run)
        results['sms'] = sms_res

    # MCP integration: create a GPT command to summarize results
    with tracer.start_as_current_span('mcp'):
        if dry_run:
            results['mcp'] = {"success": True, "dry_run": True, "response": "would send gpt_command"}
        else:
            try:
                client = MCPClient()
                resp = client.gpt_command('autonomy-agent', 'Summarize leads and next actions', github_action=None)
                results['mcp'] = {"success": True, "response": resp}
            except Exception as e:
                results['mcp'] = {"success": False, "error": str(e)}

    return results


if __name__ == '__main__':
    # simple runner
    sample = [{'id': 1, 'address': '123 Main St'}]
    res = run_full_pipeline(sample, '+17722090266', from_number=None, dry_run=True)
    print(res)
