"""
Lightweight Google Workspace connectors used by the autonomous orchestrator.
This module provides simple helper functions to read Sheets, post to Drive, send Gmail, and create Calendar events.
Requires proper credentials via GOOGLE_APPLICATION_CREDENTIALS or ADC.
"""
from typing import Optional, Dict, Any
import os
import json

from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/tasks'
]


def _get_creds(creds_path: Optional[str] = None):
    creds_path = creds_path or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_path and os.path.exists(creds_path):
        with open(creds_path, 'r', encoding='utf-8-sig') as f:
            info = json.load(f)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    # Fallback to ADC
    from google.auth import default as adc_default
    creds, _ = adc_default(scopes=SCOPES)
    return creds


def read_sheet(sheet_id: str, range_name: str, creds_path: Optional[str] = None):
    creds = _get_creds(creds_path)
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()


def send_gmail_message(to: str, subject: str, body: str, creds_path: Optional[str] = None):
    creds = _get_creds(creds_path)
    service = build('gmail', 'v1', credentials=creds)
    message = {
        'raw': None
    }
    # Note: building raw MIME messages omitted for brevity; caller should create base64-encoded raw string
    return {'status': 'not-implemented', 'note': 'Use send_gmail_raw to send base64-encoded message'}


def create_calendar_event(calendar_id: str, event: Dict[str, Any], creds_path: Optional[str] = None):
    creds = _get_creds(creds_path)
    service = build('calendar', 'v3', credentials=creds)
    return service.events().insert(calendarId=calendar_id, body=event).execute()


def upload_file_to_drive(folder_id: str, name: str, file_path: str, creds_path: Optional[str] = None):
    creds = _get_creds(creds_path)
    service = build('drive', 'v3', credentials=creds)
    from googleapiclient.http import MediaFileUpload
    file_metadata = {'name': name, 'parents': [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    return service.files().create(body=file_metadata, media_body=media, fields='id').execute()
