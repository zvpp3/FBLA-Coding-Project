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

from typing import List

from data.data_handler import Business
from ui.listed_business import ListedBusiness

class HomePage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignCenter)

        # Text
        title = QLabel("Byte-Sized Business Boost")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Discover and support your local businesses!")
        subtitle.setObjectName("subtitleLabel")
        self.layout.addWidget(title)
        self.layout.addWidget(subtitle)


class SearchPage(QWidget):
    # Signal
    show_business_details = Signal(Business)
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

        #self.list_view.itemClicked.connect(self.show_business_details) Not sure if this works, holding off

        self.business_list = QScrollArea()
        self.layout.addWidget(self.business_list)

        business_container = QWidget()
        self.business_container_layout = QVBoxLayout()
        business_container.setLayout(self.business_container_layout)
        #business_container.setWidgetResizable(True)
        #business_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        #business_container.setMinimumSize(500, 500)
        self.business_list.setWidgetResizable(True)

        self.business_list.setWidget(business_container)
        
    
    def populate_business_list(self, businesses: List[Business] = None) -> None:
        while self.business_container_layout.count():
            item = self.business_container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        for biz in businesses:
            item = ListedBusiness(biz)
            self.business_container_layout.addWidget(item)
            item.main_button.connect(self.show_business_details.emit)
        self.business_container_layout.addStretch()


class FavoritesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Placeholder Text
        label = QLabel("Favorites")
        label.setObjectName("sectionLabel")
        self.layout.addWidget(label)
        info = QLabel("Your saved businesses will appear here.")
        info.setWordWrap(True)
        self.layout.addWidget(info)

        self.layout.addStretch()


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
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Text
        self.name_label = QLabel("Business")
        self.name_label.setObjectName("sectionLabel")
        self.layout.addWidget(self.name_label)

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

    def display_business(self, biz: Business):
        self.name_label.setText(biz.name)
        #self.description.setText() Implement later
        self.populate_business_reviews(biz)

    def populate_business_reviews(self, biz):
        # Populate the reviews list widget with the business's reviews
        self.review_list_widget.clear()
        for review in biz.reviews:
            item_text = f"{review['user']} (⭐ {review['rating']}) - {review['text']}"
            item = QListWidgetItem(item_text)
            self.review_list_widget.addItem(item)