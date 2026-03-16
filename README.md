# DOS Data Entry CLI

Keyboard-first UI for transit department DOS (Days of Service) data entry. Card-based flow with segment export for TimeClockPlus.

## Deploy to Railway

1. Push this repo to GitHub and connect it in [Railway](https://railway.app)
2. Railway auto-detects Python (Procfile, nixpacks.toml)
3. Set `SECRET_KEY` in Railway Variables: any random string (e.g. `openssl rand -hex 24`)
4. Deploy — your app URL will be live

**Multi-user:** Each visitor gets an isolated session. Coworkers use the app from their own computers independently — each uploads their own DOS file, manages their own CTE list, and exports their own entries. No shared state between users.

## Local development

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

Or extract + open static UI (no server):

```bash
./run.sh ~/Downloads/your-dos.xlsx
```

## Features

- **Segment logic** — 1–3 segments per run: 1020 REG, 1000 GUAR, 1013 OT1.5, 3002 CTE; LPI split when `actual_end > planned_end`
- **Per-run selection** — Include/exclude runs; Planned vs Actual; labor code for leave; Day off (paid as OT); Extra time tail (e.g. trainer +2 hrs)
- **TCP export** — One row per segment; `e` export all, `Shift+e` export done only
- **CTE list** — Tab or Manage CTE list; employee IDs who prefer 3002 for OT (badge in list view)
- **Supervisors list** — Tab or Manage Supervisors; exclude from Op view and export
- **Done & undo** — `d` mark done, `Shift+d` or click check to undo
- **Keyboard-first** — `n` next, `p` prev, `d` done, `e` export, `c` clear, `s` fresh, `?` help

## Supported Excel formats

- **Standard** — "Table 1" sheet with SUPERVISORS/ABSENT sections
- **Raw report** — DOS_Report_*.xlsx with date-named sheet; check "Raw report format" when uploading

## Files

- `app.py` — Flask app
- `static/index.html` — Data entry UI
- `config_cte.json` — Optional: employee IDs for 3002 CTE
- `config_supervisors.json` — Optional: supervisor IDs to exclude from Op view and export
- `extract_dos_data.py` — Excel extraction

## Data entry flow

1. Upload DOS Excel
2. Op / All filter; navigate with `n`/`p` or clicks
3. Per run: **Include** if using for export; Planned/Actual; Labor (for leave runs)
4. `d` or Done & Next to mark complete
5. `e` to export TCP CSV

Progress and entries are in browser `localStorage`; `c` clears when starting a new day.
