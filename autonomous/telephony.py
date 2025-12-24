"""Telephony integration: Twilio + Google Cloud TTS scaffold.

This module will:
- Read credentials from Secret Manager (secret: infinityxone-credentials)
- Extract Twilio account SID/auth token and 'from' number
- Optionally synthesize TTS with Google Cloud TTS and upload to GCS
- Place outbound calls via Twilio (using TwiML or Play URL)

This is a scaffold. It will NOT place calls unless valid Twilio credentials are found.
"""

import base64
import json
import os
from typing import Optional

import requests

try:
    from google.cloud import secretmanager, storage, texttospeech
except Exception:
    secretmanager = None
    texttospeech = None
    storage = None


SECRET_NAME = os.environ.get("INFINITY_SECRET_NAME", "infinityxone-credentials")
GCP_PROJECT = os.environ.get(
    "GOOGLE_CLOUD_PROJECT", os.environ.get("GOOGLE_PROJECT") or "infinity-x-one-systems"
)


def get_secret_payload(secret_name: str = SECRET_NAME) -> Optional[dict]:
    if secretmanager is None:
        print("google-cloud-secretmanager not installed or unavailable")
        return None
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{GCP_PROJECT}/secrets/{secret_name}/versions/latest"
    try:
        resp = client.access_secret_version(request={"name": name})
        data = resp.payload.data
        if isinstance(data, bytes):
            text = data.decode("utf-8")
        else:
            text = data
        return json.loads(text)
    except Exception as e:
        print("Failed to read secret:", e)
        return None


def get_twilio_creds_from_secret(secret: dict) -> Optional[dict]:
    # secret is expected to contain keys like 'twilio_account_sid', 'twilio_auth_token', 'twilio_from_number'
    if not secret:
        return None
    keys = ["twilio_account_sid", "twilio_auth_token", "twilio_from_number"]
    if all(k in secret for k in keys):
        return {k: secret[k] for k in keys}
    # Try nested structure
    for k in secret.keys():
        if isinstance(secret[k], dict):
            nested = secret[k]
            if all(x in nested for x in keys):
                return {x: nested[x] for x in keys}
    return None


def synthesize_text_to_gcs(
    text: str, bucket_name: str, object_name: str
) -> Optional[str]:
    if texttospeech is None or storage is None:
        print("Google Cloud TTS or Storage libs unavailable; skipping TTS")
        return None
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.upload_from_string(response.audio_content, content_type="audio/mpeg")
    # Make public (optional)
    try:
        blob.make_public()
    except Exception:
        pass
    return blob.public_url


def place_call_twilio(
    to_number: str,
    twiml: Optional[str] = None,
    play_url: Optional[str] = None,
    twilio_creds: Optional[dict] = None,
):
    creds = twilio_creds or {}
    account_sid = creds.get("twilio_account_sid")
    auth_token = creds.get("twilio_auth_token")
    from_number = creds.get("twilio_from_number")
    if not account_sid or not auth_token or not from_number:
        print("Twilio credentials missing; cannot place call")
        return {"status": "no-creds"}

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Calls.json"
    data = {
        "To": to_number,
        "From": from_number,
    }
    if play_url:
        # Build TwiML to play the URL
        twiml_str = f"<Response><Play>{play_url}</Play></Response>"
        data["Twiml"] = twiml_str
    elif twiml:
        data["Twiml"] = twiml
    else:
        data["Twiml"] = (
            '<Response><Say voice="alice">This is an automated call from InfinityXOne systems.</Say></Response>'
        )

    try:
        resp = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print("Twilio call failed:", e, getattr(e, "response", None))
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    # Quick secret check and report
    sec = get_secret_payload()
    creds = get_twilio_creds_from_secret(sec) if sec else None
    print("Secret found:", bool(sec))
    print("Twilio creds found:", bool(creds))
