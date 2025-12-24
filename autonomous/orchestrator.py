"""Autonomous orchestrator for the Real Estate Intelligence system.
This orchestrator performs: seeds -> crawl -> ingest -> score -> analyze -> outreach
All steps are dry-run safe and designed to be extended.
"""
import os
import requests
import time
from typing import List, Dict

from .gws_connectors import read_sheet, create_calendar_event

CRAWLER_ENDPOINT = os.environ.get('CRAWLER_ENDPOINT', 'https://crawler-control-896380409704.us-east1.run.app/crawl')


def load_seeds_from_sheet(sheet_id: str, range_name: str) -> List[Dict]:
    res = read_sheet(sheet_id, range_name)
    values = res.get('values', [])
    if not values:
        return []
    header = values[0]
    rows = values[1:]
    out = []
    for r in rows:
        d = {header[i]: (r[i] if i < len(r) else '') for i in range(len(header))}
        out.append(d)
    return out


def post_crawl_job(job: Dict, dry_run: bool = True):
    if dry_run:
        print('DRY RUN: would post job', job)
        return {'status': 'dry-run'}
    resp = requests.post(CRAWLER_ENDPOINT, json=job, timeout=30)
    resp.raise_for_status()
    return resp.json()


def orchestrate(sheet_id: str, range_name: str, dry_run: bool = True):
    seeds = load_seeds_from_sheet(sheet_id, range_name)
    results = []
    for s in seeds:
        job = {
            'source': 'google_drive',
            'sheet': sheet_id,
            'seed_url': s.get('seed_url') or s.get('seed') or '',
            'type': s.get('type') or 'generic',
            'county': s.get('county'),
            'priority': s.get('priority') or 'normal'
        }
        res = post_crawl_job(job, dry_run=dry_run)
        results.append(res)
        time.sleep(0.5)
    return results


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--sheet-id', required=True)
    p.add_argument('--range', default='Sheet1!A1:Z')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    print(orchestrate(args.sheet_id, args.range, dry_run=args.dry_run))
