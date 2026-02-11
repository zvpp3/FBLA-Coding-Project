"""
This module is for the main window of LocalLink.

The main window contains the sidebar navigation and the page container
that holds all the different pages (Home, Search, Favorites, Business Details, Reviews, Stats, Help, Settings).

"""

# all imports
import os

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QGraphicsOpacityEffect,
)
from typing import Dict

from ui.sidebar import Sidebar
from ui.pages import (
    HomePage,
    SearchPage,
    FavoritesPage,
    BusinessPage,
    Page,
    ReviewPage,
    StatsPage,
    HelpPage,
)

from ui.settings_page import SettingsPage
from data.data_handler import DataHandler

# Main window class
class MainWindow(QMainWindow):
    # establish an init function for the main window
    def __init__(self, data: DataHandler, apply_style: bool = True) -> None:
        # super init ensures that attributes and behaviors are defined, and calls the initializer
        super().__init__()

        self.setWindowTitle("LocalLink")
        self.resize(1000, 600)
        self.data = data
        
        # Ensures the window always stays on top of other windows, so it doesn't get lost behind them. 
        # This is important for user experience, especially if the app is minimized or if the user has many windows open. 
        # It keeps the app easily accessible and prevents confusion about where it went.
        if self.data.get_preference("always_on_top", "no").lower() == "yes":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # this is the icon for our window
        self.setWindowIcon(QIcon("assets/logo.png"))

        # main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # sidebar
        self.sidebar = Sidebar()

        # page container: create all pages. pages that need the main window
        # (like Settings) get a reference so they can change app-wide stuff
        self.pages: Dict[str, Page] = {
            "home": HomePage(self.data),
            "search": SearchPage(self.data),
            "favorites": FavoritesPage(self.data),
            "business": BusinessPage(self.data),
            "review": ReviewPage(self.data),
            "stats": StatsPage(self.data),
            "help": HelpPage(self.data),
            "settings": SettingsPage(self.data, self),
        }

        # wire signals for pages
        self.pages["search"].show_business_details.connect(lambda biz: self._set_page("business", biz))
        self.pages["favorites"].show_business_details.connect(lambda biz: self._set_page("business", biz))
        self.pages["business"].leave_review_clicked.connect(lambda biz: self._set_page("review", biz))

        # get position is for returning to search page at the same scroll position if we use the back button
        self.pages["business"].back_to_search.connect(lambda: self._set_page("search", restore_search_pos=True))

        # when a review is submitted, go back to the business page and pass
        # the business that was being reviewed (the review page holds it).
        # review_submitted_signal now emits the Business so just forward it
        # directly to _set_page to ensure the BusinessPage updates immediately.
        self.pages["review"].review_submitted_signal.connect(
            lambda biz: self._set_page("business", biz)
        )

        # back/cancel from review page should also return to the business page
        if hasattr(self.pages["review"], "review_cancelled_signal"):
            self.pages["review"].review_cancelled_signal.connect(
                lambda biz: self._set_page("business", biz)
            )

        # stats page may emit a business clicked signal for recommendations
        if hasattr(self.pages.get("stats"), "show_business_details"):
            self.pages["stats"].show_business_details.connect(lambda biz: self._set_page("business", biz))

        # page container widgets
        self.page_container = QWidget()
        self.container_layout = QVBoxLayout()
        self.page_container.setLayout(self.container_layout)

        # scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.page_container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)

        self.search_page_scrollbar_pos = 0

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.scroll_area)

        for page in self.pages.values():
            self.container_layout.addWidget(page)

        # track the current page name for animations
        self.current_page_name: str = "home"

        # store animation refs so gc doesn't drop them
        self.current_animation = None
        self.fade_out_effect = None
        self.fade_in_effect = None

        # initially show the home page
        self._set_page("home")

        # sidebar behavior
        self.sidebar.button_selected.connect(self.sidebar_button_selected)

        # apply the stylesheet from prefs. fallback to dark if none
        if apply_style:
            self.load_styles()

    def load_styles(self) -> None:
        # Load and apply the QSS file for the chosen theme. Falls back to
        # dark theme if the requested file is missing.
        # Determine theme preference from the data handler

        preferred_theme = self.data.get_preference("theme", "dark").lower()
        # Map themes to QSS filenames
        theme_files = {
            "dark": "style.qss",
            "light": "style_light.qss",
        }

        # Resolve the filename or fall back to dark theme
        qss_file = theme_files.get(preferred_theme, "style.qss")
        qss_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), qss_file)
        if os.path.exists(qss_path):
            try:
                with open(qss_path, "r", encoding="utf8") as fh:
                    qss = fh.read()
                self.setStyleSheet(qss)
            except Exception:
                # Fallback to no style if reading fails
                self.setStyleSheet("")
        else:
            # If the file does not exist, clear styles
            self.setStyleSheet("")

    def apply_preferences(self) -> None:
        # apply current preferences that affect app-wide behavior.
        # this reloads styles and cancels any running animations so
        # changes like reduce_motion take effect immediately.
        try:
            # reload styles based on the current theme preference
            self.load_styles()
        except Exception:
            # non-fatal; continue to clear animations below
            pass

        # stop any running animation and clear references
        if getattr(self, "current_animation", None):
            try:
                self.current_animation.stop()
            except Exception:
                pass
            self.current_animation = None

        # remove graphics effects from pages so they render normally
        for page in getattr(self, "pages", {}).values():
            try:
                if page.graphicsEffect() is not None:
                    page.setGraphicsEffect(None)
            except Exception:
                # ignore errors cleaning up pages
                pass

    # Event handlers
    def sidebar_button_selected(self, name: str) -> None:

        # exit button
        if name == "exit":
            self.close()
            return

        self._set_page(name)   

    def _set_page(self, page: str, data=None, restore_search_pos: bool = False) -> None:
        # switch to the requested page. skip fade animations for heavy
        # pages (like business or stats) to avoid rendering glitches

        if self.current_page_name == "search":
            self.search_page_scrollbar_pos = self.scroll_area.verticalScrollBar().value()

        target = self.pages[page]

        # Compute the value of the scrollbar position to restore after the page switch. 
        # If we're returning to the search page, use the stored position; otherwise, reset to the top.
        desired_scroll = self.search_page_scrollbar_pos if restore_search_pos else 0

        # Pages that should NOT use the opacity effect to avoid glitches
        heavy_pages = {"business", "stats"}

        # Stop any running animation
        if self.current_animation:
            self.current_animation.stop()
            self.current_animation = None

        # Remove any leftover graphics effects from all pages
        for other_page in self.pages.values():
            if other_page.graphicsEffect() is not None:
                other_page.setGraphicsEffect(None)

        # Hide all pages, then show target only
        for other_page in self.pages.values():
            other_page.setVisible(False)
        target.setVisible(True)

        # Let the page refresh its own content BEFORE we animate
        target.page_shown(data)

        # Restore scroll AFTER layout updates
        def apply_scroll():
            bar = self.scroll_area.verticalScrollBar()
            bar.setValue(min(desired_scroll, bar.maximum()))

        QTimer.singleShot(0, apply_scroll)

        # track current page name
        self.current_page_name = page

        # keep sidebar highlight in sync (business/review pages won't change it)
        if hasattr(self.sidebar, "set_active"):
            self.sidebar.set_active(page)

        # Check reduce_motion user preference. If enabled, skip animations.
        reduce_motion_pref = self.data.get_preference("reduce_motion", "no").lower()

        # For heavy/complex pages, or if reduce_motion is enabled, skip
        # animations entirely to avoid glitches or motion.
        if page in heavy_pages or reduce_motion_pref == "yes":
            return

        # Lightweight pages: apply a simple fade-in on the target page
        self.fade_in_effect = QGraphicsOpacityEffect(target)
        target.setGraphicsEffect(self.fade_in_effect)

        # QPropertyAnimation allows us to animate properties of Qt objects
        fade_in = QPropertyAnimation(self.fade_in_effect, b"opacity", self)
        fade_in.setDuration(400)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)

        # Keep a reference so it isn't garbage-collected mid-animation
        self.current_animation = fade_in

        # When the animation finishes, drop the graphics effect so the page
        # paints normally afterwards.
        def _cleanup_effect():
            if target.graphicsEffect() is self.fade_in_effect:
                target.setGraphicsEffect(None)
            self.current_animation = None

        fade_in.finished.connect(_cleanup_effect)
        fade_in.start()


