import os
import logging
from typing import Optional

try:
    from telephony_quickstart import make_call as quick_make_call
except Exception:
    quick_make_call = None

logger = logging.getLogger(__name__)


def make_call_safe(to_number: str, from_number: Optional[str] = None, dry_run: bool = True) -> dict:
    """Make a call using the quickstart helper with safety gating.

    Returns a dict with keys: success(bool), sid(str|None), error(str|None), dry_run(bool)
    """
    if dry_run:
        logger.info("Dry-run: would place call to %s from %s", to_number, from_number)
        return {"success": True, "sid": None, "error": None, "dry_run": True}
    # If quick_make_call (twilio SDK) is available, use it. Otherwise fall back
    # to a REST call using requests and credentials from Secret Manager.
    if quick_make_call:
        try:
            sid = quick_make_call(to_number, from_number)
            return {"success": True, "sid": sid, "error": None, "dry_run": False}
        except Exception as e:
            logger.exception("Call via SDK failed, will attempt REST fallback")

    try:
        from services.real_estate_intelligence.autonomous.secrets_helper import get_infinityxone_credentials
        from services.real_estate_intelligence.autonomous.telephony_client import make_call

        creds = get_infinityxone_credentials()
        account_sid = creds.get('twilio_account_sid') or creds.get('TWILIO_ACCOUNT_SID')
        auth_token = creds.get('twilio_auth_token') or creds.get('TWILIO_AUTH_TOKEN')
        fromnum = from_number or creds.get('twilio_from_number') or creds.get('TWILIO_FROM_NUMBER')

        if not (account_sid and auth_token and fromnum):
            return {"success": False, "sid": None, "error": "twilio creds or from number missing", "dry_run": False}

        return make_call(account_sid, auth_token, to_number, fromnum)
    except Exception as e:
        logger.exception("Call failed via REST fallback")
        return {"success": False, "sid": None, "error": str(e), "dry_run": False}


def send_sms_via_twilio_stub(*args, **kwargs):
    # Placeholder to integrate real SMS sending later. Keep dry-run behavior.
    return {"success": True, "sid": None, "dry_run": True}
