# DOS Data Entry — Transit

A simple UI for transit department DOS (Days of Service) data entry, replacing cramped Excel tables with a card-based, one-employee-at-a-time flow.

## Deploy to Railway

Connect this repo in [Railway](https://railway.app) — it will auto-detect Python and deploy. On first visit, upload your DOS Excel (.xlsx) to get started.

## Local development

```bash
# Quick start (extract + open static UI)
./run.sh ~/Downloads/3.9.26.xlsx
```

Or run the web app locally:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
# Open http://localhost:5000
```

## What it does

1. **Buckets employees** — Operators vs supervisors (supervisors are marked **Skip**)
2. **Card view** — Each employee’s runs shown as cards instead of dense table rows
3. **Planned vs actual** — Highlights guarantee runs (<8 hrs) and overtime (>8 hrs)
4. **Data entry fields** — Guarantee hrs, OT type (CTE/LPI), notes
5. **Progress** — Mark done, clear progress when starting a new day
6. **Export** — Download entries as CSV for reference during TimeClockPlus entry

## Files

- `app.py` — Flask app for web/Railway deployment
- `extract_dos_data.py` — Extracts run data from Excel
- `static/index.html` — Data entry UI (served by app)
- `bucket_employees.py` — Standalone bucketing script
- `index.html` — Local static build (embedded data, no server)

## Data entry flow

1. Use **Operators** filter (default) to hide supervisors.
2. Click an employee in the list or use Previous/Next.
3. Review each run card (paddle, block, hours, notes).
4. Enter guarantee hrs, OT type, notes as needed.
5. Click **Mark Done & Next**.
6. Use **Export** to download a CSV of your entries.

Progress and entries are stored in browser `localStorage` — use **Clear** when starting a new day.
