# Mapping REI Crawl Data Into Templates

Expected workflow:

1. Sync the Google Drive folder into `services/real-estate-intelligence/drive_sync` using the instructions in `DRIVE_SYNC_README.md`.
2. Place or confirm `rei_crawl_data.csv` exists at `services/real-estate-intelligence/reports/rei_crawl_data.csv` (some tools expect this path).
3. Run the mapping tool:

```powershell
python tools\map_rei_to_templates.py --input services\real-estate-intelligence\reports\rei_crawl_data.csv --out services\real-estate-intelligence\mapped_output
```

4. Review the mapped CSVs in `services/real-estate-intelligence/mapped_output` and then push to memory-gateway using `tools/push_rei_to_memory.py`.

Notes:
- Mapping is based on header overlap; ensure the crawl CSV has headers that match or map to template headers.
- If you prefer, open the Google Sheet and export the specific tab as CSV into the repo path.
