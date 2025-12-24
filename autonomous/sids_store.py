"""Securely store SIDs and runtime metadata for live runs.

Uses AES-GCM encryption with a key obtained from Secret Manager (`infinityxone-credentials` key
`sids_encryption_key`) if present. If secret key missing, generates a local key and stores it
in `local_secrets/sids_key` with restrictive permissions.

Data is written to `runtime_sids/<timestamp>_<nonce>.json.enc` and returns the storage path.
"""

import base64
import json
import logging
import os
import time
from typing import Dict, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)


def _get_key_from_secret_manager() -> Optional[bytes]:
    try:
        import subprocess

        p = subprocess.run(
            [
                "gcloud",
                "secrets",
                "versions",
                "access",
                "latest",
                "--secret=infinityxone-credentials",
                "--project=infinity-x-one-systems",
                "--format=get(payload.data)",
            ],
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            return None
        payload_b64 = p.stdout.strip()
        creds = json.loads(base64.b64decode(payload_b64).decode("utf-8"))
        key_b64 = creds.get("sids_encryption_key")
        if not key_b64:
            return None
        return base64.b64decode(key_b64)
    except Exception:
        logger.exception("Failed to retrieve sids_encryption_key from secret manager")
        return None


def _ensure_local_key(path: str = "local_secrets/sids_key") -> bytes:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    # generate random 32-byte key
    key = AESGCM.generate_key(bit_length=256)
    with open(path, "wb") as f:
        f.write(key)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass
    return key


def get_encryption_key() -> bytes:
    key = _get_key_from_secret_manager()
    if key:
        return key
    return _ensure_local_key()


def store_sids(metadata: Dict) -> Dict:
    """Encrypt and persist metadata; return {'success': True, 'path': path} or error."""
    try:
        key = get_encryption_key()
        aes = AESGCM(key)
        nonce = os.urandom(12)
        data = json.dumps(metadata, default=str).encode("utf-8")
        ct = aes.encrypt(nonce, data, None)
        ts = int(time.time())
        os.makedirs("runtime_sids", exist_ok=True)
        filename = f"runtime_sids/{ts}_{base64.urlsafe_b64encode(nonce).decode('ascii')}.json.enc"
        with open(filename, "wb") as f:
            f.write(nonce + ct)
        return {"success": True, "path": filename}
    except Exception as e:
        logger.exception("Failed to store SIDs")
        return {"success": False, "error": str(e)}
