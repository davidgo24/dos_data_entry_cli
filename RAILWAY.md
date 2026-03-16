# Railway deployment

## Quick deploy

1. Go to [railway.app](https://railway.app) and sign in
2. **New Project** → **Deploy from GitHub repo** → select `davidgo24/dos_data_entry_cli`
3. Railway auto-detects Python and deploys from the Procfile
4. Add variable: `SECRET_KEY` = any random string (required for production sessions)
5. **Generate Domain** to get your public URL

## Multi-user behavior

Each visitor gets an isolated session (cookie-based). Coworkers:

- Use the same Railway URL from their computers
- Upload their own DOS file (stored per-session on the server)
- Manage their own CTE list (stored in browser localStorage)
- Export their own entries (localStorage + selections)
- Progress and notes are per-browser (localStorage)

No shared data between users. Each person works independently.

## Environment variables

| Variable    | Required | Description                          |
|------------|----------|--------------------------------------|
| `SECRET_KEY` | Yes (prod) | Random string for Flask session signing |
| `PORT`     | No       | Set by Railway automatically         |
