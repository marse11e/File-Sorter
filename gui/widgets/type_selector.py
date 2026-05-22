from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QButtonGroup
from PySide6.QtCore import Signal, Qt

TYPE_CONFIG = [
    {"key": "photo",    "label": "Изображения", "icon": "🖼"},
    {"key": "document", "label": "Документы",   "icon": "📄"},
    {"key": "video",    "label": "Видео",       "icon": "🎬"},
    {"key": "music",    "label": "Музыка",      "icon": "🎵"},
    {"key": "archive",  "label": "Архивы",      "icon": "📦"},
]


class TypeSelector(QWidget):
    type_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_key = "video"
        self._buttons = {}
        self._count_labels = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title = QLabel("ТИПЫ ФАЙЛОВ")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)

        for cfg in TYPE_CONFIG:
            btn = QPushButton()
            btn.setObjectName("typeCard")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(44)

            inner = QHBoxLayout(btn)
            inner.setContentsMargins(12, 0, 12, 0)
            inner.setSpacing(8)

            icon = QLabel(cfg["icon"])
            icon.setFixedWidth(20)
            inner.addWidget(icon)

            label = QLabel(cfg["label"])
            label.setStyleSheet("color: #E8E8F0; font-size: 13px;")
            inner.addWidget(label)

            inner.addStretch()

            count = QLabel("0")
            count.setObjectName("typeCount")
            self._count_labels[cfg["key"]] = count
            inner.addWidget(count)

            self._group.addButton(btn)
            self._buttons[cfg["key"]] = btn
            layout.addWidget(btn)

            if cfg["key"] == self._selected_key:
                btn.setChecked(True)

        self._group.idClicked.connect(self._on_clicked)
        layout.addStretch()

    def _on_clicked(self, btn_id):
        for key, btn in self._buttons.items():
            if self._group.button(btn_id) is btn:
                self._selected_key = key
                self.type_changed.emit(key)
                break

    def selected_key(self):
        return self._selected_key

    def select_key(self, key):
        if key in self._buttons:
            self._buttons[key].setChecked(True)
            self._selected_key = key
            self.type_changed.emit(key)

    def set_count(self, type_key, count):
        if type_key in self._count_labels:
            self._count_labels[type_key].setText(str(count))

    def set_counts(self, counts: dict):
        for key, count in counts.items():
            self.set_count(key, count)
