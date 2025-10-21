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