"""
This is the business UI module for LocalLink.

This module contains various UI components related to displaying businesses, such as business cards, lists, and details.
This handles the visual representation and interaction logic for businesses within the application.

This module is the core of the business browsing experience in LocalLink.
"""

# imports for business UI components
from PySide6.QtCore import Qt, Signal, QPoint, QTimer
from PySide6.QtWidgets import (
    QPushButton,
    QHBoxLayout,
    QLabel,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QCheckBox,
    QFrame,
    QSizePolicy,
    QMessageBox,
)
from PySide6.QtGui import QPixmap, QCursor
from data.data_handler import (
    Business,
    DataHandler,
    Review,
)

from typing import List, Callable

class FavoriteButton(QPushButton):
    # star button used to add/remove favorites

    click_signal = Signal()

    def __init__(self, data: DataHandler, biz: Business, size: str = "small") -> None:
        super().__init__()
        self.data = data
        self.business = biz
        self.clicked.connect(self._on_click)
        self.setObjectName("favButtonSmall" if size == "small" else "favButtonLarge")
        self._refresh()

    def _on_click(self) -> None:
        """
        Toggle the favorite state of this business. When removing a
        favorite, optionally ask for confirmation based on the user's
        preferences. After toggling, emit a signal so listeners can
        refresh themselves and update this button's appearance.
        """
        if not (self.business and self.data):
            return
        # If removing a favorite and confirmations are enabled, ask the user
        if self.data.is_favorite(self.business):
            confirm_pref = (self.data.get_preference("confirm_delete", "yes") or "yes").lower()
            if confirm_pref == "yes":
                msg = QMessageBox(self)
                msg.setWindowTitle("Remove Favorite?")
                msg.setText(f"Are you sure you want to remove {self.business.name} from favorites?")
                # Load and scale the banner as a thumbnail if possible
                try:
                    pix = QPixmap(self.business.banner)
                    if not pix.isNull():
                        thumb = pix.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        msg.setIconPixmap(thumb)
                except Exception:
                    pass
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                if msg.exec() != QMessageBox.Yes:
                    return
        # Toggle the favorite status
        self.data.toggle_favorite(self.business)
        # Notify listeners and update UI
        self.click_signal.emit()
        self._refresh()

    def _refresh(self) -> None:
        # Update UI based on business state
        if self.business and self.data:
            if self.data.is_favorite(self.business):
                self.setText("★")
                self.setStyleSheet("color: #49B3FF;")
                return
        self.setText("☆")
        # Choose outline color based on theme preference
        theme = "dark"
        try:
            theme = (self.data.get_preference("theme", "dark") or "dark").lower()
        except Exception:
            theme = "dark"
        if theme == "light":
            # black outline on light theme
            self.setStyleSheet("color: #000000;")
        else:
            self.setStyleSheet("color: #ffffff;")
    
    def set_business(self, biz: Business) -> None:
        self.business = biz
        self._refresh()

    def enterEvent(self, event):
        # Highlight on mouse hover
        self.setText("★")
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Refresh on mouse leave
        self._refresh()
        super().leaveEvent(event)


class BusinessReviewInfo(QWidget):
    def __init__(self, biz: Business, size: int):
        super().__init__()

    # layout
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
        # Sets the business and updates UI
        if not biz:
            return
        rounded_rating = round(biz.rating)
        self.rating_text.setText(f"{'★' * rounded_rating + '☆' * (5 - rounded_rating)}")
        self.rating_number.setText(f"{round(biz.rating, 1)}")
        self.num_reviews.setText(f"({len(biz.reviews)} {'review' if len(biz.reviews) == 1 else 'reviews'})")


