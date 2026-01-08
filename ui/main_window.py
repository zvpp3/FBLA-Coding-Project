
import os

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
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
class MainWindow(QMainWindow):
    def __init__(self, data: DataHandler, apply_style: bool = True) -> None:
        super().__init__()
        self.setWindowTitle("LocalLink")
        self.resize(1000, 600)
        self.data = data

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = Sidebar()

        # Page container: initialize all pages including new ones
        # Create all pages. Pages that depend on the main window (e.g. settings)
        # are passed a reference to this window to allow them to apply
        # application-wide changes such as switching styles.
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

        # Wire signals for existing pages
        self.pages["search"].show_business_details.connect(lambda biz: self._set_page("business", biz))
        self.pages["favorites"].show_business_details.connect(lambda biz: self._set_page("business", biz))
        self.pages["business"].leave_review_clicked.connect(lambda biz: self._set_page("review", biz))
        self.pages["review"].review_submitted_signal.connect(lambda: self._set_page("business", self.pages["business"].business))

        # Wire signals for new pages
        # Stats page may emit a business clicked signal for recommendations
        if hasattr(self.pages.get("stats"), "show_business_details"):
            self.pages["stats"].show_business_details.connect(lambda biz: self._set_page("business", biz))

        # Page Container
        self.page_container = QWidget()
        self.container_layout = QVBoxLayout()
        self.page_container.setLayout(self.container_layout)

        # Scroll Area
        self.scroll_area = QScrollArea()

        self.scroll_area.setWidget(self.page_container)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.scroll_area)

        for page in self.pages.values():
            self.container_layout.addWidget(page)

        # Track the current page name for animations
        self.current_page_name: str = "home"
        
        # Store animation references to prevent garbage collection
        self.current_animation = None
        self.fade_out_effect = None
        self.fade_in_effect = None

        # Initially show the home page
        self._set_page("home")

        # Sidebar behavior
        self.sidebar.button_selected.connect(self.sidebar_button_selected)

        # Apply the stylesheet according to user preferences. The default
        # implementation falls back to dark if no preference exists. If
        # `apply_style` is False (for unit tests), styles are not loaded.
        if apply_style:
            self.load_styles()

    def load_styles(self) -> None:
        """
        Load and apply the appropriate QSS file based on the user's
        preferences. If the preferred theme is unavailable the dark theme
        is used as a fallback.

        Themes are stored in the same directory as this script. A file
        named `style.qss` provides the dark theme, whereas
        `style_light.qss` defines the light theme. Additional themes
        could be supported by adding corresponding QSS files and mapping
        them here.
        """
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

    #  Event handlers
    def sidebar_button_selected(self, name: str) -> None:

        # Exit button
        if name == "exit":
            self.close()
            return

        self._set_page(name)   

    def _set_page(self, page: str, data=None):
        """
        Switch to the given page.

        We keep a simple fade-in animation for lightweight pages, but
        **skip the effect** for heavier, graphics-intensive pages
        ("business" and "stats"). Those pages contain large images and a
        matplotlib canvas; combining them with QGraphicsOpacityEffect can
        cause Qt to cache a single pixmap and produce the "frozen screenshot"
        effect you were seeing.
        """

        target = self.pages[page]

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

        # Reset scroll position
        self.scroll_area.verticalScrollBar().setValue(0)

        # Hide all pages, then show target only
        for other_page in self.pages.values():
            other_page.setVisible(False)
        target.setVisible(True)

        # Let the page refresh its own content BEFORE we animate
        target.page_shown(data)

        # Track current page name
        self.current_page_name = page

        # Decide if animations should be disabled.  The "reduce_motion"
        # preference comes from the settings page.  When set to "yes" all
        # animations are skipped for accessibility or performance reasons.
        reduce_motion_pref = self.data.get_preference("reduce_motion", "no").lower()
        # For heavy/complex pages, or if reduce_motion is enabled, skip
        # animations entirely to avoid glitches or motion.
        if page in heavy_pages or reduce_motion_pref == "yes":
            return

        # Lightweight pages: apply a simple fade-in on the target page
        self.fade_in_effect = QGraphicsOpacityEffect(target)
        target.setGraphicsEffect(self.fade_in_effect)

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


