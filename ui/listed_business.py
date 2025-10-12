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

class ListedBusiness(QPushButton):

    main_button = Signal(Business)
    favorites_button = Signal(Business)

    def __init__(self, biz: Business):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setFixedHeight(60)

        item_text = f"{biz.name} ({biz.category}) - ⭐ {biz.rating:.1f}"
        self.label = QLabel(item_text)
        self.layout.addWidget(self.label)

        self.layout.addStretch()

        self.favorite_button = QPushButton("☆")
        self.layout.addWidget(self.favorite_button)
        self.favorite_button.setVisible(False)
        
        # Store the underlying Business object for later retrieval
        self.business = biz
        self.clicked.connect(lambda: self.main_button.emit(self.business))
        
    def enterEvent(self, event):
        self.favorite_button.setVisible(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.favorite_button.setVisible(False)
        super().leaveEvent(event)

    