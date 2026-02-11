"""
This is the pages module for LocalLink.

This is the largest portion of our code, as it includes all of the major UI components for the pages.

This module contains the various page classes used in the LocalLink application, 
including HomePage, SearchPage, FavoritesPage, BusinessPage, StatsPage, and HelpPage.
"""

# all imports used in this module
import sys
import re
import matplotlib

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
    QMessageBox
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

# imports for the matplotlib charts in the statistics page
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MultipleLocator
matplotlib.use("Agg")  # prevents backend conflicts

# custom figure canvas that lets parent scroll areas get wheel events
class ScrollAwareFigureCanvas(FigureCanvas):
    def wheelEvent(self, event):
        # we don't consume the wheel event, we let it propagate to parent scroll area
        event.ignore()

# class page for all pages to inherit from
class Page(QWidget):
    def __init__(self, data: DataHandler) -> None:
        super().__init__()
        self.data = data
    
    def page_shown(self, data = None) -> None:
        pass

# class for the stats page. this shows charts and recommended businesses based on favorites
class StatsPage(Page):
    show_business_details = Signal(Business)

    # initializing function
    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(16)

        title = QLabel("Statistics & Recommendations")
        title.setObjectName("sectionLabel")
        self.layout.addWidget(title)

        # create a container for the canvas to better manage sizing
        self.canvas_container = QWidget()
        self.canvas_layout = QVBoxLayout(self.canvas_container)
        self.canvas_layout.setContentsMargins(0, 0, 0, 0)
            
        # create the matplotlib figure and canvas, and add the canvas to the container
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.canvas = ScrollAwareFigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas_layout.addWidget(self.canvas)
        
        # set size policy and minimum height on the container to ensure it expands properly and has enough space for the charts
        self.canvas_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas_container.setMinimumHeight(400)
        self.layout.addWidget(self.canvas_container, 1)

        # recommended section
        self.recommend_label = QLabel("Recommended for you")
        self.recommend_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.layout.addWidget(self.recommend_label)

        # container for recommended businesses, which will be populated with ListedBusiness widgets
        self.recommend_container = QWidget()
        self.recommend_layout = QVBoxLayout(self.recommend_container)
        self.recommend_layout.setContentsMargins(0, 0, 0, 0)
        self.recommend_layout.setSpacing(8)
        self.layout.addWidget(self.recommend_container)

        #stretch at the bottom to push content up if there's extra space, 
        # and to ensure the layout looks good even if there are few 
        # recommendations or the charts are small
        self.layout.addStretch()

        # build charts and recs now
        self._update_stats()
        self._populate_recommendations()

    def page_shown(self, data=None) -> None:
        # rebuild charts and recommendations when the page appears
        super().page_shown(data)
        self._update_stats()
        self._populate_recommendations()
        
        # force layout recalculation and redraw
        if self.canvas:
            # trigger layout recalculation by updating geometry
            self.layout.invalidate()
            self.canvas.draw_idle()  # idempotent draw request

            # schedule a repaint for next event loop
            self.canvas.repaint()

    def _update_stats(self) -> None:
        # clear the previous chart so we can draw a fresh one
        self.figure.clear()

        # collect categories and metrics from the data handler. we need
        # both number of businesses and average rating for each category
        # to draw the chart
        categories = self.data.categories()
        counts: list[int] = [self.data.get_number_of_businesses_by_category(cat) for cat in categories]
        average_ratings: list[float] = [self.data.get_average_rating_by_category(cat) for cat in categories]

        # create axes; second axis shares same x axis but has its
        # own y axis for ratings so counts and ratings can be shown together
        count_axis = self.figure.add_subplot(111)
        rating_axis = count_axis.twinx()

        if not categories:
            # no data yet: display a friendly message
            count_axis.text(0.5, 0.5, "No data yet", ha="center", va="center",
                            transform=count_axis.transAxes)
            count_axis.set_axis_off()
            rating_axis.set_axis_off()
        else:
            # numeric x positions for each category
            x_positions = list(range(len(categories)))

            # width for each bar group
            bar_width = 0.4

            # draw counts on the left axis
            count_bars = count_axis.bar(
                [x - bar_width/2 for x in x_positions],
                counts,
                width=bar_width,
                label="Businesses"
            )

            # draw average ratings on the right axis in a different color
            rating_bars = rating_axis.bar(
                [x + bar_width/2 for x in x_positions],
                average_ratings,
                width=bar_width,
                color="#f1fa8c",
                label="Average Rating"
            )

            # set titles and labels
            count_axis.set_title("Businesses and Average Ratings by Category")
            count_axis.set_ylabel("Number of Businesses")
            rating_axis.set_ylabel("Average Rating (0–5)")

            # ensure ratings axis always shows full scale from 0 to 5
            rating_axis.set_ylim(0, 5)

            # ticks for x axis
            count_axis.xaxis.set_major_locator(MultipleLocator(1))
            count_axis.yaxis.set_major_locator(MultipleLocator(1))
            rating_axis.yaxis.set_major_locator(MultipleLocator(1))
            count_axis.set_xticks(x_positions)
            count_axis.set_xticklabels(categories, rotation=45, ha="right")

            # add legends to identify bars; one legend for each axis
            count_axis.legend(loc="upper left")
            rating_axis.legend(loc="upper right")

            # adjust bottom spacing so long category labels don't get cut off
            self.figure.subplots_adjust(bottom=0.25)

        # trigger the canvas to redraw with the new figure contents
        self.canvas.draw()

    def _clear_recommendations(self) -> None:
        # remove all widgets from the recommendations layout to prepare for new recommendations
        while self.recommend_layout.count():
            item = self.recommend_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def _populate_recommendations(self) -> None:
        # Build and show recommended businesses (clickable items).
        # clear any existing recommendation widgets

        self._clear_recommendations()

        # check user preference for showing recommendations. if set to no, show placeholder
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
            self.recommend_layout.addWidget(item)
            item.main_button_signal.connect(self.show_business_details.emit)

