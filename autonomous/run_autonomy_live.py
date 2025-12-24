"""CLI to run the autonomy pipeline (dry-run by default).

Usage:
  python run_autonomy_live.py --to +1772... [--from +1...] [--dry-run]

This runner initializes tracing and calls `run_full_pipeline`. It prints a small summary
and the encrypted sids_store path if present.
"""
import argparse
import logging
from services.real_estate_intelligence.autonomous.autonomy_pipeline import run_full_pipeline

logging.basicConfig(level=logging.INFO)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--to', required=True)
    p.add_argument('--from', dest='from_', required=False)
    p.add_argument('--dry-run', action='store_true', default=False)
    args = p.parse_args()

    sample = [{'id': 1, 'address': '123 Main St', 'description': 'vacant foreclosure auction'}]
    res = run_full_pipeline(sample, args.to, from_number=args.from_, dry_run=args.dry_run)
    print('RESULT SUMMARY:')
    print('  dry_run:', res.get('dry_run'))
    print('  call:', res.get('call'))
    print('  sms:', res.get('sms'))
    if res.get('sids_store'):
        print('  sids_store:', res.get('sids_store'))


if __name__ == '__main__':
    main()
