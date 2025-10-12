from PySide6.QtCore import (
    Qt,
    Signal
)
from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
    QHBoxLayout,
    QLabel,
    QListWidgetItem
)

from data.data_handler import Business

class FavoriteButton(QPushButton):
    click_signal = Signal()
    def __init__(self, biz: Business):
        super().__init__()

        self.business = biz
        if biz:
            self.update()
        self.clicked.connect(self.on_click)

    def on_click(self):
        self.click_signal.emit()
        self.update()

    def update(self):
        self.setText("★" if self.business.favorited else "☆")

class ListedBusiness(QPushButton):

    main_button_clicked = Signal(Business)
    favorite_button_clicked = Signal(Business)

    def __init__(self, biz: Business):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setFixedHeight(60)

        item_text = f"{biz.name} ({biz.category}) - ⭐ {biz.rating:.1f}"
        self.label = QLabel(item_text)
        self.layout.addWidget(self.label)

        self.layout.addStretch()

        self.favorite_button = FavoriteButton(biz)
        self.layout.addWidget(self.favorite_button)
        self.favorite_button.setVisible(False)
        
        # Store the underlying Business object for later retrieval
        self.business = biz
        self.clicked.connect(lambda: self.main_button_clicked.emit(self.business))
        self.favorite_button.click_signal.connect(lambda: self.favorite_button_clicked.emit(self.business))
        
    def enterEvent(self, event):
        self.favorite_button.setVisible(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.favorite_button.setVisible(False)
        super().leaveEvent(event)