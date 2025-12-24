"""Centralized helper to fetch and cache secrets from GCP Secret Manager using gcloud.

This is a small shim to avoid repeated subprocess calls throughout the runtime.
It reads secret `infinityxone-credentials` and returns the decoded JSON payload.
"""
import subprocess
import base64
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_CACHE: Optional[Dict] = None


def get_infinityxone_credentials(project: str = "infinity-x-one-systems") -> Dict:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    try:
        p = subprocess.run([
            'gcloud', 'secrets', 'versions', 'access', 'latest',
            '--secret=infinityxone-credentials', '--project=' + project,
            '--format=get(payload.data)'
        ], capture_output=True, text=True)
        if p.returncode != 0:
            raise RuntimeError(f"gcloud secret access failed: {p.stderr}")
        payload_b64 = p.stdout.strip()
        creds = json.loads(base64.b64decode(payload_b64).decode('utf-8'))
        _CACHE = creds
        return creds
    except Exception as e:
        logger.exception('Failed to read infinityxone-credentials')
        raise
