
import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)

from ui.sidebar import Sidebar
from ui.pages import (
    HomePage,
    SearchPage,
    FavoritesPage,
    BusinessPage,
    Page,
    ReviewPage,
)
from data.data_handler import (
    DataHandler,
    Business,
)
from typing import List, Dict

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

        # Page container
        self.pages: Dict[Page] = {
            "home": HomePage(self.data),
            "search": SearchPage(self.data),
            "favorites": FavoritesPage(self.data),
            "business": BusinessPage(self.data),
            "review": ReviewPage(self.data)
        }

        # Wire signals
        self.pages["search"].show_business_details.connect(lambda biz: self._set_page("business", biz))
        self.pages["favorites"].show_business_details.connect(lambda biz: self._set_page("business", biz))
        self.pages["business"].leave_review_clicked.connect(lambda biz: self._set_page("business", biz))
        self.pages["review"].review_submitted_signal.connect(lambda: self._set_page("business", self.pages["business"].business))

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
            
        self._set_page("home")

        # Sidebar behavior
        self.sidebar.button_selected.connect(self.sidebar_button_selected)

        # Load stylesheet
        if apply_style:
            qss_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "style.qss")
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf8") as file:
                    self.setStyleSheet(file.read())

    #  Event handlers
    def sidebar_button_selected(self, name: str) -> None:

        # Exit button
        if name == "exit":
            self.close()

        self._set_page(name)   

    def _set_page(self, page: str, data = None):
        for other_page in self.pages.values():
            other_page.setVisible(False)
        self.pages[page].setVisible(True)
        self.pages[page].page_shown(data)
        self.scroll_area.verticalScrollBar().setValue(0)