# help page with questions and answers that you can click to expand the answer
class HelpPage(Page):
    # Help / FAQ page with easy answers you can expand.

    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)

        # title label for the page
        title = QLabel("Help & FAQ")
        title.setObjectName("sectionLabel")
        self.layout.addWidget(title)

        # Define questions and answers (the first text is the title, 
        # the second text is the body that appears when you click the question)
        qa = [
            ("How do I search for businesses?",
             "To search for a business, navigate to the Search page and type a business name or category into the search bar."
             " You can sort by ratings, name, reviews, or deals using the sort button and filter by categories."
             " You can also scroll through the full list of businesses without searching."),

            ("How do I leave a review?",
             "To leave a review, you must click a business to go to its detail page, then click 'Leave a Review'. Provide your username, select a star rating,"
             " and describe your experience. To prevent bots, complete the CAPTCHA before submitting."),
             
            ("How do I favorite a business?",
             "To favorite a business, hover over a business listing and click the star icon on the right side. You can also click on the listing"
             " to see the business page with its details, and a star icon will appear near the top right, which you can click to add the business to your Favorites."
             " You can view all your saved businesses on the Favorites page."),

            ("How do I view statistics?",
             "Open the Stats page from the sidebar to see charts summarizing the businesses and their average ratings, and to receive"
             " personalized recommendations. You can disable recommendations in Settings if desired."),

            ("How does the recommendation system work?",
             "The system considers the categories of your favorite businesses and their ratings to suggest other"
             " businesses you might like. Top-rated businesses from similar categories appear in your recommendations."
             "If you have no favorites yet, the system recommends popular businesses from top categories."),

            ("How can I export data?",
             "To export data, go first to the settings page. Once there, two buttons at the bottom allow you to export all businesses, or just favorited businesses."
             " After clicking one of the export buttons, you will be prompted to save the data as a CSV file. "
             "The CSV file includes all business information, including names, categories, reviews, and deals."),

             ("What Settings can I change?",
              "In Settings, you can switch between light and dark themes, enable reduced motion for a calmer experience (disables the fade animation between pages), disable recommendations on the Stats page,"
              " and turn on or off confirmation prompts when removing favorites. Your preferences are saved and will persist the next time you use the app. Make sure you click the save button after you make a change so the settings are applied.")
        ]

        # We create a button and label for each question and answer pair.
        # The answer labels are initially hidden, and clicking the question button 
        # toggles the visibility of the corresponding answer.
        self.answer_widgets: List[QLabel] = []

        for question, answer in qa:
            q_btn = QPushButton(question)
            q_btn.setStyleSheet("text-align: left; font-weight: bold; border: none; color: #49B3FF; font-size: 16px; margin-bottom: 10px;")
            a_lbl = QLabel(answer)
            a_lbl.setWordWrap(True)
            a_lbl.setVisible(False)
            a_lbl.setStyleSheet("font-size: 14px")

            # Connect toggle (when its clicked)
            q_btn.clicked.connect(lambda checked=False, lbl=a_lbl: lbl.setVisible(not lbl.isVisible()))
            self.layout.addWidget(q_btn)
            self.layout.addWidget(a_lbl)
            self.answer_widgets.append(a_lbl)

        self.layout.addStretch()

