"""
This is the startup module/entry point for LocalLink.

RUN THIS FILE ONLY TO START THE APPLICATION. DONT RUN ANY OTHER FILE(or else the code wont run!)
"""

# imports used as references
import sys
from data.data_handler import DataHandler 
from ui.main_window import MainWindow
from ui.splash import SplashScreen
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

from PySide6.QtWidgets import (
    QApplication,
)

# main app start
def main() -> None:
    """
    This is the application entry point. This file initializes the Qt application, shows
    a startup splash screen with a brief animation, then constructs
    and displays the main window. The splash runs asynchronously
    and automatically closes itself after its animation completes.

    By keeping all initialization inside this function, it makes testing
    easier and avoids side effects when importing this module.
    """
    # create the application instance
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/logo.png"))

    # Initialize the data handler before showing any UI. This loads
    # businesses and user preferences from disk.
    data_handler = DataHandler()

    # Show a splash screen with a fade‑in/out animation. The splash
    # runs its own timers and closes itself after a short delay.
    # This is purely for style points.
    splash = SplashScreen()
    splash.show()

    # Defer creation of the main window until after the splash has
    # started. If no splash exists, show the main window immediately.
    def start_main_window() -> None:
        """Construct and show the main window."""
        window = MainWindow(data_handler, True)
        window.show()
        # If a splash screen exists, close it when the main window appears
        if splash:
            splash.close()

    # Use a timer to delay the window display until the splash finishes
    # 6 seconds gives time for fade in and a moment of display
    QTimer.singleShot(6000, start_main_window)

    # Enter the Qt event loop
    sys.exit(app.exec())

# run main if this file is run directly
if __name__ == "__main__":
    main()