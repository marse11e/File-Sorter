from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QPushButton, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QColor, QFont


LOG_COLORS = {
    "info":    QColor("#8888A0"),
    "success": QColor("#3DD68C"),
    "error":   QColor("#F75F5F"),
    "warning": QColor("#F7A94F"),
}


class LogWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        title = QLabel("ЛОГ")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()

        self._clear_btn = QPushButton("🗑")
        self._clear_btn.setObjectName("titleBtn")
        self._clear_btn.setFixedWidth(24)
        self._clear_btn.setFixedHeight(24)
        self._clear_btn.clicked.connect(self.clear)
        header.addWidget(self._clear_btn)

        layout.addLayout(header)

        self._text = QPlainTextEdit()
        self._text.setObjectName("logView")
        self._text.setReadOnly(True)
        self._text.setMaximumBlockCount(5000)
        self._text.setPlaceholderText("Лог операций...")
        layout.addWidget(self._text)

    def log(self, message, msg_type="info"):
        fmt = QTextCharFormat()
        fmt.setForeground(LOG_COLORS.get(msg_type, LOG_COLORS["info"]))
        fmt.setFont(QFont("JetBrains Mono", 10))
        cursor = self._text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(message + "\n", fmt)
        self._text.ensureCursorVisible()

    def clear(self):
        self._text.clear()

    def set_theme(self, dark):
        pass
