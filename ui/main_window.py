
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
    BusinessRecord,
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

        # Wire signals
        self.search_page.show_business_details.connect(self.open_business_page)
        self.search_page.search_bar_updated.connect(lambda text: self.search_page.populate_business_list(self.data.search(text)))
        self.search_page.favorite_business.connect(self._on_toggle_from_list)

        self.favorites_page.show_business_details.connect(self.open_business_page)
        self.favorites_page.favorite_business.connect(self._on_toggle_from_list)

        # detail page favorite button toggles the current business
        self.business_page.favorite_button.click_signal.connect(lambda: self._toggle_favorite_detail())

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
            self.search_page.populate_business_list(self.data.list_businesses())

        if index == 2:
            self.favorites_page.populate_business_list(self.data.favorite_records())

        # Exit button
        if index == 4:
            self.close()

    def open_business_page(self, biz: BusinessRecord) -> None:
        # populate details and switch to the details page
        self.business_page.set_business(biz)
        # set the favorite button text according to current state
        if self.data.is_favorite(biz):
            self.business_page.favorite_button.setText("★ Favorited")
        else:
            self.business_page.favorite_button.setText("☆ Favorite business")
        self.pages.setCurrentIndex(4)

    # Helpers for toggles coming from lists
    def _on_toggle_from_list(self, biz: BusinessRecord) -> None:
        self.data.toggle_favorite(biz)
        # refresh the favorites page if open
        self.favorites_page.populate_business_list(self.data.favorite_records())

    def _toggle_favorite_detail(self) -> None:
        b = self.business_page.business
        if not b:
            return
        self.data.toggle_favorite(b)
        # update button text
        if self.data.is_favorite(b):
            self.business_page.favorite_button.setText("★ Favorited")
        else:
            self.business_page.favorite_button.setText("☆ Favorite business")
        self.favorites_page.populate_business_list(self.data.favorite_records())