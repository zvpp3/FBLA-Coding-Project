from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QCheckBox,
    QFrame,
    QSizePolicy,
)

from data.data_handler import (
    Business,
    DataHandler,
    Review,
)

from typing import Optional, List

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
        self.setFixedHeight(100)
        layout = QHBoxLayout(self)

        # Info Container
        info_container = QWidget()
        info_container.setContentsMargins(0,0,0,0)
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0,0,0,0)
        info_container.setLayout(info_layout)
        layout.addWidget(info_container)

        # Title Container
        title_container = QWidget()
        title_container.setContentsMargins(0,0,0,0)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0,0,0,0)
        title_container.setLayout(title_layout)
        title_layout.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(title_container, 0, Qt.AlignLeft)
        
        # Name
        item_text = QLabel(f"{biz.name}")
        title_layout.addWidget(item_text)
        item_text.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Deals
        if len(biz.deals):
            deals_label = QLabel(f"Deals: {len(biz.deals)}")
            title_layout.addWidget(deals_label)
            deals_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 131, 65, 0.5);
                    padding: 0px 8px;
                    font-size: 12px;
                }
            """)

        # Rating Container
        rating_container = QWidget()
        rating_container.setContentsMargins(0,0,0,0)
        rating_layout = QHBoxLayout()
        rating_layout.setContentsMargins(0,0,0,0)
        rating_container.setLayout(rating_layout)
        rating_layout.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(rating_container, 0, Qt.AlignLeft)

        # Rating Text
        rounded_rating = round(biz.rating)
        rating_text = QLabel(f"{'★' * rounded_rating + '☆' * (5 - rounded_rating)}")
        rating_text.setStyleSheet("color: #f1c40f;")
        rating_layout.addWidget(rating_text)

        # Rating Number
        rating_number = QLabel(f"{round(biz.rating, 1)}")
        rating_layout.addWidget(rating_number)

        # Num Reviews
        num_reviews = QLabel(f"({len(biz.reviews)} {'review' if len(biz.reviews) == 1 else 'reviews'})")
        num_reviews.setStyleSheet("color: #aaaaaa;")
        rating_layout.addWidget(num_reviews)

        # Category
        category_text = QLabel(f"{biz.category}")
        category_text.setStyleSheet("color: #aaaaaa;")
        info_layout.addWidget(category_text)
        
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


class BusinessList(QWidget):
    """ A way to list businesses, such as in search results or the favorites page 
    If this causes performance issues this can be changed to a QListView or similar"""

    # To be called for wiring purposes, etc.
    business_added_signal = Signal(ListedBusiness)

    def __init__(self, data: DataHandler) -> None:
        super().__init__()

        self.layout: QVBoxLayout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Data
        self.data = data

    def _clear_list(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
    
    def _add_business_to_list(self, biz: Business) -> None:
        item = ListedBusiness(self.data, biz)
        self.layout.addWidget(item)
        self.business_added_signal.emit(item)

    def populate(self, query: str, sort_key: str, reverse_sort: bool, filter_keys: List[str], onlyFavs: bool) -> None:
        self._clear_list()

        filtered = self.data.filter_businesses(query, sort_key, reverse_sort, filter_keys, onlyFavs)

        for biz in filtered:
            self._add_business_to_list(biz)

        self.layout.addStretch()


class ReviewItem(QWidget):
    """ The type of element to go inside ReviewLists (see below) """

    def __init__(self, review: Review) -> None:
        super().__init__()
        self.review = review
        layout = QVBoxLayout(self)

        user_label = QLabel(f"{review.user}")
        layout.addWidget(user_label)

        rating_date_container = QWidget()
        rating_date_layout = QHBoxLayout()
        rating_date_container.setLayout(rating_date_layout)

        rating_label = QLabel(f"{'★' * review.rating + '☆' * (5 - review.rating)}")
        rating_label.setStyleSheet("color: #f1c40f;")
        rating_date_layout.addWidget(rating_label)
        date_label = QLabel("Jan 1, 2025") # Date placeholder
        rating_date_layout.addWidget(date_label)

        #layout.addWidget(rating_date_container)
        layout.addWidget(rating_label)

        review_text = QLabel(review.text)
        review_text.setWordWrap(True)
        layout.addWidget(review_text)

class ReviewList(QWidget):
    """ A way to list reviews, such as in the business page
    If this causes performance issues this can be changed to a QListView or similar"""

    def __init__(self, biz: Business) -> None:
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Data
        self.business = biz

    def _clear_list(self) -> None:
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
    
    def _add_review_to_list(self, review: Review) -> None:
        item = ReviewItem(review)
        self.layout.addWidget(item)

    def populate(self) -> None:
        self._clear_list()

        reviews = self.business.reviews

        for review in reviews:
            self._add_review_to_list(review)

        self.layout.addStretch()

class BusinessSortMenu(QFrame):
    
    property_changed_signal = Signal()

    def __init__(self, data: DataHandler, sort_key: str, reverse_sort: bool, filter_keys: List[str]) -> None:
        super().__init__()
        self.setWindowFlags(Qt.Popup)

        # Data
        self.data = data
        self.sort_key = sort_key
        self.reverse_sort = reverse_sort
        self.filter_keys = filter_keys

        # Layout
        layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(layout)
        self.layout: QVBoxLayout = layout

        # Sort Title
        sort_text = QLabel("Sort by:")
        layout.addWidget(sort_text)

        self.sort_buttons = {
            "ratings": QPushButton("Ratings"),
            "name": QPushButton("Name"),
            "reviews": QPushButton("Reviews"),
            "deals": QPushButton("Deals"),
        }

        for key, btn in self.sort_buttons.items():
            layout.addWidget(btn)
            btn.clicked.connect(lambda _, k=key: self.sort_button_pushed(k))

        # Filter Title
        filter_text = QLabel("Filter by:")
        layout.addWidget(filter_text)

        # Category Criterion
        for category in data.categories():
            category_container = QWidget()
            category_layout = QHBoxLayout()
            category_container.setLayout(category_layout)
            layout.addWidget(category_container)

            check_box = QCheckBox()
            category_layout.addWidget(check_box)
            #check_box.clicked.connect(lambda: )

            # Category and number of businesses w/ that category
            text = QLabel(f"{category} ({data.get_number_of_businesses_by_category(category)})")
            category_layout.addWidget(text)

        self.update_sort_button_texts()

    def sort_button_label(self, key: str) -> str:
        if self.sort_key != key:
            return key.capitalize()
        arrow = "↓" if self.reverse_sort else "↑"
        label_map = {
            "ratings": "Ratings",
            "name": "Name",
            "reviews": "Reviews",
            "deals": "Deals",
        }
        return f"{label_map[key]} {arrow}"

    def update_sort_button_texts(self):
        for key, btn in self.sort_buttons.items():
            btn.setText(self.sort_button_label(key))

    def sort_key_and_order_to_string(self, key: str, reverse: bool):
        text = ""
        if key == "ratings":
            text += "Ratings | "
            text += "High → Low" if reverse else "Low → High"
        elif key == "name":
            text += "Name | "
            text += "Z → A" if reverse else "A → Z"
        elif key == "reviews":
            text += "Reviews | "
            text += "High → Low" if reverse else "Low → High"
        return text
    
    def sort_button_pushed(self, key: str):
        if self.sort_key == key:
            self.reverse_sort = not self.reverse_sort
        else:
            self.sort_key = key
            # Default direction: descending for numeric sorts, ascending for name
            self.reverse_sort = key != "name"

        self.update_sort_button_texts()
        self.property_changed_signal.emit()

    def check_box_clicked(self, filter_key: str, state: bool):
        if state:
            self.filter_keys.remove(filter_key)
        else:
            self.filter_keys.append(filter_key)
        self.property_changed_signal.emit()


class SearchAndSort(QWidget):

    sort_changed_signal = Signal()

    def __init__(self, data: DataHandler) -> None:
        super().__init__()

        # Data
        self.data = data
        self.sort_key = "ratings"
        self.reverse_sort = True
        self.filter_keys = []

        # Layout
        self.layout: QHBoxLayout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search businesses by name or category...")
        self.layout.addWidget(self.search_bar)

        # Sort Button
        self.sort_button = QPushButton("↑↓")
        self.sort_button.clicked.connect(self.show_sort_menu)
        self.layout.addWidget(self.sort_button)

        # Menu
        self.menu = None
    
    def show_sort_menu(self) -> None:
        self.menu = BusinessSortMenu(self.data, self.sort_key, self.reverse_sort, self.filter_keys)
        self.menu.property_changed_signal.connect(self._sort_changed)
        pos = self.sort_button.mapToGlobal(QPoint(0, self.sort_button.height()))
        self.menu.move(pos)
        self.menu.show()

    def _sort_changed(self) -> None:
        if not self.menu:
            return

        self.sort_key = self.menu.sort_key
        self.reverse_sort = self.menu.reverse_sort
        self.filter_keys = self.menu.filter_keys

        self.sort_changed_signal.emit()