class ListedBusiness(QPushButton):
    # one clickable business row used in lists
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

        # Favorite Button
        self.favorite_button = FavoriteButton(data, biz, "small")
        layout.addWidget(self.favorite_button)
        self.favorite_button.setVisible(False)
        self.clicked.connect(lambda: self.main_button_signal.emit(self.business))

    def enterEvent(self, event):
        # Show favorite button on hover
        self.favorite_button.setVisible(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        # Hide favorite button when mouse leaves
        self.favorite_button.setVisible(False)
        super().leaveEvent(event)


class BusinessList(QWidget):
    # widget that shows a vertical list of businesses

    # To be called for wiring purposes, etc.
    business_added_signal = Signal(ListedBusiness)

    def __init__(self, data: DataHandler) -> None:
        super().__init__()

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Data
        self.data = data

    def _clear_list(self) -> None:
        # Removes all elements from the list
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
    
    def _add_business_to_list(self, biz: Business) -> None:
        # Adds an element to the list
        item = ListedBusiness(self.data, biz)
        self.layout.addWidget(item)
        self.business_added_signal.emit(item)

    def populate(self, query: str, sort_key: str, reverse_sort: bool, filter_keys: List[str], onlyFavs: bool) -> None:
        # Repopulates the list with businesses
        self._clear_list()

        filtered = self.data.filter_businesses(query, sort_key, reverse_sort, filter_keys, onlyFavs)

        for biz in filtered:
            self._add_business_to_list(biz)

        self.layout.addStretch()


class ReviewItem(QWidget):
    """One review card. Shows username, stars, review text, toggle Read more/Show less, optional Remove."""

    MAX_LINES = 5

    def __init__(
        self,
        review: Review,
        data: DataHandler,
        biz: Business,
        refresh_callback: Callable[[], None],
    ) -> None:
        super().__init__()
        self.review = review
        self.data = data
        self.business = biz
        self.refresh_callback = refresh_callback

        self._expanded = False
        self._full_height = 0
        self._clipped_height = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(10)

        # --- Top row (username) ---
        top_row = QHBoxLayout()
        user_label = QLabel(review.user)
        user_label.setStyleSheet("font-weight: bold;")
        top_row.addWidget(user_label)
        top_row.addStretch()
        layout.addLayout(top_row)

        # --- Stars ---
        stars = "★" * review.rating + "☆" * (5 - review.rating)
        rating_label = QLabel(stars)
        rating_label.setStyleSheet("color: #f1c40f")
        layout.addWidget(rating_label)

        # --- Review text ---
        self.review_label = QLabel(review.text)
        self.review_label.setWordWrap(True)
        self.review_label.setMaximumWidth(1000) # to ensure consistent wrapping
        layout.addWidget(self.review_label)

        # --- Toggle button (Read more / Show less) ---
        self.toggle_btn = QPushButton("Read more")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet(
            "color: #888888; background: transparent; border: none; text-decoration: underline;"
        )
        self.toggle_btn.setVisible(False)
        self.toggle_btn.clicked.connect(self._toggle_expand)
        layout.addWidget(self.toggle_btn, alignment=Qt.AlignLeft)

        # --- Remove button (only for user-created reviews) ---
        if getattr(review, "user_created", False):
            remove_row = QHBoxLayout()
            remove_row.addStretch()

            remove_btn = QPushButton("Remove")
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet(
                "color: #ff6b6b; background: transparent; border: none; font-weight: bold;"
            )
            remove_btn.setFixedWidth(100)
            remove_btn.clicked.connect(self._on_remove_clicked)

            remove_row.addWidget(remove_btn)
            layout.addLayout(remove_row)

        # After layout has a real width, clamp to MAX_LINES if needed
        QTimer.singleShot(0, self._recalc_heights_and_apply)

    def _measure_heights(self) -> tuple[int, int]:
        text = self.review_label.text()
        fm = self.review_label.fontMetrics()
        width = max(500, self.review_label.width())

        full_h = fm.boundingRect(0, 0, width, 10_000, Qt.TextWordWrap, text).height()
        clipped_h = fm.lineSpacing() * self.MAX_LINES
        return full_h, clipped_h

    def _recalc_heights_and_apply(self) -> None:
        self._full_height, self._clipped_height = self._measure_heights()

        if self._full_height > self._clipped_height:
            # Long review → clamp unless expanded
            self.toggle_btn.setVisible(True)
            if self._expanded:
                self.review_label.setFixedHeight(self._full_height)
                self.toggle_btn.setText("Show less")
            else:
                self.review_label.setFixedHeight(self._clipped_height)
                self.toggle_btn.setText("Read more")
        else:
            # Short review → just fit, no toggle
            self.toggle_btn.setVisible(False)
            self._expanded = False
            self.review_label.setFixedHeight(self._full_height)

    def _toggle_expand(self) -> None:
        self._expanded = not self._expanded
        self._recalc_heights_and_apply()

    def _on_remove_clicked(self) -> None:
        msg = QMessageBox(self)
        msg.setWindowTitle("Remove Review")
        msg.setText("Are you sure you want to remove your review?")
        msg.setIcon(QMessageBox.NoIcon)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        if msg.exec() != QMessageBox.Yes:
            return

        try:
            self.data.remove_review(self.business, self.review)
        except Exception:
            pass

        try:
            self.refresh_callback()
        except Exception:
            pass


class ReviewList(QWidget):
    """Vertical list of reviews for a business."""
    reviews_changed = Signal(Business)

    def __init__(self, biz: Business, data: DataHandler) -> None:
        super().__init__()
        self.business = biz
        self.data = data

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

    def populate(self) -> None:
        # clear
        while self.layout.count():
            item = self.layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        # add items
        for review in (self.business.reviews or []):
            self.layout.addWidget(
                ReviewItem(review, self.data, self.business, self.populate)
            )

        self.layout.addStretch()

        try:
            self.reviews_changed.emit(self.business)
        except Exception:
            pass

class BusinessSortMenu(QFrame):
    # Popup menu for sorting and filtering businesses. Contains sort buttons and category filter checkboxes.
    property_changed_signal = Signal()
    menu_closed = Signal()

    def __init__(self, data: DataHandler, sort_key: str, reverse_sort: bool, filter_keys: List[str]) -> None:
        super().__init__()

        # Style and info
        self.setWindowFlags(Qt.Popup)
        self.setMinimumWidth(200)
        self.setStyleSheet("background-color: #282a36; color: #f8f8f2; font-family: 'Helvetica Neue', 'Arial', Helvetica; font-size: 14px;")

        # Data
        self.data = data
        self.sort_key = sort_key
        self.reverse_sort = reverse_sort
        self.filter_keys = set(filter_keys)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.layout = layout

        # Sort Title
        sort_text = QLabel("Sort by:")
        layout.addWidget(sort_text)

        # Sort buttons
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

    # sort_button_label generates the text for a sort button based on current state
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
        # Updates the text on sort buttons
        for key, btn in self.sort_buttons.items():
            btn.setText(self.sort_button_label(key))
    
    def sort_button_pushed(self, key: str):
        # Emits a signal and updates sort button text when pushed
        if self.sort_key == key:
            self.reverse_sort = not self.reverse_sort
        else:
            self.sort_key = key
            # Default direction: descending for numeric sorts, ascending for name
            self.reverse_sort = key != "name"

        self.update_sort_button_texts()
        self.property_changed_signal.emit()

    def checkbox_toggled(self, category: str, state: int):
        # Update filter when checkbox is toggled
        if state:
            self.filter_keys.add(category)
        else:
            self.filter_keys.discard(category)
        self.property_changed_signal.emit()

    # for when the sort menu is closed (either by clicking outside or programmatically), 
    # emit a signal so the parent can update its state
    def hideEvent(self, event):
        super().hideEvent(event)
        self.menu_closed.emit()


class SearchAndSort(QWidget):
    # Search bar, sort button, and filter menu for the business list page. Emits a signal when 
    # any property changes so the business list can update.
    sort_changed_signal = Signal()

    def __init__(self, data: DataHandler) -> None:
        super().__init__()

        # Data
        self.data = data

        # Choose default sort settings. Default to sorting by ratings.
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
        self.menu = BusinessSortMenu(self.data, self.sort_key, self.reverse_sort, self.filter_keys)
        self.menu.property_changed_signal.connect(self._sort_changed)
        self.menu.menu_closed.connect(self._menu_closed)
        self.sortMenuVisible = False
    
    def show_sort_menu(self) -> None:
        # Toggle the visibility of the sort menu. When showing, position it below the sort button.

        # the popup already closes when we click anywhere, so we dont even bother hiding the menu
        if self.sortMenuVisible:
            self.sortMenuVisible = False
            return

        self.menu.adjustSize()  # Ensure size is calculated

        # Position the menu relative to the sort button.  We move the menu
        # so its right edge aligns with the right edge of the sort
        # button.  Using mapToGlobal converts local coordinates to
        # global screen coordinates.  The vertical position is set just
        # below the button.
        # The offset of 0 ensures the menu width is used dynamically.
        pos = self.sort_button.mapToGlobal(
            QPoint(self.sort_button.width() - self.menu.width(), self.sort_button.height())
        )
        #move menu and show it
        self.menu.move(pos)
        self.menu.show()
        self.sortMenuVisible = True

    def _menu_closed(self):
        #check if menu was closed by clicking the sort button (in which case we want to keep track of it and not reopen), 
        # or by clicking outside (in which case we want to update the state and allow reopening)
        if not self.is_mouse_over_sort_button():
            self.sortMenuVisible = False

    def _sort_changed(self) -> None:
        # Update sort when changed
        if not self.menu:
            return

        self.sort_key = self.menu.sort_key
        self.reverse_sort = self.menu.reverse_sort
        self.filter_keys = self.menu.filter_keys

        self.sort_changed_signal.emit()

    # this function checks if the mouse is currently hovering over the sort button. Since the sort menu is a popup, it closes regardless
    # of where we click (not in the popup itself), even on the sort button. 
    # This function is used to prevent the menu from reopening immediately after closing when we click the sort button.
    def is_mouse_over_sort_button(self):
        global_pos = QCursor.pos()  # mouse in global coords
        local_pos = self.sort_button.mapFromGlobal(global_pos)
        return self.sort_button.rect().contains(local_pos)

    def resizeEvent(self, event):
        """
        Reposition the sort menu if it is visible when the parent widget
        is resized.  Without this, the popup menu will remain at its
        previous screen coordinate even if the sort button moves (for
        example, when the window is maximized or restored).  This
        override ensures the menu always remains anchored to the sort
        button’s current location.
        """
        super().resizeEvent(event)
        try:
            if self.menu and self.menu.isVisible():
                # Ensure the menu's size is up-to-date before computing
                # its position
                self.menu.adjustSize()
                new_pos = self.sort_button.mapToGlobal(
                    QPoint(self.sort_button.width() - self.menu.width(), self.sort_button.height())
                )
                self.menu.move(new_pos)
        except Exception:
            # If anything goes wrong during repositioning, just ignore
            pass

class BannerLabel(QLabel):
    def __init__(self, fixed_height=200, parent=None):
        super().__init__(parent)

        # Scale correctly
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
        # Scale to width while keeping aspect ratio, then crop vertically.

        w = self.width()
        h = self.fixed_height

        scaled = self.original_pixmap.scaledToWidth(
            w, Qt.SmoothTransformation
        )

        if scaled.height() > h:
            y = (scaled.height() - h) // 2
            scaled = scaled.copy(0, y, w, h)

        return scaled
    
