from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent


class DragHandle(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dragHandle")
        self.setFixedWidth(40)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        grip = QLabel("⠿")
        grip.setStyleSheet("color: #5A5A70; font-size: 16px;")
        layout.addWidget(grip)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window().windowHandle()
            if win:
                win.startSystemMove()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window().windowHandle()
            if win:
                win.startSystemMove()


class TitleBar(QWidget):
    minimize_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(36)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        drag = DragHandle(self)
        layout.addWidget(drag)

        title = QLabel("File Sorter")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        version = QLabel("v1.0")
        version.setObjectName("versionLabel")
        layout.addWidget(version)

        layout.addStretch()

        self._min_btn = QPushButton("─")
        self._min_btn.setObjectName("titleBtn")
        self._min_btn.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self._min_btn)

        self._close_btn = QPushButton("✕")
        self._close_btn.setObjectName("titleBtnClose")
        self._close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self._close_btn)
