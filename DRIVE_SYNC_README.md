## Real Estate Intelligence - Google Drive Sync

This document explains how to sync the Google Drive folder for the Real Estate Intelligence workspace into the repository.

Folder ID: `1kUpV-7tChk05pc6l3x00sVQr-X6_P9Jm`

Preferred methods:

- Use `rclone` (fast, resumable). Configure a remote named `gdrive` with `rclone config`. Then run the provided PowerShell script:

```powershell
.
Set-Location <repo-root>
.
tools\sync_drive_rei.ps1
```

- Or use the Python downloader (interactive OAuth). Place your OAuth `credentials.json` in the repo root and run:

```powershell
python tools\drive_download.py --folder-id 1kUpV-7tChk05pc6l3x00sVQr-X6_P9Jm --out services\real-estate-intelligence\drive_sync
```

After syncing, the folder `services/real-estate-intelligence/drive_sync` will contain the drive contents. Use `tools/map_rei_to_templates.py` to map crawled CSVs into repository templates and `tools/push_rei_to_memory.py` to index data.

If using a service account, make sure the service account has access to the Drive folder (share the folder with the SA's email) and set `GOOGLE_APPLICATION_CREDENTIALS` to the SA JSON path before using the Python downloader.

Service Account (recommended for automation):

- Ensure the service account JSON exists in `secrets/vertex-sa.json` (you mentioned this SA is the same account and is already synced with Google Workspace).
- Share the Drive folder with the service account's email address (the SA must be explicitly granted access to the folder).
- Run the SA downloader:

```powershell
python tools\drive_download_sa.py --sa-key secrets\vertex-sa.json --folder-id 1kUpV-7tChk05pc6l3x00sVQr-X6_P9Jm --out services\real-estate-intelligence\drive_sync
```

Notes:
- If the folder is a Shared Drive, additional `supportsAllDrives=True` flags may be required in the code. Contact me if you need that change and I'll add it.

