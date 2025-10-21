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
)

from typing import List, Optional

from data.data_handler import BusinessRecord
from ui.business_ui import ListedBusiness, FavoriteButton

class HomePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignCenter)

        # Text
        title = QLabel("LocalLink - A local business supporting app")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Discover and support your local businesses!")
        subtitle.setObjectName("subtitleLabel")
        self.layout.addWidget(title)
        self.layout.addWidget(subtitle)


def populate_business_list(container_layout, businesses: Optional[List[BusinessRecord]]) -> None:
    # utility used by SearchPage and FavoritesPage
    while container_layout.count():
        it = container_layout.takeAt(0)
        w = it.widget()
        if w:
            w.setParent(None)
    if not businesses:
        return
    for biz in businesses:
        item = ListedBusiness(biz)
        container_layout.addWidget(item)
        # caller will wire signals
    container_layout.addStretch()

class SearchPage(QWidget):
    # Signals
    show_business_details = Signal(BusinessRecord)
    favorite_business = Signal(BusinessRecord)
    search_bar_updated = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(8)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search businesses by name or category...")
        self.search_bar.textChanged.connect(self.search_bar_updated.emit)
        self.layout.addWidget(self.search_bar)

        # Business List
        # This is being switched to a scroll box. If there are performance issues, consider using QListView

        self.business_list = QScrollArea(); self.layout.addWidget(self.business_list)
        business_container = QWidget(); self.business_container_layout = QVBoxLayout(); business_container.setLayout(self.business_container_layout)
        self.business_list.setWidgetResizable(True); self.business_list.setWidget(business_container)

    def populate_business_list(self, businesses: Optional[List[BusinessRecord]]) -> None:
        populate_business_list(self.business_container_layout, businesses)
        # wire signals for the new items
        for i in range(self.business_container_layout.count()):
            it = self.business_container_layout.itemAt(i)
            if not it:
                continue
            w = it.widget()
            if isinstance(w, ListedBusiness):
                w.main_button_clicked.connect(self.show_business_details.emit)
                w.favorite_button_clicked.connect(self.favorite_business.emit)


class FavoritesPage(QWidget):

    show_business_details = Signal(BusinessRecord)
    favorite_business = Signal(BusinessRecord)

    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(); self.setLayout(self.layout)
        label = QLabel("Favorites"); label.setObjectName("sectionLabel"); self.layout.addWidget(label)
        info = QLabel("Your saved businesses will appear here."); info.setWordWrap(True); self.layout.addWidget(info)
        self.business_list = QScrollArea(); self.layout.addWidget(self.business_list)
        business_container = QWidget(); self.business_container_layout = QVBoxLayout(); business_container.setLayout(self.business_container_layout)
        self.business_list.setWidgetResizable(True); self.business_list.setWidget(business_container)

    def populate_business_list(self, businesses: Optional[List[BusinessRecord]]) -> None:
        populate_business_list(self.business_container_layout, businesses)
        for i in range(self.business_container_layout.count()):
            it = self.business_container_layout.itemAt(i)
            if not it:
                continue
            w = it.widget()
            if isinstance(w, ListedBusiness):
                w.main_button_clicked.connect(self.show_business_details.emit)
                w.favorite_button_clicked.connect(self.favorite_business.emit)


class AboutPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Text
        label = QLabel("About")
        label.setObjectName("sectionLabel")
        self.layout.addWidget(label)
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


class BusinessPage(QWidget):
    def __init__(self) -> None:
        super().__init__()

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

        # Title
        self.name_label = QLabel("Business")
        self.name_label.setObjectName("sectionLabel")
        title_container_layout.addWidget(self.name_label)

        title_container_layout.addStretch()
        # Favorite Button
        self.favorite_button = FavoriteButton(self.business, "large")
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

    def set_business(self, biz: BusinessRecord):
        self.business = biz
        self.favorite_button.set_business(biz)
        # the caller (main window) should set the visual star state after this
        self.name_label.setText(biz.name)
        self.populate_business_reviews(biz)

    def populate_business_reviews(self, biz):
        # Populate the reviews list widget with the business's reviews
        self.review_list_widget.clear()
        for review in biz.reviews:
            item_text = f"{review['user']} (⭐ {review['rating']}) - {review['text']}"
            item = QListWidgetItem(item_text)
            self.review_list_widget.addItem(item)