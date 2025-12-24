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
        import subprocess, base64, json, requests

        p = subprocess.run([
            'gcloud', 'secrets', 'versions', 'access', 'latest',
            '--secret=infinityxone-credentials', '--project=infinity-x-one-systems',
            '--format=get(payload.data)'
        ], capture_output=True, text=True)
        if p.returncode != 0:
            return {"success": False, "sid": None, "error": f"secret access failed: {p.stderr}", "dry_run": False}
        creds = json.loads(base64.b64decode(p.stdout.strip()).decode('utf-8'))

        account_sid = creds.get('twilio_account_sid') or creds.get('TWILIO_ACCOUNT_SID')
        auth_token = creds.get('twilio_auth_token') or creds.get('TWILIO_AUTH_TOKEN')
        fromnum = from_number or creds.get('twilio_from_number') or creds.get('TWILIO_FROM_NUMBER')

        if not (account_sid and auth_token and fromnum):
            return {"success": False, "sid": None, "error": "twilio creds or from number missing", "dry_run": False}

        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json'
        # Use TwiML URL to play demo or provided URL
        resp = requests.post(url, auth=(account_sid, auth_token), data={'To': to_number, 'From': fromnum, 'Url': 'https://demo.twilio.com/welcome/voice/'}, timeout=30)
        try:
            jr = resp.json()
        except Exception:
            jr = {'text': resp.text}
        if resp.status_code >= 400:
            return {"success": False, "sid": None, "error": jr, "dry_run": False}
        return {"success": True, "sid": jr.get('sid'), "error": None, "dry_run": False}
    except Exception as e:
        logger.exception("Call failed via REST fallback")
        return {"success": False, "sid": None, "error": str(e), "dry_run": False}


def send_sms_via_twilio_stub(*args, **kwargs):
    # Placeholder to integrate real SMS sending later. Keep dry-run behavior.
    return {"success": True, "sid": None, "dry_run": True}
