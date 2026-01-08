import sys

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

from typing import List

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

# Optional imports for charts; these are used by StatsPage to display data analysis
try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
except Exception:
    Figure = None
    FigureCanvas = None

# Custom FigureCanvas that allows wheel events to propagate for scrolling
class ScrollAwareFigureCanvas(FigureCanvas):
    """A matplotlib canvas that allows parent scroll areas to handle wheel events."""
    def wheelEvent(self, event):
        # Don't consume the wheel event, let it propagate to parent scroll area
        event.ignore()

# Optional imports for statistics page
try:
    import matplotlib
    matplotlib.use("Agg")  # prevents backend conflicts
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

class Page(QWidget):
    def __init__(self, data: DataHandler) -> None:
        super().__init__()
        self.data = data
    
    def page_shown(self, data = None) -> None:
        pass


class StatsPage(Page):
    """
    A page that displays statistics about the businesses in the dataset and
    provides intelligent recommendations based on user favorites. It uses
    matplotlib to render charts within the PySide6 application. The page also
    exposes a signal to show business details when a recommended item is
    clicked.
    """
    show_business_details = Signal(Business)

    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(16)

        title = QLabel("Statistics & Recommendations")
        title.setObjectName("sectionLabel")
        self.layout.addWidget(title)

        # Chart canvas; may be None if matplotlib is not installed
        if Figure and FigureCanvas:
            # Create a container for the canvas to better manage sizing
            self.canvas_container = QWidget()
            self.canvas_layout = QVBoxLayout(self.canvas_container)
            self.canvas_layout.setContentsMargins(0, 0, 0, 0)
            
            self.figure = Figure(figsize=(10, 6), dpi=100)
            self.canvas = ScrollAwareFigureCanvas(self.figure)
            self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.canvas_layout.addWidget(self.canvas)
            
            self.canvas_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.canvas_container.setMinimumHeight(400)
            self.layout.addWidget(self.canvas_container, 1)
        else:
            placeholder = QLabel("Charts are unavailable (matplotlib missing).")
            placeholder.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(placeholder)
            self.figure = None
            self.canvas = None

        # Recommended section
        self.recommend_label = QLabel("Recommended for you")
        self.recommend_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.recommend_label)

        self.recommend_container = QWidget()
        self.recommend_layout = QVBoxLayout(self.recommend_container)
        self.recommend_layout.setContentsMargins(0, 0, 0, 0)
        self.recommend_layout.setSpacing(8)
        self.layout.addWidget(self.recommend_container)

        self.layout.addStretch()

        # Populate charts and recommendations initially
        self._update_stats()
        self._populate_recommendations()

    def page_shown(self, data=None) -> None:
        """Repopulate charts and recommendations when the page is shown."""
        super().page_shown(data)
        self._update_stats()
        self._populate_recommendations()
        
        # Force a complete layout recalculation and canvas redraw
        if self.canvas:
            # Trigger layout recalculation by updating geometry
            self.layout.invalidate()
            self.canvas.draw_idle()  # Idempotent draw request
            # Schedule a repaint for next event loop
            self.canvas.repaint()

    def _update_stats(self) -> None:
        if not MATPLOTLIB_AVAILABLE or self.figure is None:
            return

        # Clear the previous chart so we can draw a fresh one
        self.figure.clear()

        # Collect the categories and metrics from the data handler. We need
        # both the number of businesses and the average rating for each
        # category to draw a combined bar chart.
        categories = self.data.categories()
        counts: list[int] = [self.data.get_number_of_businesses_by_category(cat) for cat in categories]
        average_ratings: list[float] = [self.data.get_average_rating_by_category(cat) for cat in categories]

        # Create axes; the second axis shares the same x axis but has its
        # own y axis for the ratings. This allows us to display counts and
        # ratings side by side with different scales.
        count_axis = self.figure.add_subplot(111)
        rating_axis = count_axis.twinx()

        if not categories:
            # No data yet: display a friendly message
            count_axis.text(0.5, 0.5, "No data yet", ha="center", va="center",
                            transform=count_axis.transAxes)
            count_axis.set_axis_off()
            rating_axis.set_axis_off()
        else:
            # Numeric x positions for each category
            x_positions = list(range(len(categories)))
            # Width for each bar group
            bar_width = 0.4
            # Draw counts on the left axis
            count_bars = count_axis.bar(
                [x - bar_width/2 for x in x_positions],
                counts,
                width=bar_width,
                label="Businesses"
            )
            # Draw average ratings on the right axis in a different color
            rating_bars = rating_axis.bar(
                [x + bar_width/2 for x in x_positions],
                average_ratings,
                width=bar_width,
                color="#f1fa8c",
                label="Average Rating"
            )
            # Set titles and labels
            count_axis.set_title("Businesses and Average Ratings by Category")
            count_axis.set_ylabel("Number of Businesses")
            rating_axis.set_ylabel("Average Rating (0–5)")
            # Ensure ratings axis always shows full scale from 0 to 5
            rating_axis.set_ylim(0, 5)
            # Ticks for x axis
            from matplotlib.ticker import MultipleLocator
            count_axis.xaxis.set_major_locator(MultipleLocator(1))
            count_axis.yaxis.set_major_locator(MultipleLocator(1))
            rating_axis.yaxis.set_major_locator(MultipleLocator(1))
            count_axis.set_xticks(x_positions)
            count_axis.set_xticklabels(categories, rotation=45, ha="right")
            # Add legends to identify bars; one legend for each axis
            count_axis.legend(loc="upper left")
            rating_axis.legend(loc="upper right")
            # Adjust bottom spacing so long category labels don't get cut off
            self.figure.subplots_adjust(bottom=0.25)

        # Trigger the canvas to redraw with the new figure contents
        self.canvas.draw()

    def _clear_recommendations(self) -> None:
        while self.recommend_layout.count():
            item = self.recommend_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def _populate_recommendations(self) -> None:
        """
        Display a list of recommended businesses based on the user's favorites.
        Each item is clickable and emits a signal to show its detail page.
        """
        # Clear any existing recommendation widgets
        self._clear_recommendations()
        # Check the user's preference for showing recommendations. If the
        # preference has been set to "no", display a placeholder and exit.
        show_pref = self.data.get_preference("show_recommendations", "yes")
        if isinstance(show_pref, str) and show_pref.lower() == "no":
            placeholder = QLabel("Recommendations are disabled in settings.")
            placeholder.setStyleSheet("font-style: italic;")
            self.recommend_layout.addWidget(placeholder)
            return
        # Otherwise fetch recommendations and display them
        recommendations = self.data.recommend_businesses(3)
        for business in recommendations:
            item = ListedBusiness(self.data, business)
            # Show the favorite button on hover for recommended items
            item.favorite_button.setVisible(True)
            self.recommend_layout.addWidget(item)
            item.main_button_signal.connect(self.show_business_details.emit)


