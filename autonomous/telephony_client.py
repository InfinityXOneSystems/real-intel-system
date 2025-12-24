"""Resilient telephony client with retries and optional status polling."""
import logging
import time
from typing import Optional, Dict

import requests

logger = logging.getLogger(__name__)


def _retry(fn, retries=3, backoff=1.0, allowed_exceptions=(Exception,)):
    last = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except allowed_exceptions as e:
            last = e
            wait = backoff * (2 ** (attempt - 1))
            logger.warning('Attempt %d failed: %s; retrying in %.1fs', attempt, e, wait)
            time.sleep(wait)
    logger.exception('All retries failed')
    raise last


def make_call(account_sid: str, auth_token: str, to_number: str, from_number: str, twiml_url: Optional[str] = None, retries: int = 3) -> Dict:
    twiml_url = twiml_url or 'https://demo.twilio.com/welcome/voice/'

    def _do():
        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json'
        resp = requests.post(url, auth=(account_sid, auth_token), data={'To': to_number, 'From': from_number, 'Url': twiml_url}, timeout=30)
        resp.raise_for_status()
        try:
            return {'success': True, 'sid': resp.json().get('sid')}
        except Exception:
            return {'success': True, 'sid': None, 'raw': resp.text}

    return _retry(_do, retries=retries, backoff=1.0, allowed_exceptions=(requests.RequestException,))


def send_sms(account_sid: str, auth_token: str, to_number: str, from_number: str, body: str, retries: int = 3) -> Dict:
    def _do():
        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
        resp = requests.post(url, auth=(account_sid, auth_token), data={'To': to_number, 'From': from_number, 'Body': body}, timeout=30)
        resp.raise_for_status()
        try:
            return {'success': True, 'sid': resp.json().get('sid')}
        except Exception:
            return {'success': True, 'sid': None, 'raw': resp.text}

    return _retry(_do, retries=retries, backoff=1.0, allowed_exceptions=(requests.RequestException,))
