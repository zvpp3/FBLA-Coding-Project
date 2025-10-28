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

        # helper to create nav buttons
        def make_button(text: str, idx: int) -> QPushButton:
            btn = QPushButton(text)
            btn.setObjectName("navButton")
            btn.setMinimumHeight(36)
            btn.clicked.connect(lambda _, i=idx: self.button_selected.emit(i))
            layout.addWidget(btn)
            return btn

        self.btn_home = make_button("Home", 0)
        self.btn_biz = make_button("Businesses", 1)
        self.btn_fav = make_button("Favorites", 2)
        self.btn_exit = make_button("Exit", 3)

        layout.addStretch()