# home page with welcome message and credits
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

        # Increase the title size to dominate the welcome screen. This is set through the QSS.
        title.setStyleSheet("font-size: 56px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Connect with your community's local businesses")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setStyleSheet("font-size: 26px; margin-top: 8px;")
        subtitle.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(subtitle)
        
        # stretch to push about text to the middle of the page
        self.layout.addStretch()

        # About Text (the \n creates a newline to separate the paragraphs, 
        # and the margins give it some breathing room)
        about = QLabel(
            "LocalLink is your friendly neighborhood companion. Use it to discover, review and support local businesses right where you live.\n\n"
            "Search and filter tons of listings, read honest reviews and keep a handy list of your favorites. The Stats page shows how many businesses and average ratings each category has, and even recommends new places you might like.\n\n"
            "For additional information, visit the Help page.\n\n"
            "Happy exploring!"
        )
        about.setWordWrap(True)
        about.setStyleSheet("font-size: 22px; margin-top: 16px; margin-bottom: 16px;")
        about.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(about)
        
        # stretch for pushing the credits and exit button to the bottom of the page, 
        # which looks better and is more intuitive for users
        self.layout.addStretch()

        # Credits Text
        credits = QLabel("Developed by Ever Otto, Avery Roelofsen, Guru Madana")
        credits.setWordWrap(True)
        credits.setStyleSheet("font-size: 21px; font-style: italic; font-weight: bold;")
        credits.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(credits)
        
        # This is for the Exit button. Setting the object name allows the QSS to apply the
        # primary button styles while our inline style increases the font size.
        exit_button = QPushButton("Exit")
        exit_button.setObjectName("primaryButton")
        exit_button.setStyleSheet("font-size: 18px; margin-top: 5px;")
        exit_button.clicked.connect(sys.exit)
        self.layout.addWidget(exit_button)

# search page with search bar, sort options, and business listings
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
    
    # When a business is added to the list, connect its signal to show details
    def _business_added_to_list(self, item: ListedBusiness) -> None:
        if item:
            item.main_button_signal.connect(self.show_business_details.emit)

    # Update the business list based on current search and sort settings
    def _sort_changed(self) -> None:
        query = self.search_and_sort.search_bar.text()
        # these are variables we use for the populate function, we get them from the 
        # search and sort widget so we can update the business list based on the current settings
        sort_key = self.search_and_sort.sort_key
        reverse_sort = self.search_and_sort.reverse_sort
        filter_keys = self.search_and_sort.filter_keys
        self.business_list.populate(query, sort_key, reverse_sort, filter_keys, False)
    
    # When the page is shown, refresh the business list
    def page_shown(self, data = None) -> None:
        super().page_shown()
        self._sort_changed()

# favorites page with business listings that the user has favorited, 
# which they can click to view details or unfavorite
class FavoritesPage(Page):
    # signals
    show_business_details = Signal(Business)
    favorite_business = Signal(Business)

    # initializer
    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)
        self.layout = QVBoxLayout(); self.setLayout(self.layout)
        # basic informative labels at the top of the page
        label = QLabel("Favorites"); label.setObjectName("sectionLabel"); self.layout.addWidget(label)
        info = QLabel("Your saved businesses will appear here."); info.setWordWrap(True); self.layout.addWidget(info)

        # Business List
        self.business_list = BusinessList(self.data)
        self.layout.addWidget(self.business_list)
        self.business_list.business_added_signal.connect(self._business_added_to_list)

        # we populate the business list with only favorited businesses, 
        # so we pass the appropriate parameters to the populate function
        self.business_list.populate("", "name", False, [], True)
    
    # When a business is added to the list, connect its signal to show details
    def _business_added_to_list(self, item: ListedBusiness) -> None:
        if item:
            item.main_button_signal.connect(self.show_business_details.emit)
            item.favorite_button.click_signal.connect(lambda: self.business_list.populate("", "name", False, [], True))
    
    # When the page is shown, refresh the business list
    def page_shown(self, data = None):
        super().page_shown()
        self.business_list.populate("", "name", False, [], True)


