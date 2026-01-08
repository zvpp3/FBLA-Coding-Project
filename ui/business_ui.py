from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QCheckBox,
    QFrame,
    QSizePolicy,
)
from PySide6.QtGui import QPixmap
from data.data_handler import (
    Business,
    DataHandler,
    Review,
)

from typing import List

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
        # When the star is clicked this function runs.  It asks for a
        # confirmation if we are about to remove a favourite and the
        # setting says we should.  Otherwise it just toggles the favourite
        # status and refreshes the button display.
        from PySide6.QtWidgets import QMessageBox
        if self.business and self.data:
            # check if this business is already favourited
            if self.data.is_favorite(self.business):
                # see if the user has turned on confirmations
                confirm_pref = self.data.get_preference("confirm_delete", "yes").lower()
                if confirm_pref == "yes":
                    # show a yes/no message box before removing
                    reply = QMessageBox.question(
                        self,
                        "Remove Favorite?",
                        f"Are you sure you want to remove {self.business.name} from favorites?",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                    if reply != QMessageBox.Yes:
                        return
            # toggle the status (add or remove) in the data handler
            self.data.toggle_favorite(self.business)
        # emit a signal so other widgets can update themselves and refresh our text
        self.click_signal.emit()
        self._refresh()

    def _refresh(self) -> None:
        if self.business and self.data:
            if self.data.is_favorite(self.business):
                self.setText("★")
                self.setStyleSheet("color: #49B3FF;")
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


class BusinessReviewInfo(QWidget):
    def __init__(self, biz: Business, size: int):
        super().__init__()

        self.setContentsMargins(0,0,0,0)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignLeft)

        # Rating Text
        self.rating_text = QLabel()
        self.rating_text.setStyleSheet(f"color: #f1c40f; font-size: {size}px")
        self.layout.addWidget(self.rating_text)

        # Rating Number
        self.rating_number = QLabel()
        self.layout.addWidget(self.rating_number)
        self.rating_number.setStyleSheet(f"font-size: {size}px;")

        # Num Reviews
        self.num_reviews = QLabel()
        self.num_reviews.setStyleSheet(f"color: #aaaaaa; font-size: {size}px")
        self.layout.addWidget(self.num_reviews)

        self.set_business(biz)

    def set_business(self, biz: Business):
        if not biz:
            return
        rounded_rating = round(biz.rating)
        self.rating_text.setText(f"{'★' * rounded_rating + '☆' * (5 - rounded_rating)}")
        self.rating_number.setText(f"{round(biz.rating, 1)}")
        self.num_reviews.setText(f"({len(biz.reviews)} {'review' if len(biz.reviews) == 1 else 'reviews'})")


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
                    background-color: rgba(255, 126, 94, 0.5);
                    padding: 0px 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)

        # Review Info
        review_info = BusinessReviewInfo(biz, 14)
        info_layout.addWidget(review_info, 0, Qt.AlignLeft)

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
        layout.setContentsMargins(0, 10, 0, 10)

        user_label = QLabel(f"{review.user}")
        layout.addWidget(user_label)
        # Include units on font-size for consistency
        user_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        rating_label = QLabel(f"{'★' * review.rating + '☆' * (5 - review.rating)}")
        rating_label.setStyleSheet("color: #f1c40f;")
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
        self.layout.setContentsMargins(0,0,0,0)

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
        self.setMinimumWidth(200)
        self.setStyleSheet("background-color: #282a36; color: #f8f8f2; font-family: 'Segoe UI', 'Arial', sans-serif; font-size: 14px;")

        # Data
        self.data = data
        self.sort_key = sort_key
        self.reverse_sort = reverse_sort
        self.filter_keys = set(filter_keys)

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

        self.checkboxes = {}

        # Category Criterion
        for category in data.categories():
            container = QWidget()
            h_layout = QHBoxLayout(container)
            layout.addWidget(container)

            check_box = QCheckBox()
            check_box.setChecked(category in self.filter_keys)
            self.checkboxes[category] = check_box
            check_box.stateChanged.connect(lambda state, cat=category: self.checkbox_toggled(cat, state))
            h_layout.addWidget(check_box)

            label = QLabel(f"{category} ({data.get_number_of_businesses_by_category(category)})")
            h_layout.addWidget(label)

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
        return f"{label_map.get(key, key.capitalize())} {arrow}"

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

    def checkbox_toggled(self, category: str, state: int):
        if state:
            self.filter_keys.add(category)
        else:
            self.filter_keys.discard(category)
        self.property_changed_signal.emit()


class SearchAndSort(QWidget):

    sort_changed_signal = Signal()

    def __init__(self, data: DataHandler) -> None:
        super().__init__()

        # Data
        self.data = data
        # Determine initial sort preferences based on user settings. If the
        # preference is absent, fall back to the previously hardcoded default
        # of "ratings". Reverse sort is True for numeric fields and False
        # for name (alphabetical ascending).
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
        self.menu.adjustSize()  # Ensure size is calculated
        pos = self.sort_button.mapToGlobal(QPoint(0, self.sort_button.height()))
        
        # Adjust position to keep menu on screen
        screen = QApplication.primaryScreen()
        screen_rect = screen.availableGeometry()
        menu_rect = self.menu.rect()
        menu_rect.moveTopLeft(pos)
        
        if pos.x() + menu_rect.width() > screen_rect.right():
            pos.setX(screen_rect.right() - menu_rect.width())
        if pos.y() + menu_rect.height() > screen_rect.bottom():
            pos.setY(pos.y() - menu_rect.height() - self.sort_button.height())
        if pos.x() < screen_rect.left():
            pos.setX(screen_rect.left())
        if pos.y() < screen_rect.top():
            pos.setY(screen_rect.top() + self.sort_button.height())
        
        self.menu.move(pos)
        self.menu.show()

    def _sort_changed(self) -> None:
        if not self.menu:
            return

        self.sort_key = self.menu.sort_key
        self.reverse_sort = self.menu.reverse_sort
        self.filter_keys = self.menu.filter_keys

        self.sort_changed_signal.emit()

class BannerLabel(QLabel):
    def __init__(self, fixed_height=200, parent=None):
        super().__init__(parent)
        self.fixed_height = fixed_height
        self.original_pixmap = None

        self.setFixedHeight(fixed_height)
        self.setScaledContents(False)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

    def setPixmap(self, pixmap: QPixmap):
        self.original_pixmap = pixmap
        super().setPixmap(self._scaled_pixmap())

    def resizeEvent(self, event):
        if self.original_pixmap:
            super().setPixmap(self._scaled_pixmap())
        super().resizeEvent(event)

    def _scaled_pixmap(self):
        """Scale to width while keeping aspect ratio, crop vertically."""
        w = self.width()
        h = self.fixed_height

        scaled = self.original_pixmap.scaledToWidth(
            w, Qt.SmoothTransformation
        )

        if scaled.height() > h:
            y = (scaled.height() - h) // 2
            scaled = scaled.copy(0, y, w, h)

        return scaled