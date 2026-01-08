from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class Sidebar(QWidget):
    # Signal
    button_selected = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        # Layout
        self.setFixedWidth(220)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 24, 12, 24)

        # helper to create nav buttons
        def make_button(text: str, name: str) -> QPushButton:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setMinimumHeight(36)
            btn.clicked.connect(lambda _, name=name: self.button_selected.emit(name))
            layout.addWidget(btn)
            return btn

        # Primary navigation buttons
        self.btn_home = make_button("Home", "home")
        self.btn_biz = make_button("Search", "search")
        self.btn_fav = make_button("Favorites", "favorites")
        self.btn_stats = make_button("Stats", "stats")
        self.btn_help = make_button("Help", "help")
        # Settings button to configure preferences
        self.btn_settings = make_button("Settings", "settings")
        # You can add more buttons here if needed

        layout.addStretch()