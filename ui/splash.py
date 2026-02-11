"""
This is the splash screen module for LocalLink.

This codes for a solid splash "card" with our logo on the left and text on the right.
"""

from PySide6.QtCore import Qt, QPropertyAnimation, QTimer, Property
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
)

class ShimmerBar(QWidget):
    """
    A simple shimmer/progress bar. Animates a highlight across the bar.
    When marked finished, it fills solid and stops animating.
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(10)
        self._shift = 0.0
        self._finished = False

        self._anim = QPropertyAnimation(self, b"shift", self)
        self._anim.setDuration(1100)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setLoopCount(-1)  # infinite

    def start(self) -> None:
        self._finished = False
        self._anim.start()

    def finish(self) -> None:
        self._finished = True
        self._anim.stop()
        self.update()

    def getShift(self) -> float:
        return self._shift

    def setShift(self, value: float) -> None:
        self._shift = value
        self.update()

    shift = Property(float, getShift, setShift)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        r = self.rect()
        radius = 5

        # Base track
        track = QColor("#0f1115")
        border = QColor("#252b38")
        fill = QColor("#49B3FF")

        painter.setPen(border)
        painter.setBrush(track)
        painter.drawRoundedRect(r.adjusted(0, 0, -1, -1), radius, radius)

        if self._finished:
            # Solid filled bar when done
            painter.setPen(Qt.NoPen)
            painter.setBrush(fill)
            painter.drawRoundedRect(r.adjusted(1, 1, -2, -2), radius, radius)
            return

        # Shimmer highlight
        # We draw a moving bright pill across the bar
        w = r.width()
        h = r.height()

        highlight_w = max(40, int(w * 0.22))
        x = int((w + highlight_w) * self._shift) - highlight_w

        # dim base fill
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1d2a3a"))
        painter.drawRoundedRect(r.adjusted(1, 1, -2, -2), radius, radius)

        # bright shimmer
        shimmer_rect = r.adjusted(1, 1, -2, -2)
        shimmer_rect.setLeft(x)
        shimmer_rect.setRight(x + highlight_w)

        painter.setBrush(QColor("#6fd0ff"))
        painter.drawRoundedRect(shimmer_rect, radius, radius)

class SplashScreen(QWidget):
    """Animated splash screen with a solid card + left logo."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # Frameless splash that stays on top
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen
        )

        # Fixed size that looks clean and consistent
        self.setFixedSize(720, 260)

        # set whole window background transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        # --- Solid card container ---
        self.card = QWidget(self)
        self.card.setObjectName("splashCard")
        self.card.setGeometry(30, 30, self.width() - 60, self.height() - 60)
        self.card.setStyleSheet("""
            QWidget#splashCard {
                background: #161a22;
                border: 1px solid #252b38;
                border-radius: 18px;
            }
        """)

        # Layout inside the card: logo left, text right
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(26, 22, 26, 22)
        card_layout.setSpacing(18)

        # --- Left logo ---
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(120, 120)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            background: #0f1115;
            border: 1px solid #252b38;
            border-radius: 16px;
        """)

        # Center the splash on the screen
        screen = self.screen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

        pix = QPixmap("assets/logo.png")
        if not pix.isNull():
            self.logo_label.setPixmap(
                pix.scaled(86, 86, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )

        card_layout.addWidget(self.logo_label, 0, Qt.AlignVCenter)

        # --- Right text stack ---
        text_col = QWidget()
        text_layout = QVBoxLayout(text_col)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)
        text_layout.setAlignment(Qt.AlignVCenter)

        self.title_label = QLabel("LocalLink")
        title_font = QFont()
        title_font.setPointSize(40)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: #49B3FF;")

        self.tagline_label = QLabel("Connecting you to local businesses")
        tagline_font = QFont()
        tagline_font.setPointSize(15)
        tagline_font.setItalic(True)
        self.tagline_label.setFont(tagline_font)
        self.tagline_label.setStyleSheet("color: #d6d9e0;")

        self.sub_label = QLabel("Loading…")
        sub_font = QFont()
        sub_font.setPointSize(12)
        self.sub_label.setFont(sub_font)
        self.sub_label.setStyleSheet("color: #8e95a6;")

        # Loading dots animation: Loading -> Loading. -> Loading.. -> Loading...
        self._loading_base = "Loading"
        self._loading_step = 0

        self._loading_timer = QTimer(self)
        self._loading_timer.setInterval(350)  # speed of the dots
        self._loading_timer.timeout.connect(self._tick_loading)
        self._loading_timer.start()

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.tagline_label)
        text_layout.addSpacing(6)
        text_layout.addWidget(self.sub_label)

        # Shimmer progress bar
        self.shimmer = ShimmerBar()
        text_layout.addSpacing(10)
        text_layout.addWidget(self.shimmer)

        self.shimmer.start()

        card_layout.addWidget(text_col, 1)

        #Fade animations
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0.0)

        self.fade_in = QPropertyAnimation(self.effect, b"opacity", self)
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)

        self.fade_out = QPropertyAnimation(self.effect, b"opacity", self)
        self.fade_out.setDuration(800)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.finished.connect(self.close)

        self.fade_in.start()

        # after the shimmer runs a bit, we mark the loaded state, then fade out shortly after
        QTimer.singleShot(4500, self._mark_loaded)
        QTimer.singleShot(5500, self._start_fade_out)

    def _start_fade_out(self) -> None:
        self.fade_out.start()

    def _tick_loading(self) -> None:
        self._loading_step = (self._loading_step + 1) % 4
        self.sub_label.setText(self._loading_base + ("." * self._loading_step))

    # function for marking the splash as loaded, we check if the shimmer exists by looking if there is a shimmer attribute on self
    def _mark_loaded(self) -> None:
        self.sub_label.setText("Loaded")
        if hasattr(self, "shimmer"):
            self.shimmer.finish()
        if hasattr(self, "_loading_timer"):
            self._loading_timer.stop()