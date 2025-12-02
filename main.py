from __future__ import annotations

import sys
from data.data_handler import DataHandler
from ui.main_window import MainWindow

from PySide6.QtWidgets import (
    QApplication,
)

DATA_FILE = "data/businesses.json"

def main() -> None:
    data_handler = DataHandler()
    app = QApplication(sys.argv)
    window = MainWindow(data_handler, True)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()