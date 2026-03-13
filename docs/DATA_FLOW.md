# How Data Is Stored — DOS Data Entry App

## Overview

The app has **two storage layers** and **two modes of use**.

---

## Web App (Railway / `python app.py`)

### 1. Server-side (Python / in-memory)

| What        | Where                    | Persists?                         |
|-------------|--------------------------|-----------------------------------|
| DOS data    | `_dos_data` global var   | No — lost on server restart       |
| (employees, runs, etc.) | Flask app memory | Railway redeploy = fresh start    |

- **No database.** When you upload an Excel file, it’s parsed and stored in a Python variable.
- If the Railway service restarts (redeploy, crash, sleep), `_dos_data` is cleared and you need to upload again.
- `POST /api/clear` sets `_dos_data = None` so the app returns to the upload screen on reload.

### 2. Client-side (Browser `localStorage`)

| What                 | Key                        | Persists?                    |
|----------------------|----------------------------|------------------------------|
| “Done” employee IDs  | `dos_data_entry_done`      | Yes — until you clear it     |
| Notes per employee   | `dos_data_entry_entries`   | Yes — until you clear it     |

- Lives in the browser, per origin (e.g. your Railway URL).
- Survives page reloads and closing the tab.
- Survives server restarts (but without server data, the app shows the upload form).
- Clear manually via the **Clear** button, or by clearing site data in the browser.

---

## Local Static (`index.html` from `build_ui.py`)

### Data source

- DOS data is **embedded** in the HTML at build time (from `dos_data.json`).
- No server; you open the file directly in the browser.
- To change data: run `extract_dos_data.py` on a new Excel file, then run `build_ui.py`.

### Client-side (same as web)

- Progress and notes are in `localStorage` the same way as in the web app.
- **Clear** removes progress and notes for this origin (the `file://` URL or local server).

---

## Buttons

| Button       | Web app                                      | Local static                  |
|--------------|-----------------------------------------------|-------------------------------|
| **Clear**    | Clears progress + notes; keeps DOS data        | Same                          |
| **Start Fresh** | Clears server data, progress, notes; reload → upload screen | Not shown (no server) |

---

## Starting completely fresh (web app)

1. Click **Start Fresh** (or call `POST /api/clear`).
2. This clears server data, progress, notes, and reloads.
3. You get the upload screen and can upload a new Excel file.
