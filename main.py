# Main

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from typing import List

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
)

from data.data_handler import DataHandler

from ui.main_window import MainWindow

def main() -> None:
    app = QApplication(sys.argv)
    data = DataHandler()
    window = MainWindow(data)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()