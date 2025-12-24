# Real Estate Intelligence Templates

This folder contains the Platinum REI system templates split into three categories:

- `PF/` — Investor-facing feed templates (PF_*)
- `OL/` — Ops Ledger / audit trail templates (OL_*)
- `TL/` — Templates library (TL_*)

Location of original archive: `_legacy_or_experiments/duplicates_backup_20251224T032513/real-estate-intelligence/templates_and_docs/templates and docs/`

Tab map:
- PF_LIVE_FEED -> `PF/PF_LIVE_FEED.csv`
- PF_PRIME_ONLY -> `PF/PF_PRIME_ONLY.csv`
- PF_BUYERS -> `PF/PF_BUYERS.csv`
- PF_INFLUENCERS -> `PF/PF_INFLUENCERS.csv`
- PF_DASHBOARD -> `PF/PF_DASHBOARD.csv`
- PF_PROOF_PACK_LINKS -> `PF/PF_PROOF_PACK_LINKS.csv`

- OL_RUNS -> `OL/OL_RUNS.csv`
- OL_TASK_LEDGER -> `OL/OL_TASK_LEDGER.csv`
- OL_CRAWL_JOBS -> `OL/OL_CRAWL_JOBS.csv`
- OL_RAW_EVENTS_INDEX -> `OL/OL_RAW_EVENTS_INDEX.csv`
- OL_ENTITY_RESOLUTION -> `OL/OL_ENTITY_RESOLUTION.csv`
- OL_SCORECARD -> `OL/OL_SCORECARD.csv`
- OL_PREDICTIONS -> `OL/OL_PREDICTIONS.csv`
- OL_VALIDATION_LOG -> `OL/OL_VALIDATION_LOG.csv`
- OL_PUBLISH_LOG -> `OL/OL_PUBLISH_LOG.csv`
- OL_OUTREACH_LOG -> `OL/OL_OUTREACH_LOG.csv`
- OL_APPOINTMENTS_LOG -> `OL/OL_APPOINTMENTS_LOG.csv`

- TL_GPT_TRIGGERS -> `TL/TL_GPT_TRIGGERS.csv`
- TL_VALIDATOR_PROMPTS -> `TL/TL_VALIDATOR_PROMPTS.csv`
- TL_CALL_SCRIPTS -> `TL/TL_CALL_SCRIPTS.csv`
- TL_EMAIL_TEMPLATES -> `TL/TL_EMAIL_TEMPLATES.csv`
- TL_SMS_TEMPLATES -> `TL/TL_SMS_TEMPLATES.csv`
- TL_DISPOSITION_RULES -> `TL/TL_DISPOSITION_RULES.csv`
- TL_FOLLOWUP_CADENCE -> `TL/TL_FOLLOWUP_CADENCE.csv`
- TL_CALENDAR_EVENT_SCHEMAS -> `TL/TL_CALENDAR_EVENT_SCHEMAS.csv`

Use `tools/map_rei_to_templates.py` to map REI crawl rows into these templates.