# business page with detailed information about a business, 
# reviews, and the option to leave a review
class BusinessPage(Page):
    # signals
    leave_review_clicked = Signal(Business)
    back_to_search = Signal()

    def __init__(self, data: DataHandler) -> None:
        super().__init__(data)

        # Business
        self.business = None
        
        # Layout
        self.layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.layout)

        # Exit Button
        self.backButton = QPushButton("←")
        self.backButton.setObjectName("exitButton")
        self.backButton.setFixedSize(60, 40)
        self.backButton.clicked.connect(lambda: self.back_to_search.emit())
        self.layout.addWidget(self.backButton)

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

        # Custom styles for the leave review button to make it look more like a link, 
        # since it's a less prominent action than the main buttons on the page
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
        
        # we connect the leave review button to emit the leave_review_clicked signal 
        # with the current business when clicked
        self.layout.addWidget(leave_review_button)
        leave_review_button.setCursor(Qt.PointingHandCursor)
        leave_review_button.clicked.connect(lambda: self.leave_review_clicked.emit(self.business))
        leave_review_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        leave_review_button.setFixedWidth(100)
        leave_review_button.adjustSize()

        # Review List
        self.review_list = ReviewList(self.business, self.data)

        # update review_info when the review list changes (add/remove)
        try:
            self.review_list.reviews_changed.connect(lambda biz: self.review_info.set_business(biz))
        except Exception:
            pass
        self.layout.addWidget(self.review_list)

    # When the page is shown, populate with business data
    def page_shown(self, data = None) -> None:
        if not data:
            return
        
        # we populate the page with the business data passed in, 
        # which includes setting all the labels, the banner, the reviews, 
        # and the favorite button
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

        # if there are deals, we show the deals banner and populate it with the deal information.
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

