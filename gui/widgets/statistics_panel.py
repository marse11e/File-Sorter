from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QFrame, QLabel
from PySide6.QtCore import Qt


class StatCard(QFrame):
    def __init__(self, label, value="0", accent=False, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self._accent = accent
        self._setup_ui(label, value)

    def _setup_ui(self, label, value):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        self._value_label = QLabel(value)
        self._value_label.setObjectName("statValue")
        if self._accent:
            self._value_label.setProperty("class", "accent")
            self._value_label.setStyleSheet("color: #4F6EF7; font-size: 20px; font-weight: 600;")
        layout.addWidget(self._value_label, alignment=Qt.AlignCenter)

        self._label_text = QLabel(label)
        self._label_text.setObjectName("statLabel")
        layout.addWidget(self._label_text, alignment=Qt.AlignCenter)

    def set_value(self, value):
        self._value_label.setText(str(value))


class StatisticsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("СТАТИСТИКА")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(6)

        self._found_card = StatCard("Найдено", "0")
        grid.addWidget(self._found_card, 0, 0)

        self._selected_card = StatCard("Выбрано", "0", accent=True)
        grid.addWidget(self._selected_card, 0, 1)

        self._size_card = StatCard("Размер", "0 B")
        grid.addWidget(self._size_card, 1, 0)

        self._moved_card = StatCard("Перемещено", "0")
        grid.addWidget(self._moved_card, 1, 1)

        layout.addLayout(grid)

    def set_found(self, count, total_size=0):
        self._found_card.set_value(str(count))
        self._size_card.set_value(self._format_size(total_size))

    def set_selected(self, count):
        self._selected_card.set_value(str(count))

    def set_moved(self, count):
        self._moved_card.set_value(str(count))

    def reset(self):
        self._found_card.set_value("0")
        self._selected_card.set_value("0")
        self._size_card.set_value("0 B")
        self._moved_card.set_value("0")

    @staticmethod
    def _format_size(size_bytes):
        for unit in ("B", "KB", "MB", "GB"):
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
