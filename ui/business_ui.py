from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel

from data.data_handler import BusinessRecord
from typing import Optional


class FavoriteButton(QPushButton):
    """Lightweight favorite control. Caller manages persistence and visual state."""
    click_signal = Signal()

    def __init__(self, business: Optional[BusinessRecord] = None, size: str = "small"):
        super().__init__()
        self.business = business
        self.clicked.connect(self._on_click)
        self.setObjectName("favButtonSmall" if size == "small" else "favButtonLarge")
        self._refresh()

    def _on_click(self) -> None:
        self.click_signal.emit()
        self._refresh()

    def set_business(self, business: BusinessRecord) -> None:
        self.business = business
        self._refresh()

    def _refresh(self) -> None:
        if not self.business:
            self.setText("☆")
            return
        # default to outline; caller may change text after toggling favorite
        self.setText("☆")

    def enterEvent(self, event):
        self.setText("★")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._refresh()
        super().leaveEvent(event)


class ListedBusiness(QPushButton):
    main_button_clicked = Signal(BusinessRecord)
    favorite_button_clicked = Signal(BusinessRecord)

    def __init__(self, biz: BusinessRecord):
        super().__init__()
        self.business = biz
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        item_text = f"{biz.name} ({biz.category}) - ⭐ {biz.rating:.1f}"
        label = QLabel(item_text)
        layout.addWidget(label)
        layout.addStretch()
        self.favorite_button = FavoriteButton(biz, "small")
        layout.addWidget(self.favorite_button)
        self.favorite_button.setVisible(False)
        self.clicked.connect(lambda: self.main_button_clicked.emit(self.business))
        self.favorite_button.click_signal.connect(lambda: self.favorite_button_clicked.emit(self.business))

    def enterEvent(self, event):
        self.favorite_button.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.favorite_button.setVisible(False)
        super().leaveEvent(event)