from PySide6.QtCore import (
    Qt,
    Signal,
)
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
    QSizePolicy,
    QLayout,
)

from dataclasses import dataclass
from typing import List, Optional

from data.data_handler import (
    Business,
    DataHandler,
)
from ui.business_ui import (
    ListedBusiness,
    FavoriteButton,
    BusinessList,
)

class Page(QWidget):
    def __init__(self, data: DataHandler) -> None:
        super().__init__()
        self.data = data
    
    def page_shown(self) -> None:
        pass

class HomePage(Page):
    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("LocalLink - An app to support local businesses")
        title.setObjectName("titleLabel")
        self.layout.addWidget(title)
        self.layout.addStretch()

        # Subtitle
        subtitle = QLabel("Discover and support your local businesses!")
        subtitle.setObjectName("subtitleLabel")
        self.layout.addWidget(subtitle)

        # About Text
        text = QLabel(
            "This application was developed by a high school team for the FBLA "
            "Coding & Programming event.\n\n"
            "Built with Python and PySide6, it demonstrates how modern design and "
            "clean code can be combined to create a useful tool for supporting "
            "local businesses."
        )
        text.setWordWrap(True)
        self.layout.addWidget(text)
        self.layout.addStretch()

        # Credits Text
        credits = QLabel("Developed by Ever Otto, Avery Roelofsen, Guru Madana")
        credits.setWordWrap(True)
        self.layout.addWidget(credits)


class SearchPage(Page):
    # Signals
    show_business_details = Signal(Business)

    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(8)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search businesses by name or category...")
        self.search_bar.textChanged.connect(self._search_bar_updated)
        self.layout.addWidget(self.search_bar)

        # Business List
        self.business_list = BusinessList(self.data)
        self.layout.addWidget(self.business_list)
        self.business_list.business_added_signal.connect(self._business_added_to_list)

        self.business_list.populate()
    
    def _business_added_to_list(self, item: ListedBusiness) -> None:
        if item:
            item.main_button_signal.connect(self.show_business_details.emit)

    def _search_bar_updated(self, text: str) -> None:
        self.business_list.populate(text)
    
    def page_shown(self) -> None:
        super().page_shown()
        self.business_list.populate()


class FavoritesPage(Page):

    show_business_details = Signal(Business)
    favorite_business = Signal(Business)

    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        self.layout = QVBoxLayout(); self.setLayout(self.layout)
        label = QLabel("Favorites"); label.setObjectName("sectionLabel"); self.layout.addWidget(label)
        info = QLabel("Your saved businesses will appear here."); info.setWordWrap(True); self.layout.addWidget(info)

        self.business_list = BusinessList(self.data)
        self.layout.addWidget(self.business_list)
        self.business_list.business_added_signal.connect(self._business_added_to_list)

        self.business_list.populate("", True)
    
    def _business_added_to_list(self, item: ListedBusiness) -> None:
        if item:
            item.main_button_signal.connect(self.show_business_details.emit)
            item.favorite_button.click_signal.connect(lambda: self.business_list.populate("", True))
    
    def page_shown(self):
        super().page_shown()
        self.business_list.populate("", True)


class BusinessPage(Page):
    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)

        # Business
        self.business = None
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title/Favorite Container
        title_container = QWidget()
        title_container_layout = QHBoxLayout()
        title_container.setLayout(title_container_layout)
        self.layout.addWidget(title_container)
        title_container_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        self.name_label = QLabel("Business")
        self.name_label.setObjectName("sectionLabel")
        title_container_layout.addWidget(self.name_label)

        title_container_layout.addStretch()
        # Favorite Button
        self.favorite_button = FavoriteButton(self.data, self.business, "large")
        title_container_layout.addWidget(self.favorite_button)

        # Description
        self.description = QLabel("Description")
        self.description.setWordWrap(True)
        self.description.setObjectName("sectionDescription")
        self.layout.addWidget(self.description)

        self.layout.addStretch()

        # Reviews
        reviews_label = QLabel("Reviews")
        self.layout.addWidget(reviews_label)
        self.review_list_widget = QListWidget()
        self.layout.addWidget(self.review_list_widget)

    def set_business(self, biz: Business) -> None:
        self.business = biz
        self.name_label.setText(biz.name)
        self.populate_business_reviews(biz)
        self.favorite_button.set_business(biz)
        self.description.setText(biz.description)

    def populate_business_reviews(self, biz: Business) -> None:
        # Populate the reviews list widget with the business's reviews
        self.review_list_widget.clear()
        for review in biz.reviews:
            item_text = f"{review['user']} (⭐ {review['rating']}) - {review['text']}"
            item = QListWidgetItem(item_text)
            self.review_list_widget.addItem(item)