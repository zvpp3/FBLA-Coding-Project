from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QVBoxLayout,
)

from data.data_handler import (
    Business,
    DataHandler,
)

from typing import Optional

class FavoriteButton(QPushButton):
    """ A simple button that communicates with the data handler to add and remove favorite businesses """
    click_signal = Signal()

    def __init__(self, data: DataHandler, biz: Business, size: str = "small") -> None:
        super().__init__()
        self.data = data
        self.business = biz
        self.clicked.connect(self._on_click)
        self.setObjectName("favButtonSmall" if size == "small" else "favButtonLarge")
        self._refresh()

    def _on_click(self) -> None:
        if self.business and self.data:
            self.data.toggle_favorite(self.business)
        self.click_signal.emit()
        self._refresh()

    def _refresh(self) -> None:
        if self.business and self.data:
            if self.data.is_favorite(self.business):
                self.setText("★")
                self.setStyleSheet("color: #f1c40f;")
                return
        self.setText("☆")
        self.setStyleSheet("color: #ffffff;")
    
    def set_business(self, biz: Business) -> None:
        self.business = biz
        self._refresh()

    def enterEvent(self, event):
        self.setText("★")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._refresh()
        super().leaveEvent(event)


class ListedBusiness(QPushButton):
    """ The type of element to go inside BusinessLists (see below) """
    main_button_signal = Signal(Business)

    def __init__(self, data: DataHandler, biz: Business):
        super().__init__()
        self.business = biz
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        item_text = f"{biz.name} ({biz.category}) - ⭐ {biz.rating:.1f}"
        label = QLabel(item_text)
        layout.addWidget(label)
        layout.addStretch()
        self.favorite_button = FavoriteButton(data, biz, "small")
        layout.addWidget(self.favorite_button)
        self.favorite_button.setVisible(False)
        self.clicked.connect(lambda: self.main_button_signal.emit(self.business))

    def enterEvent(self, event):
        self.favorite_button.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.favorite_button.setVisible(False)
        super().leaveEvent(event)


class BusinessList(QScrollArea):
    """ A way to list businesses, such as in search results or the favorites page 
    If this causes performance issues this can be changed to a QListView or similar"""

    # To be called for wiring purposes, etc.
    business_added_signal = Signal(ListedBusiness)

    def __init__(self, data: DataHandler) -> None:
        super().__init__()

        # Business Container
        business_container = QWidget()
        self.business_container_layout = QVBoxLayout()
        business_container.setLayout(self.business_container_layout)

        # Set Properties
        self.setWidgetResizable(True); self.setWidget(business_container)

        # Data
        self.data = data

    def _clear_list(self) -> None:
        while self.business_container_layout.count():
            item = self.business_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
    
    def _add_business_to_list(self, biz: Business) -> None:
        item = ListedBusiness(biz)
        self.business_container_layout.addWidget(item)

    def populate(self, query: str = "", onlyFavs: bool = False) -> None:
        self._clear_list()

        if query:
            filtered_list = self.data.search(query)
        elif onlyFavs:
            filtered_list = self.data.favorite_businesses()
            # for biz in filtered_list:
            #     print(biz.name)
        else:
            filtered_list = self.data.list_businesses()

        for biz in filtered_list:
            item = ListedBusiness(self.data, biz)
            self.business_container_layout.addWidget(item)
            self.business_added_signal.emit(item)

        self.business_container_layout.addStretch()