class HelpPage(Page):
    """
    A page that provides instructions and answers common questions about using
    the application. Each question can be expanded to reveal the answer.
    """

    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)

        title = QLabel("Help & FAQ")
        title.setObjectName("sectionLabel")
        self.layout.addWidget(title)

        # Define questions and answers
        qa = [
            ("How do I search for businesses?",
             "Navigate to the Search page and type a business name or category into the search bar."
             " You can also sort by ratings, name, reviews, or deals using the sort button and filter by categories."),
            ("How do I leave a review?",
             "From a business detail page, click 'Leave a Review'. Provide your username, select a star rating,"
             " and describe your experience. To prevent bots, complete the CAPTCHA before submitting."),
            ("How do I save favorites?",
             "Click the star icon on a business listing or its detail page to add it to your favorites."
             " View all your saved businesses on the Favorites page."),
            ("How do I view statistics?",
             "Open the Stats page from the sidebar to see charts summarizing the businesses and to receive"
             " personalized recommendations. You can disable recommendations in Settings if desired."),
            ("How does the recommendation system work?",
             "The system considers the categories of your favorite businesses and their ratings to suggest other"
             " businesses you might like. Top-rated businesses from similar categories appear in your recommendations."),
             ("How can I export data?",
             "You can export your favorite businesses and reviews to a CSV file via the Settings page."
             " Easily choose between exporting favorited business, or all business data."),
        ]

        self.answer_widgets: List[QLabel] = []

        for question, answer in qa:
            q_btn = QPushButton(question)
            q_btn.setStyleSheet("text-align: left; font-weight: bold; border: none; color: #49B3FF;")
            a_lbl = QLabel(answer)
            a_lbl.setWordWrap(True)
            a_lbl.setVisible(False)
            # Connect toggle
            q_btn.clicked.connect(lambda checked=False, lbl=a_lbl: lbl.setVisible(not lbl.isVisible()))
            self.layout.addWidget(q_btn)
            self.layout.addWidget(a_lbl)
            self.answer_widgets.append(a_lbl)

        self.layout.addStretch()

