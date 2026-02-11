"""
This module contains the sidebar navigation for LocalLink.

The sidebar includes buttons for navigating between different pages
of the application, such as Home, Search, Favorites, Stats, Help, and Settings.
"""

# imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, QButtonGroup

# Sidebar class
class Sidebar(QWidget):
    # signal emitted when a button is selected, with the button name as str
    button_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        # Set fixed width for sidebar
        self.setFixedWidth(220)
        # Set up layout
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 24, 12, 24)

        # Make buttons behave like tabs (only one checked at a time)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        self._buttons: dict[str, QPushButton] = {}

        # button making function to reduce redundancy
        def make_button(text: str, name: str) -> QPushButton:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setMinimumHeight(36)

            btn.setCheckable(True)
            self._group.addButton(btn)
            self._buttons[name] = btn

            btn.clicked.connect(lambda _, n=name: self.button_selected.emit(n))
            layout.addWidget(btn)
            return btn

        # Create sidebar buttons
        self.btn_home = make_button("Home", "home")
        self.btn_biz = make_button("Search", "search")
        self.btn_fav = make_button("Favorites", "favorites")
        self.btn_stats = make_button("Stats", "stats")
        self.btn_help = make_button("Help", "help")
        self.btn_settings = make_button("Settings", "settings")

        # adding stretch to push buttons to top
        layout.addStretch()

        # Default highlight
        self.set_active("home")

    def set_active(self, page_name: str) -> None:
        """This is for highlighting or 'marking' the sidebar tab. If page isn't in the sidebar, keep current highlight."""
        btn = self._buttons.get(page_name)
        if btn:
            btn.setChecked(True)