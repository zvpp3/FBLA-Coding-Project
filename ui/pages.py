from PySide6.QtCore import (
    Qt,
    Signal,
)
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QTextEdit,
)
from PySide6.QtGui import QPixmap

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
    ReviewList,
    SearchAndSort,
    BannerLabel,
    BusinessReviewInfo
)

class Page(QWidget):
    def __init__(self, data: DataHandler) -> None:
        super().__init__()
        self.data = data
    
    def page_shown(self, data = None) -> None:
        pass

class HomePage(Page):
    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        #self.layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("LocalLink")
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

        # Search and Sort
        self.search_and_sort: SearchAndSort = SearchAndSort(self.data)
        self.search_and_sort.search_bar.textChanged.connect(self._sort_changed)
        self.layout.addWidget(self.search_and_sort)
        self.search_and_sort.sort_changed_signal.connect(self._sort_changed)

        # Business List
        self.business_list = BusinessList(self.data)
        self.layout.addWidget(self.business_list)
        self.business_list.business_added_signal.connect(self._business_added_to_list)

        self._sort_changed()
    
    def _business_added_to_list(self, item: ListedBusiness) -> None:
        if item:
            item.main_button_signal.connect(self.show_business_details.emit)

    def _sort_changed(self) -> None:
        query = self.search_and_sort.search_bar.text()
        sort_key = self.search_and_sort.sort_key
        reverse_sort = self.search_and_sort.reverse_sort
        filter_keys = self.search_and_sort.filter_keys
        self.business_list.populate(query, sort_key, reverse_sort, filter_keys, False)
    
    def page_shown(self, data = None) -> None:
        super().page_shown()
        self._sort_changed()


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

        self.business_list.populate("", "name", False, [], True)
    
    def _business_added_to_list(self, item: ListedBusiness) -> None:
        if item:
            item.main_button_signal.connect(self.show_business_details.emit)
            item.favorite_button.click_signal.connect(lambda: self.business_list.populate("", "name", False, [], True))
    
    def page_shown(self, data = None):
        super().page_shown()
        self.business_list.populate("", "name", False, [], True)


