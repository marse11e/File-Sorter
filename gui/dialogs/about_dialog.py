from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtCore import QUrl


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setFixedSize(360, 240)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        icon = QLabel("🗂")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("File Sorter")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #E8E8F0;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        version = QLabel("Версия 1.0")
        version.setStyleSheet("font-size: 12px; color: #8888A0;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        layout.addSpacing(8)

        desc = QLabel("Автоматическая сортировка файлов по типам")
        desc.setStyleSheet("font-size: 12px; color: #8888A0;")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        author = QLabel('<a href="https://github.com/marse11e" style="color: #4F6EF7;">by @marse11e</a>')
        author.setStyleSheet("font-size: 12px;")
        author.setAlignment(Qt.AlignCenter)
        author.setOpenExternalLinks(True)
        layout.addWidget(author)

        layout.addStretch()

        btn = QPushButton("Закрыть")
        btn.setObjectName("primaryBtn")
        btn.setFixedWidth(120)
        btn.setFixedHeight(32)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
