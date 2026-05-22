import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
                               QTreeWidgetItem, QLineEdit, QPushButton, QLabel,
                               QFrame, QStackedWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont, QIcon, QPainter, QPixmap


def _format_size(size_bytes):
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


STATUS_STYLES = {
    "found":    (QColor("#2A2A32"), QColor("#8888A0")),
    "moved":    (QColor(61, 214, 140, 38), QColor("#3DD68C")),
    "error":    (QColor(247, 95, 95, 38), QColor("#F75F5F")),
    "duplicate":(QColor(247, 169, 79, 38), QColor("#F7A94F")),
}


class StatusBadge(QLabel):
    def __init__(self, status="found", parent=None):
        super().__init__(parent)
        self._status = status
        self.setFixedHeight(22)
        self.setAlignment(Qt.AlignCenter)
        self._update_style()

    def _update_style(self):
        bg, fg = STATUS_STYLES.get(self._status, STATUS_STYLES["found"])
        self.setText(self._status.capitalize() if self._status != "found" else "Найден")
        self.setStyleSheet(
            f"background-color: {bg.name(QColor.NameFormat.HexArgb)};"
            f"color: {fg.name()};"
            f"border-radius: 4px;"
            f"font-size: 11px;"
            f"font-weight: 500;"
            f"padding: 0 8px;"
        )

    def set_status(self, status):
        self._status = status
        self._update_style()


class PreviewTable(QWidget):
    selection_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._files = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search row
        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self._search_field = QLineEdit()
        self._search_field.setObjectName("searchField")
        self._search_field.setPlaceholderText("🔍  Фильтр по имени...")
        self._search_field.textChanged.connect(self._apply_filter)
        search_row.addWidget(self._search_field)

        self._select_all_btn = QPushButton("Выбрать все")
        self._select_all_btn.setObjectName("textBtn")
        self._select_all_btn.clicked.connect(self._select_all)
        search_row.addWidget(self._select_all_btn)

        self._deselect_btn = QPushButton("Снять")
        self._deselect_btn.setObjectName("textBtn")
        self._deselect_btn.clicked.connect(self._deselect_all)
        search_row.addWidget(self._deselect_btn)

        layout.addLayout(search_row)

        # Stack: empty state | tree
        self._stack = QStackedWidget()

        # Empty state
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)

        folder_icon = QLabel("📁")
        folder_icon.setObjectName("emptyIcon")
        folder_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(folder_icon)

        empty_text = QLabel('Нажмите «Сканировать» для поиска файлов')
        empty_text.setObjectName("emptyText")
        empty_text.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_text)

        self._stack.addWidget(empty_widget)

        # Tree
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)

        self._tree = QTreeWidget()
        self._tree.setAlternatingRowColors(True)
        self._tree.setHeaderLabels(["", "Имя файла", "Размер", "Папка", "Статус"])
        self._tree.setColumnWidth(0, 30)
        self._tree.setColumnWidth(1, 200)
        self._tree.setColumnWidth(2, 70)
        self._tree.setColumnWidth(3, 160)
        self._tree.setColumnWidth(4, 90)
        self._tree.setRootIsDecorated(False)
        self._tree.header().setStretchLastSection(False)
        self._tree.header().setStretchLastSection(True)
        self._tree.itemChanged.connect(self._on_item_changed)
        self._tree.setMouseTracking(True)
        tree_layout.addWidget(self._tree)

        self._stack.addWidget(tree_container)
        self._stack.setCurrentIndex(0)
        layout.addWidget(self._stack, stretch=1)

    def _select_all(self):
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if not item.isHidden():
                item.setCheckState(0, Qt.CheckState.Checked)

    def _deselect_all(self):
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if not item.isHidden():
                item.setCheckState(0, Qt.CheckState.Unchecked)

    def _on_item_changed(self, item, column):
        if column == 0:
            checked = sum(
                1 for i in range(self._tree.topLevelItemCount())
                if self._tree.topLevelItem(i).checkState(0) == Qt.CheckState.Checked
            )
            self.selection_changed.emit(checked)

    def set_files(self, files):
        self._files = files
        self._tree.clear()
        self._stack.setCurrentIndex(1 if files else 0)

        items = []
        for f in files:
            item = QTreeWidgetItem()
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked)
            item.setText(1, f["name"])
            item.setText(2, _format_size(f["size"]))
            item.setText(3, os.path.basename(f["folder"]) if f["folder"] else "")
            item.setData(0, Qt.ItemDataRole.UserRole, f)

            badge = StatusBadge("found")
            self._tree.setItemWidget(item, 4, badge)

            items.append(item)

        self._tree.setUpdatesEnabled(False)
        self._tree.addTopLevelItems(items)
        self._tree.setUpdatesEnabled(True)

        self._search_field.clear()

    def clear_data(self):
        self._files = []
        self._tree.clear()
        self._stack.setCurrentIndex(0)

    def checked_files(self):
        result = []
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            if not item.isHidden() and item.checkState(0) == Qt.CheckState.Checked:
                result.append(item.data(0, Qt.ItemDataRole.UserRole))
        return result

    def update_status(self, path, status):
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.get("path") == path:
                badge = self._tree.itemWidget(item, 4)
                if badge:
                    badge.set_status(status)
                break

    def _apply_filter(self, text):
        text = text.lower().strip()
        for i in range(self._tree.topLevelItemCount()):
            item = self._tree.topLevelItem(i)
            name = item.text(1).lower()
            item.setHidden(bool(text) and text not in name)

    @property
    def file_count(self):
        return self._tree.topLevelItemCount()