class HomePage(Page):
    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        
        # Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # Center items horizontally and provide generous top margin for a clean look
        self.layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # Title
        title = QLabel("LocalLink")
        title.setObjectName("titleLabel")
        # Increase the title size to dominate the welcome screen.  The colors
        # are still defined in the QSS, but we override the font size and
        # weight here to ensure the branding pops on both dark and light
        # themes.
        title.setStyleSheet("font-size: 56px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Connect with your community's local businesses")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setStyleSheet("font-size: 26px; margin-top: 8px;")
        subtitle.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(subtitle)

        # About Text
        about = QLabel(
            "LocalLink is your friendly neighborhood companion. Use it to discover, review and support local businesses right where you live.\n\n"
            "Search and filter thousands of listings, read honest reviews and keep a handy list of your favorites. The Stats page shows how many businesses and average ratings each category has, and even recommends new places you might like.\n\n"
            "In Settings you can switch themes, export your data to CSV, reduce motion for a calmer experience or require confirmations before removing favorites."
        )
        about.setWordWrap(True)
        about.setStyleSheet("font-size: 18px; margin-top: 16px; margin-bottom: 16px;")
        about.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(about)

        # Credits Text
        credits = QLabel("Developed by Ever Otto, Avery Roelofsen, Guru Madana")
        credits.setWordWrap(True)
        credits.setStyleSheet("font-size: 18px; font-style: italic;")
        credits.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(credits)

        # Exit button. Setting the object name allows the QSS to apply the
        # primary button styles while our inline style increases the font size.
        
        self.layout.addStretch()
        
        exit_button = QPushButton("Exit")
        exit_button.setObjectName("primaryButton")
        exit_button.setStyleSheet("font-size: 18px; margin-top: 24px;")
        exit_button.clicked.connect(sys.exit)
        self.layout.addWidget(exit_button)

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
        # Validate form fields and provide helpful error messages
        from PySide6.QtWidgets import QMessageBox
        if not (1 <= self.rating <= 5):
            QMessageBox.warning(self, "Invalid Rating", "Please select a rating between 1 and 5 stars.")
            return
        if not self.line_edit.text().strip():
            QMessageBox.warning(self, "Missing Username", "Please enter your username before submitting.")
            return
        if not self.review_text_edit.toPlainText().strip():
            QMessageBox.warning(self, "Missing Review", "Please write a brief review of your experience.")
            return

        # open captcha window
        from ui.captcha_window import CaptchaWindow
        self.captcha = CaptchaWindow()

        # submit review when captcha succeeds
        self.captcha.captcha_passed.connect(self._send_final_review)
        
        # show the window
        self.captcha.show()
