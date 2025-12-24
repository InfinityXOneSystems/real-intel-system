#!/usr/bin/env python3
"""
Read crawl seed rows from a Google Sheet and post jobs to the crawler control endpoint.

Prereqs:
- Enable Google Sheets API and Google Drive API on project
- Set environment variable `GOOGLE_APPLICATION_CREDENTIALS` pointing to service account JSON
- Share the Drive folder / sheet with the service account (or use OAuth creds)

Usage:
  python run_seed_crawl.py --sheet-id <SPREADSHEET_ID> --range "Sheet1!A1:Z" --endpoint https://crawler-control-896380409704.us-east1.run.app/crawl --dry-run

The sheet is expected to have a header row with columns such as:
  source,type,priority,seed_url,county,notes

This script will convert each row into a JSON job and POST it to the control endpoint.
"""
import argparse
import csv
import json
import os
import sys
from typing import List, Dict

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build


def read_sheet(sheet_id: str, range_name: str, creds) -> List[Dict]:
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    values = result.get('values', [])
    if not values:
        return []
    header = values[0]
    rows = values[1:]
    out = []
    for r in rows:
        entry = {header[i].strip(): (r[i].strip() if i < len(r) else '') for i in range(len(header))}
        out.append(entry)
    return out


def build_job(row: Dict) -> Dict:
    job = {
        'source': row.get('source') or 'sheet',
        'type': row.get('type') or 'generic',
        'priority': row.get('priority') or 'normal',
        'seed_url': row.get('seed_url') or row.get('seed') or row.get('seed_url') or '',
        'county': row.get('county') or '',
        'meta': {k: v for k, v in row.items() if k not in ('source', 'type', 'priority', 'seed_url', 'seed', 'county')}
    }
    return job


def post_job(endpoint: str, job: Dict, dry_run: bool = True) -> Dict:
    if dry_run:
        print('DRY RUN - would post job:', json.dumps(job))
        return {'status': 'dry-run', 'job': job}
    resp = requests.post(endpoint, json=job, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--sheet-id', required=True)
    p.add_argument('--range', default='Sheet1!A1:Z')
    p.add_argument('--endpoint', default='https://crawler-control-896380409704.us-east1.run.app/crawl')
    p.add_argument('--creds', default=os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    if not args.creds or not os.path.exists(args.creds):
        print('ERROR: Google credentials JSON not found. Set GOOGLE_APPLICATION_CREDENTIALS or pass --creds', file=sys.stderr)
        sys.exit(2)

    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']
    # Some service account JSON files may include a UTF-8 BOM. Load using utf-8-sig
    try:
        with open(args.creds, 'r', encoding='utf-8-sig') as f:
            info = json.load(f)
        creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    except Exception:
        # Fallback to library helper which will raise a clearer error if invalid
        try:
            creds = service_account.Credentials.from_service_account_file(args.creds, scopes=scopes)
        except Exception:
            # Try Application Default Credentials (gcloud auth application-default login) as last resort
            print('Warning: service account file invalid; attempting Application Default Credentials (ADC) fallback')
            from google.auth import default as adc_default
            creds, _ = adc_default(scopes=scopes)

    rows = read_sheet(args.sheet_id, args.range, creds)
    if not rows:
        print('No rows found in sheet')
        return

    results = []
    for r in rows:
        job = build_job(r)
        try:
            res = post_job(args.endpoint, job, dry_run=args.dry_run)
            results.append(res)
        except Exception as e:
            print('Failed to post job for seed', job.get('seed_url'), 'error:', str(e))
            results.append({'error': str(e), 'job': job})

    print('\nSummary: posted', len(results), 'jobs')


if __name__ == '__main__':
    main()
