"""
This module defines a simple settings page where users can configure
application preferences such as the UI theme. The settings page is
integrated with the DataHandler to persist user preferences to disk and
applies the chosen theme immediately via the main window.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QMessageBox,
)

from data.data_handler import DataHandler
from ui.pages import Page


class SettingsPage(Page):
    """A page allowing users to configure LocalLink preferences."""

    def __init__(self, data: DataHandler, main_window) -> None:
        super().__init__(data)
        self.main_window = main_window

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Settings")
        title.setObjectName("sectionLabel")
        layout.addWidget(title)

        # Theme selector
        theme_label = QLabel("Theme")
        layout.addWidget(theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        layout.addWidget(self.theme_combo)

        # Show recommendations toggle
        recs_label = QLabel("Show recommendations")
        layout.addWidget(recs_label)
        self.recs_combo = QComboBox()
        # Yes/No options for whether to show recommended businesses on the
        # statistics page.  Changing this preference will update the
        # recommendations section immediately when the settings are saved.
        self.recs_combo.addItems(["Yes", "No"])
        layout.addWidget(self.recs_combo)

        # Reduce motion toggle
        reduce_label = QLabel("Reduce motion (disable animations)")
        layout.addWidget(reduce_label)
        self.reduce_combo = QComboBox()
        # Users can choose to turn off page transition animations.  If
        # animations cause motion sickness or sluggishness, selecting
        # "Yes" will make the interface switch pages instantly.
        self.reduce_combo.addItems(["No", "Yes"])
        layout.addWidget(self.reduce_combo)

        # Confirm delete toggle
        confirm_label = QLabel("Confirm before removing favorite")
        layout.addWidget(confirm_label)
        self.confirm_combo = QComboBox()
        # Prompting the user before removing a business from favorites
        # prevents accidental deletions.  Choose "Yes" to enable a
        # confirmation dialog on unfavorite actions.
        self.confirm_combo.addItems(["Yes", "No"])
        layout.addWidget(self.confirm_combo)

        # Export section
        export_label = QLabel("Export data to CSV")
        layout.addWidget(export_label)
        export_all_btn = QPushButton("Export All Businesses")
        export_all_btn.clicked.connect(self.export_all_csv)
        layout.addWidget(export_all_btn)
        export_fav_btn = QPushButton("Export Favorites Only")
        export_fav_btn.clicked.connect(self.export_favorites_csv)
        layout.addWidget(export_fav_btn)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()

        # Initialize values based on current preferences
        self._sync_widgets_to_preferences()

    def page_shown(self, data=None) -> None:
        """Ensure widgets reflect current preferences when page is shown."""
        super().page_shown(data)
        self._sync_widgets_to_preferences()

    def _sync_widgets_to_preferences(self) -> None:
        """Set the state of each settings widget based on saved preferences."""
        # Theme
        current_theme = self.data.get_preference("theme", "dark").lower()
        idx = self.theme_combo.findText(current_theme.capitalize())
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        # Show recommendations
        recs_pref = self.data.get_preference("show_recommendations", "yes").lower()
        idx = self.recs_combo.findText(recs_pref.capitalize())
        if idx >= 0:
            self.recs_combo.setCurrentIndex(idx)

        # Reduce motion
        reduce_pref = self.data.get_preference("reduce_motion", "no").lower()
        idx = self.reduce_combo.findText(reduce_pref.capitalize())
        if idx >= 0:
            self.reduce_combo.setCurrentIndex(idx)

        # Confirm delete
        confirm_pref = self.data.get_preference("confirm_delete", "yes").lower()
        idx = self.confirm_combo.findText(confirm_pref.capitalize())
        if idx >= 0:
            self.confirm_combo.setCurrentIndex(idx)

    def save_settings(self) -> None:
        """
        Persist settings to the data handler and refresh the main window.

        This method collects the current values from all settings widgets,
        stores them in the DataHandler's preferences dictionary and then
        triggers the main window to refresh its appearance.
        """
        # Theme preference
        theme_value = self.theme_combo.currentText().lower()
        self.data.set_preference("theme", theme_value)
        # Show recommendations preference
        recs_value = self.recs_combo.currentText().lower()
        self.data.set_preference("show_recommendations", recs_value)
        # Reduce motion preference
        reduce_value = self.reduce_combo.currentText().lower()
        self.data.set_preference("reduce_motion", reduce_value)
        # Confirm delete preference
        confirm_value = self.confirm_combo.currentText().lower()
        self.data.set_preference("confirm_delete", confirm_value)
        # Reload styles to apply theme changes
        if hasattr(self.main_window, "load_styles"):
            self.main_window.load_styles()

    def export_favorites_csv(self) -> None:
        """
        Prompt the user to select a filename and then export only favorite
        businesses to that CSV file. A message box informs the user of
        success or failure. If the user cancels the file dialog, nothing
        happens.
        """
        path, _ = QFileDialog.getSaveFileName(self, "Export Favorites", "favorites.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            # Show a simple progress dialog while exporting.  The export
            # function is synchronous, so the dialog will block the UI until
            # the operation finishes.  This gives users feedback that the
            # application is working.
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Exporting favorites…", None, 0, 0, self)
            progress.setWindowModality(Qt.ApplicationModal)
            progress.setCancelButton(None)
            progress.setAutoClose(False)
            progress.show()
            # Perform the export
            self.data.export_businesses_to_csv(path, favorites_only=True)
            progress.close()
            QMessageBox.information(self, "Export Complete", f"Favorites exported to {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Export Failed", f"Could not export favorites: {exc}")

    def export_all_csv(self) -> None:
        """
        Prompt the user to select a filename and then export all
        businesses to that CSV file. A message box informs the user of
        success or failure. If the user cancels the file dialog, nothing
        happens.
        """
        path, _ = QFileDialog.getSaveFileName(self, "Export All Businesses", "businesses.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            # Show progress dialog while exporting all businesses
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Exporting businesses…", None, 0, 0, self)
            progress.setWindowModality(Qt.ApplicationModal)
            progress.setCancelButton(None)
            progress.setAutoClose(False)
            progress.show()
            self.data.export_businesses_to_csv(path, favorites_only=False)
            progress.close()
            QMessageBox.information(self, "Export Complete", f"All businesses exported to {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Export Failed", f"Could not export businesses: {exc}")