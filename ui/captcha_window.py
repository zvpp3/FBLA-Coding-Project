# imports
from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton
)
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QPainterPath
)
from PySide6.QtGui import QFont
from PySide6.QtCore import (
    Qt, QPoint, QPropertyAnimation, QEasingCurve, Signal
)
import os, random

class CaptchaWindow(QWidget):
    captcha_passed = Signal()

    # initialize the window
    def __init__(self):
        super().__init__()

        #Base window
        self.setWindowTitle("Verify CAPTCHA")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        # main layout
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(10, 10, 10, 10)

        # background image
        self.bg_label = QLabel(self)
        self.bg_label.setFixedSize(600, 450)
        self.bg_label.setStyleSheet("background-color: #444; border-radius: 4px;")

        # puzzle piece
        self.piece_label = QLabel(self)
        self.piece_label.setFixedSize(75, 75)
        self.piece_label.setStyleSheet("background: transparent;")

        # load background
        self.bg = self._load_or_generate_background()

        # puzzle variables
        self.piece_size = 75
        # padding which keeps the piece inside the image when sliding
        self.left_padding = 6
        self.right_padding = 6
        # compute the left (starting point) of the image
        self.bg_left = (self.width() - self.bg_label.width()) // 2
        # min/max positions for the piece
        self.min_x = self.bg_left + self.left_padding
        self.max_x = self.bg_left + self.bg_label.width() - self.piece_size - self.right_padding

        self._randomize_cut_position()  

        # builds visuals
        self._build_puzzle()

        # regen button
        btn_layout = QHBoxLayout()
        self.regen_btn = QPushButton("Regenerate")
        self.regen_btn.clicked.connect(self._regen)
        self.regen_btn.setStyleSheet("background-color:#333; padding:6px; color:white;")

        # stretch before and after
        btn_layout.addStretch()
        btn_layout.addWidget(self.regen_btn)
        btn_layout.addStretch()

        # captcha slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self._slider_changed)
        self.slider.sliderReleased.connect(self._check_success)

        # slider style
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 10px;
                background: #333;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #49B3FF;
                width: 20px;
                border-radius: 6px;
            }
        """)

        # instructions text
        self.instruction_label = QLabel("Drag the slider to fill in the missing piece!")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setPointSize(14)
        f.setBold(True)
        self.instruction_label.setFont(f)
        self.instruction_label.setFixedHeight(48)
        self.instruction_label.setStyleSheet(
            "color: #E6F7FF;"
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2b2b2b, stop:1 #3a3a3a);"
            "padding: 8px; border-radius: 8px;"
        )

        # add widgets (or guis) and put instruction label on top, then put a layout for the button to evenly keep slider and btn together
        self.root.addWidget(self.instruction_label, alignment=Qt.AlignCenter)
        self.root.addWidget(self.bg_label, alignment=Qt.AlignCenter)
        self.root.addLayout(btn_layout)
        self.root.addSpacing(10)
        self.root.addWidget(self.slider)

        # a nice animation if the slider is put in the wrong place
        self.anim = QPropertyAnimation(self.piece_label, b"pos")
        self.anim.setDuration(350)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

    # function for loading the background
    def _load_or_generate_background(self):
        path = "assets/captcha"
        # check path validity
        if os.path.exists(path):
            #check for captcha images
            files = [f for f in os.listdir(path)
                     if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            if files:
                #get a random selection and 
                img = random.choice(files)
                imgpath = os.path.join(path, img)
                return QPixmap(imgpath).scaled(
                    600, 450, Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                )

    # function for randomizing the cutout position
    def _randomize_cut_position(self):
        self.cut_x = random.randint(100, 600 - 150)
        self.cut_y = random.randint(100, 450 - 150)
        self.offset_y = self.cut_y + 66 # When qpainter cuts the hole, the y needs to be offset (they dont have the same y level??) 
        # bounds for the puzzle x position
        self.correct_x = self.bg_left + self.cut_x

    # function for building the image and cutting the hole
    def _build_puzzle(self):
        # draw hole
        bg_copy = QPixmap(self.bg)
        p = QPainter(bg_copy)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(0, 0, 0))  # pitch black hole (we dont actually cut out the image)
        p.setPen(Qt.NoPen)
        p.drawEllipse(self.cut_x, self.cut_y, self.piece_size, self.piece_size) # draws the hole at pos(xy) and size(xy)
        p.end()

        self.bg_label.setPixmap(bg_copy)

        # now getting the puzzle piece
        piece = QPixmap(self.piece_size, self.piece_size)
        piece.fill(Qt.transparent)

        p = QPainter(piece)
        p.setRenderHint(QPainter.Antialiasing)

        mask = QPainterPath() # cutout is a mask
        mask.addEllipse(0, 0, self.piece_size, self.piece_size)
        p.setClipPath(mask)
        #reflect the position when its made
        p.drawPixmap(-self.cut_x, -self.cut_y, self.bg)
        p.end()

        self.piece_label.setPixmap(piece)
        # set the position at the origin x
        self.piece_label.move(self.min_x, self.offset_y)

    # regenerate function
    def _regen(self):
        # call every function over again
        self.bg = self._load_or_generate_background()
        self._randomize_cut_position()
        self._build_puzzle()

        # reset the slider *after* we build everything
        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)

    # slider changed connection, this is how we change the sliders position
    def _slider_changed(self, value):
        # get the min and max x bounds
        min_x = self.min_x
        max_x = self.max_x

        # convert the bounds to a 1000 value scale (this is how we determine if the user gets the right puzzle position)
        new_x = min_x + (value / 1000) * (max_x - min_x)

        self.piece_label.move(int(new_x), self.offset_y)

    # check the puzzles position and animate back if it fails
    def _check_success(self):
        current_x = self.piece_label.x()

        if abs(current_x - self.correct_x) <= 6:
            self.captcha_passed.emit()
            self.close()
            return

        # nice animation back if user fails
        self.anim.stop()
        self.anim.setStartValue(QPoint(current_x, self.offset_y))
        self.anim.setEndValue(QPoint(self.min_x, self.offset_y))
        self.anim.start()

        # reset the slider after the animation is done playing
        self.anim.finished.connect(lambda: self._reset_slider_once())

    #function for resetting the slider (blocks any signals while we reset it)
    def _reset_slider_once(self):
        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)