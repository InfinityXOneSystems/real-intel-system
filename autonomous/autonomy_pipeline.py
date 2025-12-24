import logging

from integrations.mcp_client import MCPClient

from services.real_estate_intelligence.autonomous.evaluation_harness import \
    run_scoring_pipeline
from services.real_estate_intelligence.autonomous.ingestion_sink import \
    write_records_to_gcs
from services.real_estate_intelligence.autonomous.sids_store import store_sids
from services.real_estate_intelligence.autonomous.sms_adapter import \
    send_sms_safe
from services.real_estate_intelligence.autonomous.telephony_adapter import \
    make_call_safe
from services.real_estate_intelligence.autonomous.tracing import init_tracing

logger = logging.getLogger(__name__)


def run_full_pipeline(sample_records, to_number, from_number=None, dry_run=True):
    # init_tracing returns None or tracer provider; we wrap usage defensively
    tracer = init_tracing("autonomy-pipeline")
    results = {"dry_run": dry_run}

    # inbound: ingest
    try:
        if tracer:
            with tracer.start_as_current_span("ingest"):
                ingest_res = write_records_to_gcs(
                    sample_records,
                    "infinity-xone-telemetry",
                    "ingest/sample.json",
                    dry_run=dry_run,
                )
        else:
            ingest_res = write_records_to_gcs(
                sample_records,
                "infinity-xone-telemetry",
                "ingest/sample.json",
                dry_run=dry_run,
            )
        results["ingest"] = ingest_res
    except Exception as e:
        results["ingest"] = {"success": False, "error": str(e)}

    # scoring
    try:
        if tracer:
            with tracer.start_as_current_span("scoring"):
                score_res = run_scoring_pipeline(sample_records, dry_run=dry_run)
        else:
            score_res = run_scoring_pipeline(sample_records, dry_run=dry_run)
        results["scoring"] = score_res
    except Exception as e:
        results["scoring"] = {"success": False, "error": str(e)}

    # telephony
    call_res = None
    sms_res = None
    try:
        if tracer:
            with tracer.start_as_current_span("telephony"):
                call_res = make_call_safe(
                    to_number, from_number=from_number, dry_run=dry_run
                )
                sms_res = send_sms_safe(
                    to_number,
                    "We found a property of interest. We will follow up by email.",
                    from_number=from_number,
                    dry_run=dry_run,
                )
        else:
            call_res = make_call_safe(
                to_number, from_number=from_number, dry_run=dry_run
            )
            sms_res = send_sms_safe(
                to_number,
                "We found a property of interest. We will follow up by email.",
                from_number=from_number,
                dry_run=dry_run,
            )
    except Exception as e:
        call_res = {"success": False, "error": str(e)}
        sms_res = {"success": False, "error": str(e)}
    results["call"] = call_res
    results["sms"] = sms_res

    # MCP integration: create a GPT command to summarize results
    try:
        if tracer:
            with tracer.start_as_current_span("mcp"):
                if dry_run:
                    results["mcp"] = {
                        "success": True,
                        "dry_run": True,
                        "response": "would send gpt_command",
                    }
                else:
                    client = MCPClient()
                    resp = client.gpt_command(
                        "autonomy-agent",
                        "Summarize leads and next actions",
                        github_action=None,
                    )
                    results["mcp"] = {"success": True, "response": resp}
        else:
            if dry_run:
                results["mcp"] = {
                    "success": True,
                    "dry_run": True,
                    "response": "would send gpt_command",
                }
            else:
                client = MCPClient()
                resp = client.gpt_command(
                    "autonomy-agent",
                    "Summarize leads and next actions",
                    github_action=None,
                )
                results["mcp"] = {"success": True, "response": resp}
    except Exception as e:
        results["mcp"] = {"success": False, "error": str(e)}

    # Persist SIDs securely if this was a real run
    try:
        if not dry_run:
            meta = {
                "timestamp": __import__("time").time(),
                "call": call_res,
                "sms": sms_res,
                "ingest": results.get("ingest"),
                "scoring": results.get("scoring"),
                "mcp": results.get("mcp"),
            }
            store_res = store_sids(meta)
            results["sids_store"] = store_res
    except Exception as e:
        results["sids_store"] = {"success": False, "error": str(e)}

    return results


if __name__ == "__main__":
    # simple runner
    sample = [{"id": 1, "address": "123 Main St"}]
    res = run_full_pipeline(sample, "+17722090266", from_number=None, dry_run=True)
    print(res)
