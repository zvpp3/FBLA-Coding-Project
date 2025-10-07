# Byte‑Sized Business Boost

This project is a **starting template** for the FBLA Coding & Programming event
for the 2025‑2026 school year.  The theme, *Byte‑Sized Business Boost*,
challenges teams to build a tool that helps users discover and support
small, local businesses in their community【17924830928865†L29-L48】.  This
repository contains a simple desktop application written in Python using
the [PySide6](https://doc.qt.io/qtforpython-6/) GUI framework.  It
features a modern, dark themed interface inspired by the "PyDracula" UI
shown in the screenshot provided by the project sponsor.

## Features

The template implements a handful of core features that you can build
upon:

- Dark, modern interface with a navigation sidebar and stacked pages.
- Home, Businesses, Favorites, and About pages to structure your app.
- Searchable list of example businesses with categories, ratings, and
  deals.
- Detail pop‑up window for each business showing reviews and promotions.

The **business data** is currently hard‑coded for demonstration
purposes.  In your final application you should replace this with
persistent storage (e.g., a database or API) and implement features
outlined in the FBLA guidelines, such as bookmarking favorites,
allowing users to leave reviews/ratings, sorting, and displaying
special deals【17924830928865†L29-L47】.

## Getting Started

1. **Install dependencies**.  Use Python 3.9 or later.  Install
   [PySide6](https://pypi.org/project/PySide6/) with pip:

   ```bash
   python -m pip install pyside6
   ```

2. **Run the program locally**.  Execute the `main.py` file:

   ```bash
   python main.py
   ```

   You should see a window with the dark theme, navigation sidebar,
   and sample content.  Feel free to explore the pages and search
   through the dummy businesses.

3. **Use Visual Studio Code**.  [VS Code](https://code.visualstudio.com/)
   is a popular editor for Python development.  To work on this
   project:

   - Open VS Code and select **File → Open Folder…**.  Navigate to
     the `fbla_byte_boost` directory.
   - Install the **Python** extension if prompted.  This extension
     enables IntelliSense, debugging, and other helpful features.
   - Use the integrated terminal (``Ctrl+` ``) to run the program
     (`python main.py`) and commit changes to version control.

4. **Collaborate on GitHub**.  The GitHub repository provided by
   your team (e.g. `zvpp3/FBLA-Coding-Project`) is perfect for
   collaboration.  A typical workflow looks like this:

   1. Install Git on your computer if it isn't already installed.
      On Windows you can use [Git for Windows](https://gitforwindows.org/);
      on macOS and Linux Git is usually pre‑installed.
   2. Clone the repository from GitHub:

      ```bash
      git clone https://github.com/zvpp3/FBLA-Coding-Project.git
      ```

   3. Copy or move the `fbla_byte_boost` folder into the cloned
      repository and commit your changes:

      ```bash
      cd FBLA-Coding-Project
      git add fbla_byte_boost
      git commit -m "Add initial PySide6 template for Byte‑Sized Business Boost"
      git push origin main
      ```

   4. Share the repository link with your teammates so they can pull
      the latest code.  When working together, create separate
      branches for new features and open pull requests for review.

## Next Steps

This template is intended as a starting point.  To meet the FBLA
requirements and score highly at competition, consider the following
enhancements:

- **Persistent data storage** for businesses, reviews, ratings, and
  favorites (e.g., using SQLite or an online API).
- **User authentication** or a light verification step (perhaps a
  CAPTCHA) to prevent bot activity【17924830928865†L29-L48】.
- **Sorting and filtering** options beyond search, such as by
  category or rating.
- **Create/update/delete** capabilities for reviews and ratings.
- **Responsive or adaptive layout** to ensure the interface scales
  gracefully on different screen sizes.
- **Presentation preparation** for district and state levels, such as a
  short pitch deck demonstrating your design process and technical
  decisions.

Feel free to modify the code structure, add modules, or change the
design as you see fit.  Good luck with your project!