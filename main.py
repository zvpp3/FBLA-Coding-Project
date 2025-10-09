"""
Byte‑Sized Business Boost – FBLA Coding & Programming template
================================================================

This module provides a starting point for the FBLA Coding & Programming
event.  The 2025‑2026 topic challenges competitors to build a tool that
helps users discover and support local businesses.  This initial
implementation uses PySide6 to build a modern, dark‑themed desktop
application similar to the "PyDracula" example.  The design includes a
navigation sidebar, a set of stacked pages, and simple business data
models.  Teams can extend this template by adding features such as
user authentication, persistent storage, reviews, and deal management.

To run this application locally install the ``pyside6`` package (for
example via ``pip install pyside6``) and execute this file with
``python main.py``.  See the accompanying ``README.md`` for more
details on development and deployment.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


@dataclass
class Business:
    """Simple data class representing a local business.

    Attributes:
        name: Human-friendly name of the business.
        category: Category such as ``Food``, ``Retail``, or ``Services``.
        rating: Average rating from user reviews on a 0-5 scale.
        reviews: List of text comments left by users.
        deals: Optional list of promotional messages or coupons.
    """

    name: str
    category: str
    rating: float = 0.0
    reviews: List[str] = field(default_factory=list)
    deals: List[str] = field(default_factory=list)


class BusinessDetailWindow(QWidget):
    """A simple window to display details of a single business."""

    def __init__(self, business: Business) -> None:
        super().__init__()
        self.business = business
        self.setWindowTitle(business.name)
        self.resize(420, 320)
        layout = QVBoxLayout(self)

        name_label = QLabel(f"<h2>{business.name}</h2>")
        category_label = QLabel(f"Category: <b>{business.category}</b>")
        rating_label = QLabel(f"Rating: <b>{business.rating:.1f}</b> ⭐")
        deals_label = QLabel(
            f"Deals: <b>{', '.join(business.deals) if business.deals else 'None'}</b>"
        )
        reviews_label = QLabel("Reviews:")
        reviews_text = QTextEdit("\n".join(business.reviews))
        reviews_text.setReadOnly(True)

        for widget in [name_label, category_label, rating_label, deals_label, reviews_label, reviews_text]:
            layout.addWidget(widget)


class MainWindow(QMainWindow):
    """The main application window containing navigation and pages."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Byte‑Sized Business Boost")
        self.resize(1000, 600)
        self._businesses: List[Business] = []

        self._init_ui()
        self._load_business_data()
        self._populate_business_list()

    def _init_ui(self) -> None:
        """Set up the main user interface widgets."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # --- Sidebar navigation ---
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setSpacing(8)
        sidebar_layout.setContentsMargins(12, 24, 12, 24)

        # Navigation buttons
        self.btn_home = QPushButton("Home")
        self.btn_home.setObjectName("navButton")
        self.btn_home.clicked.connect(lambda: self.pages.setCurrentIndex(0))

        self.btn_biz = QPushButton("Businesses")
        self.btn_biz.setObjectName("navButton")
        self.btn_biz.clicked.connect(lambda: self.pages.setCurrentIndex(1))

        self.btn_fav = QPushButton("Favorites")
        self.btn_fav.setObjectName("navButton")
        self.btn_fav.clicked.connect(lambda: self.pages.setCurrentIndex(2))

        self.btn_about = QPushButton("About")
        self.btn_about.setObjectName("navButton")
        self.btn_about.clicked.connect(lambda: self.pages.setCurrentIndex(3))

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setObjectName("navButton")
        self.btn_exit.clicked.connect(self.close)

        # Add buttons to sidebar
        for btn in [self.btn_home, self.btn_biz, self.btn_fav, self.btn_about, self.btn_exit]:
            btn.setMinimumHeight(36)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # --- Page container ---
        self.pages = QStackedWidget()
        self.pages.addWidget(self._create_home_page())
        self.pages.addWidget(self._create_business_page())
        self.pages.addWidget(self._create_favorites_page())
        self.pages.addWidget(self._create_about_page())
        self.pages.addWidget(self._create_business_details_page())

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.pages)

        # Load external stylesheet (dark theme)
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf8") as f:
                self.setStyleSheet(f.read())

    # ------------------------------------------------------------------
    #  Page definitions
    # ------------------------------------------------------------------
    def _create_home_page(self) -> QWidget:
        """Return the welcome page with a title and subtitle."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("Byte‑Sized Business Boost")
        title.setObjectName("titleLabel")
        subtitle = QLabel("Discover and support your local businesses!")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        return page

    def _create_business_page(self) -> QWidget:
        """Return the page listing businesses with search capability."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search businesses by name or category...")
        self.search_bar.textChanged.connect(self._filter_business_list)
        layout.addWidget(self.search_bar)

        # List view
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._show_business_detail)
        layout.addWidget(self.list_widget)
        return page

    def _create_favorites_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Favorites")
        label.setObjectName("sectionLabel")
        layout.addWidget(label)
        info = QLabel("Your saved businesses will appear here.")
        info.setWordWrap(True)
        layout.addWidget(info)
        layout.addStretch()
        return page

    def _create_about_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("About")
        label.setObjectName("sectionLabel")
        layout.addWidget(label)
        text = QLabel(
            "This application was developed by a high school team for the FBLA "
            "Coding & Programming event.\n\n"
            "Built with Python and PySide6, it demonstrates how modern design and "
            "clean code can be combined to create a useful tool for supporting "
            "local businesses."
        )
        text.setWordWrap(True)
        layout.addWidget(text)
        layout.addStretch()
        return page
    
    def _create_business_details_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Business")
        label.setObjectName("sectionLabel")
        layout.addWidget(label)
        text = QLabel("Description")
        text.setWordWrap(True)
        text.setObjectName("sectionDescription")
        layout.addWidget(text)
        layout.addStretch()
        return page
    

    # ------------------------------------------------------------------
    #  Data loading and filtering
    # ------------------------------------------------------------------
    def _load_business_data(self) -> None:
        """Load initial business data.

        For this prototype the data is hard-coded.  In a production
        solution you might read from a JSON file or database.  See the
        ``data.json`` file or implement an API integration to fetch real
        business data.  Each entry is converted into a ``Business``
        instance and stored on the ``_businesses`` list.
        """
        # Example dataset; extend or replace with real data
        self._businesses = [
            Business(
                name="Sunshine Café",
                category="Food",
                rating=4.5,
                reviews=["Great coffee and friendly service!"],
                deals=["10% off breakfast before 9 AM"],
            ),
            Business(
                name="Village Bookshop",
                category="Retail",
                rating=4.8,
                reviews=["Wide selection of books and cozy atmosphere."],
                deals=["Buy 2 get 1 free on used books"],
            ),
            Business(
                name="Paws & Claws Grooming",
                category="Services",
                rating=4.2,
                reviews=["My dog loves coming here!"],
                deals=["20% off for new customers"],
            ),
        ]

    def _populate_business_list(self, businesses: List[Business] | None = None) -> None:
        """Populate the list widget with business entries."""
        self.list_widget.clear()
        data = businesses if businesses is not None else self._businesses
        for biz in data:
            item_text = f"{biz.name} ({biz.category}) - ⭐ {biz.rating:.1f}"
            item = QListWidgetItem(item_text)
            # Store the underlying Business object for later retrieval
            item.setData(Qt.UserRole, biz)
            self.list_widget.addItem(item)

    def _filter_business_list(self, text: str) -> None:
        """Filter the business list based on a search query."""
        query = text.lower().strip()
        if not query:
            self._populate_business_list()
            return
        filtered = [
            biz
            for biz in self._businesses
            if query in biz.name.lower() or query in biz.category.lower()
        ]
        self._populate_business_list(filtered)

    # ------------------------------------------------------------------
    #  Event handlers
    # ------------------------------------------------------------------
    def _show_business_detail(self, item: QListWidgetItem) -> None:
        """Show a pop‑up window with details for the selected business."""
        biz: Business = item.data(Qt.UserRole)
        # detail_win = BusinessDetailWindow(biz)
        # # Use ``show`` instead of exec() to avoid blocking; see note below.
        # detail_win.show()
        self.pages.setCurrentIndex(4)
        page = self.pages.currentWidget()

        title_label = page.findChild(QLabel, "sectionLabel")
        desc_label = page.findChild(QLabel, "sectionDescription")

        title_label.setText(biz.name)
        desc_label.setText(biz.reviews[0])


def main() -> None:
    """Entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()