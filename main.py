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
from data.data_handler import DataHandler, Business
from ui.main_window import MainWindow

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

def main() -> None:
    data_handler = DataHandler()
    app = QApplication(sys.argv)
    window = MainWindow(data_handler)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()