
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
        self.pages = QStackedWidget()
        self.home_page = HomePage(self.data)
        self.search_page = SearchPage(self.data)
        self.favorites_page = FavoritesPage(self.data)
        self.business_page = BusinessPage(self.data)
        self.review_page = ReviewPage(self.data)

        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.search_page)
        self.pages.addWidget(self.favorites_page)
        self.pages.addWidget(self.business_page)
        self.pages.addWidget(self.review_page)

        # Wire signals
        self.search_page.show_business_details.connect(self.open_business_page)
        self.favorites_page.show_business_details.connect(self.open_business_page)
        self.business_page.leave_review_clicked.connect(lambda biz: self.open_review_page(biz))
        self.review_page.review_submitted_signal.connect(lambda: self.open_business_page(self.business_page.business))

        # Scroll Area
        self.scroll_area = QScrollArea()

        self.scroll_area.setWidget(self.pages)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.scroll_area)

        # Sidebar behavior
        self.sidebar.button_selected.connect(self.sidebar_button_selected)

        # Load stylesheet
        if apply_style:
            qss_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "style.qss")
            if os.path.exists(qss_path):
                with open(qss_path, "r", encoding="utf8") as file:
                    self.setStyleSheet(file.read())

    #  Event handlers
    def sidebar_button_selected(self, index: int) -> None:
        # Switch page if button is home, search, or favorites
        if index >= 0 and index <= 2:
            self.pages.setCurrentIndex(index)

            current = self.pages.currentWidget()
            if isinstance(current, Page):
                current.page_shown()

        # Exit button
        if index == 3:
            self.close()

    def open_business_page(self, biz: Business) -> None:
        self.business_page.set_business(biz)
        self.pages.setCurrentIndex(3)
    
    def open_review_page(self, biz: Business) -> None:
        self.review_page.set_business(biz)
        self.pages.setCurrentIndex(4)