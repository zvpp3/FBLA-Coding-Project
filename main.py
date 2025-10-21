"""Refactored LocalLink main module.

This version organizes the app into clearer functions/classes, uses a
dataclass for business records, human-readable names, and keeps the
existing behavior (search, details, reviews, favorites persistence).
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import List, Optional, Set
from data.data_handler import DataHandler, BusinessRecord

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
    QVBoxLayout,
    QWidget,
)

DATA_FILE = "data/businesses.json"



class LocalLinkWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LocalLink")
        self.resize(1000, 600)
        # Data
        self.data = DataHandler()
        self.businesses: List[BusinessRecord] = []
        self.current_business: Optional[BusinessRecord] = None

        # Build UI and load data
        self._build_ui()
        self._load_businesses()
        self._refresh_business_list()
        self._refresh_favorites_list()

    # ---------------- UI ----------------
    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        top_layout = QHBoxLayout(root)

        # Sidebar
        sidebar = QWidget(); sb_layout = QVBoxLayout(sidebar); sb_layout.setContentsMargins(12,24,12,24)
        for label, idx in [("Home", 0), ("Businesses", 1), ("Favorites", 2), ("About", 3), ("Exit", None)]:
            btn = QPushButton(label); btn.setObjectName("navButton"); btn.setMinimumHeight(36)
            if label == "Exit":
                btn.clicked.connect(self.close)
            else:
                btn.clicked.connect(lambda _, i=idx: self.pages.setCurrentIndex(i))
            sb_layout.addWidget(btn)
        sb_layout.addStretch()

        # Pages
        self.pages = QStackedWidget()
        self.pages.addWidget(self._page_home())
        self.pages.addWidget(self._page_businesses())
        self.pages.addWidget(self._page_favorites())
        self.pages.addWidget(self._page_about())
        self.pages.addWidget(self._page_details())

        top_layout.addWidget(sidebar); top_layout.addWidget(self.pages)

        # stylesheet
        qss = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(qss):
            with open(qss, "r", encoding="utf8") as f:
                self.setStyleSheet(f.read())

    def _page_home(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter)
        title_label = QLabel("LocalLink - A local business supporting app"); title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("Discover and support your local businesses!"); subtitle_label.setObjectName("subtitleLabel")
        layout.addWidget(title_label); layout.addWidget(subtitle_label); return page

    def _page_businesses(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(16,16,16,16)
        self.search = QLineEdit(); self.search.setPlaceholderText("Search businesses by name or category...")
        self.search.textChanged.connect(self._on_search)
        layout.addWidget(self.search)
        self.list_business = QListWidget(); self.list_business.itemClicked.connect(self._open_details_from_item)
        layout.addWidget(self.list_business); return page

    def _page_favorites(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); section_label = QLabel("Favorites"); section_label.setObjectName("sectionLabel"); layout.addWidget(section_label)
        self.list_favorites = QListWidget(); self.list_favorites.itemClicked.connect(self._open_details_from_item)
        layout.addWidget(self.list_favorites); layout.addStretch(); return page

    def _page_about(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page); section_label = QLabel("About"); section_label.setObjectName("sectionLabel"); layout.addWidget(section_label)
        about_text = QLabel("Built for FBLA. Uses PySide6 to list and favorite local businesses."); about_text.setWordWrap(True)
        layout.addWidget(about_text); layout.addStretch(); return page

    def _page_details(self) -> QWidget:
        page = QWidget(); layout = QVBoxLayout(page)
        header_layout = QHBoxLayout(); title_label = QLabel("Business"); title_label.setObjectName("sectionLabel"); header_layout.addWidget(title_label); header_layout.addStretch()
        # favorite button: show only a star character, size controlled by QSS
        self.btn_fav = QPushButton("☆"); self.btn_fav.setObjectName("favButtonLarge"); self.btn_fav.setFlat(True); self.btn_fav.clicked.connect(self._toggle_favorite); header_layout.addWidget(self.btn_fav)
        layout.addLayout(header_layout)
        self.lbl_desc = QLabel("Description"); self.lbl_desc.setWordWrap(True); self.lbl_desc.setObjectName("sectionDescription"); layout.addWidget(self.lbl_desc)
        layout.addStretch(); layout.addWidget(QLabel("Reviews")); self.list_reviews = QListWidget(); layout.addWidget(self.list_reviews)
        return page

    # ---------------- Data ----------------
    def _load_businesses(self) -> None:
        # DataHandler already loads businesses on init; keep local reference
        self.businesses = self.data.list_businesses()

    # ---------------- Helpers ----------------
    def _item_text(self, business: BusinessRecord) -> str:
        return f"{business.name} ({business.category}) - ⭐ {business.rating:.1f}"

    def _refresh_business_list(self, items: Optional[List[BusinessRecord]] = None) -> None:
        self.list_business.clear()
        for business in (items or self.businesses):
            list_item = QListWidgetItem(self._item_text(business))
            list_item.setData(Qt.UserRole, business)
            self.list_business.addItem(list_item)

    def _refresh_favorites_list(self) -> None:
        self.list_favorites.clear()
        for favorite in self.data.favorite_records():
            list_item = QListWidgetItem(self._item_text(favorite))
            list_item.setData(Qt.UserRole, favorite)
            self.list_favorites.addItem(list_item)

    # ---------------- Events ----------------
    def _on_search(self, text: str) -> None:
        query = text.lower().strip()
        if not query:
            self._refresh_business_list(); return
        self._refresh_business_list([record for record in self.businesses if query in record.name.lower() or query in record.category.lower()])

    def _open_details_from_item(self, item: QListWidgetItem) -> None:
        business: BusinessRecord = item.data(Qt.UserRole)
        self._show_details(business)

    def _show_details(self, business: BusinessRecord) -> None:
        """Show the details page for a business and populate its content."""
        self.current_business = business
        self.pages.setCurrentIndex(4)

        lbl = self.findChild(QLabel, "sectionLabel")
        if lbl:
            lbl.setText(business.name)

        self.lbl_desc.setText(f"Deals: {', '.join(business.deals) if business.deals else 'None'}")
        self.list_reviews.clear()
        for review in business.reviews:
            review_item = QListWidgetItem(f"{review.get('user','')} (⭐ {review.get('rating',0)}) - {review.get('text','')}")
            self.list_reviews.addItem(review_item)

        # show star only; white when not favorited, yellow when favorited
        if self.data.is_favorite(business):
            self.btn_fav.setText("★")
            self.btn_fav.setStyleSheet("color: #f1c40f; font-weight: bold;")
        else:
            self.btn_fav.setText("☆")
            self.btn_fav.setStyleSheet("color: #ffffff;")

    def _toggle_favorite(self) -> None:
        business = self.current_business
        if not business:
            return

        self.data.toggle_favorite(business)

        if self.data.is_favorite(business):
            self.btn_fav.setText("★")
            self.btn_fav.setStyleSheet("color: #f1c40f; font-weight: bold;")
        else:
            self.btn_fav.setText("☆")
            self.btn_fav.setStyleSheet("color: #ffffff;")

        self._refresh_favorites_list()


def main() -> None:
    app = QApplication(sys.argv)
    w = LocalLinkWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()