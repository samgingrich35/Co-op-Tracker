# Co-op-Tracker
A place to store information on applied co-ops/Internships with data on what position and date of application.

Built with Python, Flask, and SQLite.

## Features
- Add an application: company, role, location, date applied, deadline, job posting link, status, and notes
- Statuses: interested, applied, interviewing, offer, rejected
- View all applications in a table
- Filter by status, and sort by clicking a column heading (click again to reverse)
- Edit and delete applications

## Setup (Windows PowerShell, first time only)
Requires Python 3.12 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app init-db
```

If `Activate.ps1` gives an "execution policy" error, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

> **Warning:** `flask --app app init-db` erases all saved applications. Only run it during setup, or when you want to start over.

## Running the app

```powershell
.\.venv\Scripts\Activate.ps1
flask --app app run --debug
```

Then open http://127.0.0.1:5000 in your browser. Press Ctrl+C in PowerShell to stop the server.

## Project files
| File | Purpose |
|---|---|
| `app.py` | The Flask app and all routes (pages) |
| `db.py` | Database connection helpers and the `init-db` command |
| `schema.sql` | Creates the `applications` table |
| `templates/` | HTML pages: `base.html` (layout), `index.html` (list), `form.html` (add/edit) |
| `requirements.txt` | Python packages to install |
| `instance/tracker.db` | Your data (created by `init-db`, not uploaded to GitHub) |
