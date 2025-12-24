import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_sms_safe(to_number: str, body: str, from_number: Optional[str] = None, dry_run: bool = True) -> dict:
    """Send SMS with dry-run safety. Returns dict with success, sid, error."""
    if dry_run:
        logger.info("Dry-run: would send SMS to %s body=%s", to_number, body)
        return {"success": True, "sid": None, "error": None, "dry_run": True}
    # Real implementation using Twilio REST API. Credentials are read from
    # Secret Manager via gcloud to avoid in-repo secrets. Returns SID on success.
    try:
        import subprocess, base64, json, requests

        # fetch secret payload (base64) and decode
        p = subprocess.run([
            'gcloud', 'secrets', 'versions', 'access', 'latest',
            '--secret=infinityxone-credentials', '--project=infinity-x-one-systems',
            '--format=get(payload.data)'
        ], capture_output=True, text=True)
        if p.returncode != 0:
            return {"success": False, "sid": None, "error": f"secret access failed: {p.stderr}", "dry_run": False}
        payload_b64 = p.stdout.strip()
        creds = json.loads(base64.b64decode(payload_b64).decode('utf-8'))

        account_sid = creds.get('twilio_account_sid') or creds.get('TWILIO_ACCOUNT_SID')
        auth_token = creds.get('twilio_auth_token') or creds.get('TWILIO_AUTH_TOKEN')
        fromnum = from_number or creds.get('twilio_from_number') or creds.get('TWILIO_FROM_NUMBER')

        if not (account_sid and auth_token and fromnum):
            return {"success": False, "sid": None, "error": "twilio creds or from number missing", "dry_run": False}

        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
        resp = requests.post(url, auth=(account_sid, auth_token), data={'To': to_number, 'From': fromnum, 'Body': body}, timeout=30)
        try:
            jr = resp.json()
        except Exception:
            jr = {'text': resp.text}
        if resp.status_code >= 400:
            return {"success": False, "sid": None, "error": jr, "dry_run": False}
        return {"success": True, "sid": jr.get('sid'), "error": None, "dry_run": False}
    except Exception as e:
        logger.exception('SMS send failed')
        return {"success": False, "sid": None, "error": str(e), "dry_run": False}