# this is the page for leaving a review on a business. 
# it includes a star rating system, text input for the review, 
# and a submit button. it also has validation to ensure the user enters a username, 
# selects a star rating, and writes a review within the character limit before submitting.
class ReviewPage(Page):

    # signals
    review_submitted_signal = Signal(Business)
    review_cancelled_signal = Signal(Business)

    # Constructor
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

        # run a loop to create 5 star buttons, which the user can click to set their rating.
        # (each star is invidiually made)
        for i in range(1, 6):
            btn = QPushButton("☆")
            btn.setObjectName("starButton")
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("font-size: 36px; color: #ffaa00; background: transparent; border: none;")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, rating=i: self._star_clicked(rating))
            stars_layout.addWidget(btn)
            self.star_buttons.append(btn)
            btn.setAutoFillBackground(False)

        # we add the widget then the stretch after the stars to push them to the left, 
        # which looks better and is more intuitive for users
        for btn in self.star_buttons:
            stars_layout.addWidget(btn)

        stars_layout.addStretch()
        self.layout.addWidget(stars_container)

        # User Line Edit
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Username")
        self.layout.addWidget(self.line_edit)

        # Text Edit
        self.review_text_edit = QTextEdit()
        self.review_text_edit.setPlaceholderText("Tell us your experience...")
        self.layout.addWidget(self.review_text_edit)

        # character counter (bottom-left) showing current / max chars
        self._max_review_chars = 500
        self.char_count_label = QLabel(f"0/{self._max_review_chars}")
        self.char_count_label.setStyleSheet("color: #aaaaaa; font-size: 18px;")

        # place counter into a small container together with buttons below
        # Buttons row: Counter (left), Back and Submit (right)
        buttons_row = QWidget()
        buttons_layout = QHBoxLayout(buttons_row)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # add the counter on the left
        buttons_layout.addWidget(self.char_count_label)
        buttons_layout.addStretch()

        self.back_button = QPushButton("Back")
        buttons_layout.addWidget(self.back_button)
        self.back_button.setCursor(Qt.PointingHandCursor)

        # Make the Back button visually match the Submit button
        self.back_button.setObjectName("primaryButton")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self._on_back_clicked)

        # Submit Button
        self.submit_button = QPushButton("Submit")
        self.submit_button.setObjectName("primaryButton")
        buttons_layout.addWidget(self.submit_button)
        self.submit_button.setFixedWidth(100)
        self.submit_button.clicked.connect(self.submit_review)

        self.layout.addWidget(buttons_row)

        # update the character counter whenever text changes
        self.review_text_edit.textChanged.connect(self._update_char_count)
        
        # initialize display
        self._update_char_count()

    # When the page is shown, populate with business data
    def page_shown(self, data = None):
        if not data:
            return
        
        biz: Business = data
        self.review_text_edit.clear()
        self.business = biz
        self.name_label.setText(f"Leaving a review on {biz.name}")
        self._star_clicked(0)
        self.line_edit.clear()

    # Star button clicked (this handles the star buttons)
    def _star_clicked(self, rating: int) -> None:
        self.rating = rating
        for i, btn in enumerate(self.star_buttons, start=1):
            if i <= rating:
                btn.setText("★")
            else:
                btn.setText("☆")

    def _update_char_count(self) -> None:
        # update the bottom-left character counter and change color when limit reached

        try:
            text = self.review_text_edit.toPlainText()

            # remove indentation at the start of each line (we dont want to include those as counted characters)
            no_indents = re.sub(r"(?m)^[ \t]+", "", text)

            # then remove line breaks
            clean = ( no_indents.replace("\r", "").replace("\n", "") )

            # get the length of the text then set the text
            length = len(clean)
            self.char_count_label.setText(f"{length}/{self._max_review_chars}")

            if length >= self._max_review_chars:
                # red when at or over the limit
                self.char_count_label.setStyleSheet("color: #ff6b6b; font-size: 18px;")
            else:
                self.char_count_label.setStyleSheet("color: #aaaaaa; font-size: 18px;")

        except Exception:
            # defensive: ignore if widgets not yet available
            pass

    def _send_final_review(self):
        # Create the review. The Review object itself carries a `user_created`
        # boolean so ownership is persisted with the review data.
        username = self.line_edit.text().strip()

        # Add the review and rely on Review.user_created to indicate ownership
        self.data.add_review(self.business, username, self.rating, self.review_text_edit.toPlainText().strip())

        # emit the business so the main window can refresh the business page
        self.review_submitted_signal.emit(self.business)

    def submit_review(self) -> None:
        # check normal form fields
        # Validate form fields and provide helpful error messages

        # rating needs to be between 1 and 5
        if not (1 <= self.rating <= 5):
            QMessageBox.warning(self, "Invalid Rating", "Please select a rating between 1 and 5 stars.")
            return
        
        # username is required and must be between 3 and 20 characters (after stripping whitespace)
        if not self.line_edit.text().strip():
            QMessageBox.warning(self, "Missing Username", "Please enter your username before submitting.")
            return
        
        # check the length of the username to ensure it's not too short or too long, 
        # which helps maintain a positive user experience and prevents potential 
        # issues with extremely long usernames in the UI or database
        if len(self.line_edit.text().strip()) < 3 or len(self.line_edit.text().strip()) > 20:
            QMessageBox.warning(self, "Invalid Username", "Username must be between 3-20 characters long.")
            return
        
        # review text is required and must not be just whitespace
        if not self.review_text_edit.toPlainText().strip():
            QMessageBox.warning(self, "Missing Review", "Please write a brief review of your experience.")
            return

        # check character limit and block submission if exceeded
        current_len = len(self.review_text_edit.toPlainText())
        if current_len > self._max_review_chars:
            QMessageBox.warning(self, "Exceeded max character count", "Exceeded max character count")
            return

        # open captcha window
        from ui.captcha_window import CaptchaWindow
        self.captcha = CaptchaWindow()

        # submit review when captcha succeeds
        self.captcha.captcha_passed.connect(self._send_final_review)
        
        # show the window
        self.captcha.show()

    def _on_back_clicked(self) -> None:
        # Tell the main window to go back to the business page if the user clicks back, 
        # and emit the business so it can refresh the business page if needed
        self.review_cancelled_signal.emit(self.business)