class BusinessPage(Page):

    leave_review_clicked = Signal(Business)

    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)

        # Business
        self.business = None
        
        # Layout
        self.layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.layout)

        # Banner
        self.banner = BannerLabel(fixed_height=200)
        self.layout.addWidget(self.banner)

        # Title/Favorite Container
        title_container = QWidget()
        title_container_layout = QHBoxLayout()
        title_container.setLayout(title_container_layout)
        self.layout.addWidget(title_container)
        title_container_layout.setContentsMargins(0, 0, 0, 0)

        # Title Subtitle Container
        title_subtitle_container = QWidget()
        title_subtitle_container.setContentsMargins(0, 0, 0, 0)
        title_subtitle_layout = QVBoxLayout()
        title_subtitle_container.setLayout(title_subtitle_layout)
        title_subtitle_layout.setContentsMargins(0, 0, 0, 0)
        title_container_layout.addWidget(title_subtitle_container)

        title_container_layout.addStretch()

        # Title
        self.name_label = QLabel("Business")
        self.name_label.setObjectName("sectionLabel")
        title_subtitle_layout.addWidget(self.name_label)

        # Category
        self.category_label = QLabel("Category")
        self.category_label.setStyleSheet("color: #aaaaaa;")
        title_subtitle_layout.addWidget(self.category_label)

        # Favorite Button
        self.favorite_button = FavoriteButton(self.data, self.business, "large")
        title_container_layout.addWidget(self.favorite_button)

        # Deals Banner
        self.deals_banner = QWidget()
        self.deals_layout = QVBoxLayout(self.deals_banner)
        self.deals_banner.setStyleSheet("background-color: rgba(255, 126, 94, 0.5);")
        self.layout.addWidget(self.deals_banner)
        self.deals_title = QLabel("Deals")
        self.deals_title.setStyleSheet("background-color: transparent; font-weight: bold; font-size: 16px;")
        self.deals_layout.addWidget(self.deals_title)
        self.deals_text = QLabel()
        self.deals_text.setStyleSheet("background-color: transparent;")
        self.deals_layout.addWidget(self.deals_text)

        self.layout.addSpacing(10)

        # Description
        self.description = QLabel("Description")
        self.description.setWordWrap(True)
        self.description.setObjectName("sectionDescription")
        self.layout.addWidget(self.description)

        self.layout.addSpacing(16)

        # Reviews
        self.reviews_label = QLabel("Reviews")
        self.layout.addWidget(self.reviews_label)
        self.reviews_label.setStyleSheet("font-size: 20px;")

        # Review Info
        self.review_info = BusinessReviewInfo(self.business, 20)
        self.layout.addWidget(self.review_info)

        # Leave a Review
        leave_review_button = QPushButton("Leave a Review")
        leave_review_button.setStyleSheet("""
            QPushButton {
                color: #0077cc;
                background: transparent;
                border: none;
                text-decoration: none;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.layout.addWidget(leave_review_button)
        leave_review_button.setCursor(Qt.PointingHandCursor)
        leave_review_button.clicked.connect(lambda: self.leave_review_clicked.emit(self.business))
        leave_review_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        leave_review_button.setFixedWidth(100)
        leave_review_button.adjustSize()

        # Review List
        self.review_list = ReviewList(self.business)
        self.layout.addWidget(self.review_list)

    def page_shown(self, data = None) -> None:
        if not data:
            return
        biz: Business = data
        self.business = biz
        self.name_label.setText(biz.name)
        self.category_label.setText(biz.category)
        self.review_list.business = biz
        self.review_list.populate()
        self.favorite_button.set_business(biz)
        self.description.setText(biz.description)
        self.reviews_label.setText(f"Reviews")
        self.banner.setPixmap(QPixmap(biz.banner))
        self.review_info.set_business(biz)
        if len(biz.deals) > 0:
            self.deals_title.setText("Special deal" if len(biz.deals) == 1 else "Special deals")

            self.deals_banner.setVisible(True)
            deals_string = ""
            for deal in biz.deals:
                if deals_string == "":
                    deals_string += f"✦ {deal}"
                else:
                    deals_string = deals_string + "\n✦ " + deal
            self.deals_text.setText(deals_string)
        else:
            self.deals_banner.setVisible(False)


class ReviewPage(Page):

    review_submitted_signal = Signal()

    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)

        # Data
        self.business: Business = None
        self.rating = 0
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        self.name_label = QLabel(f"Leaving a review on ")
        self.name_label.setObjectName("sectionLabel")
        self.layout.addWidget(self.name_label)

        # Stars Picker
        stars_container = QWidget()
        stars_layout = QHBoxLayout(stars_container)
        self.star_buttons: List[QPushButton] = []
        for i in range(1, 6):
            btn = QPushButton("☆")
            btn.setObjectName("starButton")
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("font-size: 24px; color: #ffaa00; background: transparent; border: none;")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, rating=i: self._star_clicked(rating))
            stars_layout.addWidget(btn)
            self.star_buttons.append(btn)
            btn.setAutoFillBackground(False)
        for btn in self.star_buttons:
            stars_layout.addWidget(btn)
        stars_layout.addStretch()
        self.layout.addWidget(stars_container)

        # User Line Edit
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Username")
        self.layout.addWidget(self.line_edit)
        self.line_edit.textChanged.connect(self.update_submit_button_enabled)

        # Text Edit
        self.review_text_edit = QTextEdit()
        self.review_text_edit.setPlaceholderText("Tell us your experience...")
        self.layout.addWidget(self.review_text_edit)
        self.review_text_edit.textChanged.connect(self.update_submit_button_enabled)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setObjectName("primaryButton")
        self.layout.addWidget(self.submit_button)
        self.submit_button.setFixedWidth(100)
        self.submit_button.clicked.connect(self.submit_review)

    def page_shown(self, data = None):
        if not data:
            return
        biz: Business = data
        self.review_text_edit.clear()
        self.business = biz
        self.name_label.setText(f"Leaving a review on {biz.name}")
        self._star_clicked(0)
        self.line_edit.clear()

    def _star_clicked(self, rating: int) -> None:
        self.rating = rating
        for i, btn in enumerate(self.star_buttons, start=1):
            if i <= rating:
                btn.setText("★")
            else:
                btn.setText("☆")
        self.update_submit_button_enabled()

    def update_submit_button_enabled(self) -> None:
        self.submit_button.setEnabled(self.rating >= 1 and self.rating <= 5 and len(self.review_text_edit.toPlainText().strip()) > 0 and len(self.line_edit.text().strip()) > 0)

    def _send_final_review(self):
        self.data.add_review(
            self.business,
            self.line_edit.text().strip(),
            self.rating,
            self.review_text_edit.toPlainText().strip()
        )
        self.review_submitted_signal.emit()

    def submit_review(self) -> None:
        # check normal form fields
        if not (1 <= self.rating <= 5):
            return
        if not self.review_text_edit.toPlainText().strip():
            return
        if not self.line_edit.text().strip():
            return

        # open captcha window
        from ui.captcha_window import CaptchaWindow
        self.captcha = CaptchaWindow()

        # submit review when captcha succeeds
        self.captcha.captcha_passed.connect(self._send_final_review)
        
        # show the window
        self.captcha.show()
