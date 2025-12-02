<<<<<<< HEAD
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
=======
the [PySide6](https://doc.qt.io/qtforpython-6/) GUI framework.  It
# LocalLink — a small local-business browser (starter template)

This repository contains a compact example desktop app that helps you
discover local businesses. It was built as a small FBLA project
template using Python and PySide6 and includes:

- a business list with search
- a detail view with reviews and deals
- a simple favorites/bookmarks feature (saved to `data/user_data.json`)

This version focuses on simplicity and easy customization — use it as
a starting point for your own features.

Quick start
1. Install dependencies (Python 3.9+ recommended):

```bash
python3 -m pip install -r requirements.txt
```

2. Run the app:

```bash
python3 main.py
```

3. Try it:
- Click "Businesses" in the sidebar, pick an item, then click the
  star in the top-right of the detail view to favorite/unfavorite.
- Open "Favorites" to see saved businesses (persisted between runs).

Project layout
- `main.py` — entry point and primary window (uses `data/` and `ui/`).
- `data/` — sample business data and a simple data handler.
- `ui/` — small UI components split into pages and widgets.

Notes and next steps
- Businesses use stable `id` values (see `data/businesses.json`) so
  favorites are robust if names change.
- The data handler is intentionally simple. If you want server sync
  or a database backend, I can help wire that up.

If you'd like, I can also:
- add tests for the data handler
- switch the star glyph to an icon
- add sorting / filters (by rating or category)

If you want any of the above, tell me which and I'll add it.
>>>>>>> efab7ce3798974cad4726836cd6917ad4baef2fe
