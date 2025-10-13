
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
)

from ui.sidebar import Sidebar
from ui.pages import (
    HomePage,
    SearchPage,
    FavoritesPage,
    AboutPage,
    BusinessPage,
)
from data.data_handler import (
    DataHandler,
    Business
)

class MainWindow(QMainWindow):
    def __init__(self, data_handler: DataHandler) -> None:
        super().__init__()

        self.setWindowTitle("LocalLink")
        self.resize(1000, 600)

        self.data = data_handler

        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.sidebar = Sidebar()

        # Page container
        self.pages = QStackedWidget()
        self.home_page = HomePage()
        self.search_page = SearchPage()
        self.favorites_page = FavoritesPage()
        self.about_page = AboutPage()
        self.business_page = BusinessPage()

        self.pages.addWidget(self.home_page)
        self.pages.addWidget(self.search_page)
        self.pages.addWidget(self.favorites_page)
        self.pages.addWidget(self.about_page)
        self.pages.addWidget(self.business_page)

        self.search_page.show_business_details.connect(self.open_business_page)
        self.search_page.search_bar_updated.connect(lambda text: self.search_page.populate_business_list(self.data.filter_business_list(text)))
        self.search_page.favorite_business.connect(data_handler.toggle_favorite_business)

        self.favorites_page.show_business_details.connect(self.open_business_page)
        self.favorites_page.favorite_business.connect(data_handler.toggle_favorite_business)

        self.business_page.favorite_button.click_signal.connect(lambda: self.data.toggle_favorite_business(self.business_page.favorite_button.business))

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.pages)

        # Sidebar behavior
        self.sidebar.button_selected.connect(self.sidebar_button_selected)

        # Load stylesheet
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf8") as f:
                self.setStyleSheet(f.read())

    #  Event handlers
    def sidebar_button_selected(self, index: int):
        # Switch page if button is home, businesses, favorites, or about
        if index >= 0 and index <= 3:
            self.pages.setCurrentIndex(index)
        
        # Update businesses in search page
        if index == 1:
            self.search_page.populate_business_list(self.data.filter_business_list(""))

        if index == 2:
            self.favorites_page.populate_business_list(self.data.get_favorite_businesses())

        # Exit button
        if index == 4:
            self.close()

    def open_business_page(self, biz: Business) -> None:

        self.business_page.set_business(biz)
        self.pages.setCurrentIndex(4)