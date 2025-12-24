import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_sms_safe(
    to_number: str, body: str, from_number: Optional[str] = None, dry_run: bool = True
) -> dict:
    """Send SMS with dry-run safety. Returns dict with success, sid, error."""
    if dry_run:
        logger.info("Dry-run: would send SMS to %s body=%s", to_number, body)
        return {"success": True, "sid": None, "error": None, "dry_run": True}
    # Real implementation using Twilio REST API. Credentials are read from
    # Secret Manager via gcloud to avoid in-repo secrets. Returns SID on success.
    try:
        from services.real_estate_intelligence.autonomous.secrets_helper import \
            get_infinityxone_credentials
        from services.real_estate_intelligence.autonomous.telephony_client import \
            send_sms

        creds = get_infinityxone_credentials()
        account_sid = creds.get("twilio_account_sid") or creds.get("TWILIO_ACCOUNT_SID")
        auth_token = creds.get("twilio_auth_token") or creds.get("TWILIO_AUTH_TOKEN")
        fromnum = (
            from_number
            or creds.get("twilio_from_number")
            or creds.get("TWILIO_FROM_NUMBER")
        )

        if not (account_sid and auth_token and fromnum):
            return {
                "success": False,
                "sid": None,
                "error": "twilio creds or from number missing",
                "dry_run": False,
            }

        return send_sms(account_sid, auth_token, to_number, fromnum, body)
    except Exception as e:
        logger.exception("SMS send failed")
        return {"success": False, "sid": None, "error": str(e), "dry_run": False}
