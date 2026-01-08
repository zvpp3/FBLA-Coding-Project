# LocalLink — local-business browser (Python + PySide6)

LocalLink is a compact desktop example app for discovering and bookmarking local businesses. It is a small starter template built with Python and the PySide6 GUI toolkit.

Key features
-- Business list with search and filtering \n
-- Detail view with reviews and special deals \n
-- Favorites/bookmarks persisted to `data/user_data.json` \n
-- Settings page with theme selection (dark/light), the ability to reduce motion \n
   animations, toggle recommendations, and require confirmation before removing favourites \n
-- CSV export of all businesses or only your favourites \n
-- Statistics page showing counts and average ratings per category plus personalised recommendations \n
-- Expanded business dataset with a diverse selection of 50 local businesses and hundreds of realistic reviews \n

Requirements
- Python 3.14 or later
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
- Use the **Settings** page from the navigation bar to switch between light and dark
  themes, turn motion animations on or off, enable or disable recommendations,
  require confirmations when removing favourites or change other preferences.  From
  this page you can also export all businesses or only your favourites to a CSV file for
  sharing or analysis.

Project layout
- `main.py` — application entry point and window setup
- `ui/` — UI widgets and window pages (captcha, sidebar, business views)
- `data/` — sample data (`businesses.json`) and the data handler (`data_handler.py`)
- `assets/` — static assets (captcha images, icons)
