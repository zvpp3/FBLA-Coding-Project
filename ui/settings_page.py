"""
This module contains the settings UI for LocalLink.

The settings UI lets users change the theme, toggle various options, and export data.
"""

# All imports for the settings page
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
    # simple settings page for theme, recs, motion, and exports

    def __init__(self, data: DataHandler, main_window) -> None:
        super().__init__(data)
        self.main_window = main_window

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(13)

        # label for the title
        title = QLabel("Settings")
        title.setObjectName("sectionLabel")
        layout.addWidget(title)

        # Theme selector
        theme_label = QLabel("Theme")
        theme_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setMinimumHeight(32)
        layout.addWidget(self.theme_combo)

        # show recommendations toggle
        recs_label = QLabel("Show recommendations")
        recs_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(recs_label)
        self.recs_combo = QComboBox()
        # yes/no option to show recommendations on the stats page
        self.recs_combo.addItems(["Yes", "No"])
        self.recs_combo.setMinimumHeight(32)
        layout.addWidget(self.recs_combo)

        # reduce motion toggle
        reduce_label = QLabel("Reduce motion (disable animations)")
        reduce_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(reduce_label)
        self.reduce_combo = QComboBox()
        # users can turn off page animations to reduce motion
        self.reduce_combo.addItems(["No", "Yes"])
        self.reduce_combo.setMinimumHeight(32)
        layout.addWidget(self.reduce_combo)

        # confirm delete toggle
        confirm_label = QLabel("Confirm before removing favorite")
        confirm_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(confirm_label)
        self.confirm_combo = QComboBox()

        # prompt before removing a favorite to avoid accidents
        self.confirm_combo.addItems(["Yes", "No"])
        self.confirm_combo.setMinimumHeight(32)
        layout.addWidget(self.confirm_combo)

        # always on top toggle
        always_on_top_label = QLabel("Always on top (restart app to apply after saving)")
        always_on_top_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(always_on_top_label)
        self.always_on_top_combo = QComboBox()

        # toggle always on top behavior
        self.always_on_top_combo.addItems(["No", "Yes"])
        self.always_on_top_combo.setMinimumHeight(32)
        layout.addWidget(self.always_on_top_combo)

        # export label
        export_label = QLabel("Export data to CSV")
        export_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(export_label)

        # Export all businesses button to CSV
        export_all_btn = QPushButton("Export All Businesses")
        export_all_btn.setMinimumHeight(36)
        export_all_btn.clicked.connect(self.export_all_csv)
        layout.addWidget(export_all_btn)

        # Export favorites only button to CSV
        export_fav_btn = QPushButton("Export Favorites Only")
        export_fav_btn.setMinimumHeight(36)
        export_fav_btn.clicked.connect(self.export_favorites_csv)
        layout.addWidget(export_fav_btn)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("primaryButton")
        save_btn.setMinimumHeight(36)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()

        # Initialize values based on current preferences
        self._sync_widgets_to_preferences()

    def page_shown(self, data=None) -> None:
        # make sure widgets match saved prefs when page shows
        super().page_shown(data)
        self._sync_widgets_to_preferences()

    def _sync_widgets_to_preferences(self) -> None:
        # set the state of each settings widget based on saved preferences

        # theme
        current_theme = self.data.get_preference("theme", "dark").lower()
        # find and set the combo box index to match saved preference
        idx = self.theme_combo.findText(current_theme.capitalize())
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        # show recommendations
        recs_pref = self.data.get_preference("show_recommendations", "yes").lower()
        idx = self.recs_combo.findText(recs_pref.capitalize())
        if idx >= 0:
            self.recs_combo.setCurrentIndex(idx)

        # reduce motion
        reduce_pref = self.data.get_preference("reduce_motion", "no").lower()
        idx = self.reduce_combo.findText(reduce_pref.capitalize())
        if idx >= 0:
            self.reduce_combo.setCurrentIndex(idx)

        # confirm delete
        confirm_pref = self.data.get_preference("confirm_delete", "yes").lower()
        idx = self.confirm_combo.findText(confirm_pref.capitalize())
        if idx >= 0:
            self.confirm_combo.setCurrentIndex(idx)

        # always on top
        always_pref = self.data.get_preference("always_on_top", "no").lower()
        idx = self.always_on_top_combo.findText(always_pref.capitalize())
        if idx >= 0:
            self.always_on_top_combo.setCurrentIndex(idx)

    def save_settings(self) -> None:
        # save the user's choices and apply them right away

        # theme preference
        theme_value = self.theme_combo.currentText().lower()
        self.data.set_preference("theme", theme_value)

        # show recommendations preference
        recs_value = self.recs_combo.currentText().lower()
        self.data.set_preference("show_recommendations", recs_value)

        # reduce motion preference
        reduce_value = self.reduce_combo.currentText().lower()
        self.data.set_preference("reduce_motion", reduce_value)

        # confirm delete preference
        confirm_value = self.confirm_combo.currentText().lower()
        self.data.set_preference("confirm_delete", confirm_value)

        # always on top preference
        always_value = self.always_on_top_combo.currentText().lower()
        self.data.set_preference("always_on_top", always_value)

        # apply preferences (reload styles and cancel animations)
        # so changes like reduce_motion take effect right away
        if hasattr(self.main_window, "apply_preferences"):
            self.main_window.apply_preferences()
        elif hasattr(self.main_window, "load_styles"):
            # fallback if apply_preferences is not available
            self.main_window.load_styles()

    def export_favorites_csv(self) -> None:
        # ask for a filename and export favorites to CSV. show a message on success/failure
        # if user has no favorites, inform them instead of opening the file dialog
        if not self.data.favorite_businesses():
            QMessageBox.information(self, "No favorites", "You have no businesses favorited.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Favorites", "favorites.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            # show a small progress dialog while exporting (this blocks until done)
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Exporting favorites…", None, 0, 0, self)
            progress.setWindowModality(Qt.ApplicationModal)
            progress.setCancelButton(None)
            progress.setAutoClose(False)
            progress.show()

            # perform the export
            self.data.export_businesses_to_csv(path, favorites_only=True)
            progress.close()
            QMessageBox.information(self, "Export Complete", f"Favorites exported to {path}")
        except Exception as exc:
            QMessageBox.warning(self, "Export Failed", f"Could not export favorites: {exc}")

    def export_all_csv(self) -> None:
        # export all businesses to CSV (same flow as favorites export)
        path, _ = QFileDialog.getSaveFileName(self, "Export All Businesses", "businesses.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            # Show progress dialog while exporting all businesses
            from PySide6.QtWidgets import QProgressDialog
            progress = QProgressDialog("Exporting businesses…", None, 0, 0, self)
            # window modality is for blocking input to other windows while progress is shown
            progress.setWindowModality(Qt.ApplicationModal)
            progress.setCancelButton(None)
            progress.setAutoClose(False)
            progress.show()
            self.data.export_businesses_to_csv(path, favorites_only=False)
            progress.close()
            QMessageBox.information(self, "Export Complete", f"All businesses exported to {path}")
        except Exception as exc:
            # safely catch exceptions(errors) and show a message box
            QMessageBox.warning(self, "Export Failed", f"Could not export businesses: {exc}")