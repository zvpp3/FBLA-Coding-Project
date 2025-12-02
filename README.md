# LocalLink — local-business browser (Python + PySide6)

LocalLink is a compact desktop example app for discovering and bookmarking local businesses. It is a small starter template built with Python and the PySide6 GUI toolkit.

Key features
- Business list with search
- Detail view with reviews and deals
- Favorites/bookmarks persisted to `data/user_data.json`

Requirements
- Python 3.9 or later
- See `requirements.txt` for Python packages (includes `PySide6`).

Install
1. Create and activate a Python virtual environment (recommended).

Windows (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the app

```bash
python main.py
```

Usage
- Open the "Businesses" page to browse and search the sample businesses.
- Select an item to view details, reviews, and available deals.
- Click the star icon in the detail view to add or remove a business from `Favorites`.
- Favorites are stored in `data/user_data.json` and persist between runs.

Project layout
- `main.py` — application entry point and window setup
- `ui/` — UI widgets and window pages (captcha, sidebar, business views)
- `data/` — sample data (`businesses.json`) and the data handler (`data_handler.py`)
- `assets/` — static assets (captcha images, icons)

Developer notes
- The data handler is intentionally minimal; swapping to a database or remote API requires changes in `data/data_handler.py`.
- The GUI uses fixed sizes for the main window and captcha widget. Adjust values in `ui/captcha_window.py` if different layouts are required.