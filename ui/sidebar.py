from PySide6.QtCore import (
    Qt,
    Signal,
)

from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class Sidebar(QWidget):
    # Signal
    button_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__()

        # Layout
        self.setFixedWidth(220)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 24, 12, 24)

        # Navigation buttons
        self.btn_home = QPushButton("Home")
        self.btn_home.setObjectName("navButton")
        self.btn_home.clicked.connect(lambda: self.button_selected.emit(0))

        self.btn_biz = QPushButton("Businesses")
        self.btn_biz.setObjectName("navButton")
        self.btn_biz.clicked.connect(lambda: self.button_selected.emit(1))

        self.btn_fav = QPushButton("Favorites")
        self.btn_fav.setObjectName("navButton")
        self.btn_fav.clicked.connect(lambda: self.button_selected.emit(2))

        self.btn_about = QPushButton("About")
        self.btn_about.setObjectName("navButton")
        self.btn_about.clicked.connect(lambda: self.button_selected.emit(3))

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setObjectName("navButton")
        self.btn_exit.clicked.connect(lambda: self.button_selected.emit(4))

        # Add buttons to sidebar
        for btn in [self.btn_home, self.btn_biz, self.btn_fav, self.btn_about, self.btn_exit]:
            btn.setMinimumHeight(36)
            layout.addWidget(btn)

        layout.addStretch()