from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget,
                               QPushButton, QHBoxLayout, QFileDialog)


class FolderDialog(QDialog):
    def __init__(self, current_folders, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Пользовательские папки")
        self.setMinimumSize(500, 350)
        self._folders = list(current_folders)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        label = QLabel("Добавьте дополнительные папки для поиска файлов:")
        label.setStyleSheet("color: #E8E8F0; font-size: 13px;")
        layout.addWidget(label)

        self._list = QListWidget()
        for folder in self._folders:
            self._list.addItem(folder)
        layout.addWidget(self._list)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        add_btn = QPushButton("+ Добавить папку")
        add_btn.clicked.connect(self._add_folder)
        btn_layout.addWidget(add_btn)

        remove_btn = QPushButton("− Удалить")
        remove_btn.clicked.connect(self._remove_folder)
        btn_layout.addWidget(remove_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        btn_layout2 = QHBoxLayout()
        btn_layout2.setSpacing(8)

        btn_layout2.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout2.addWidget(cancel_btn)

        ok_btn = QPushButton("OK")
        ok_btn.setObjectName("primaryBtn")
        ok_btn.clicked.connect(self.accept)
        btn_layout2.addWidget(ok_btn)

        layout.addLayout(btn_layout2)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if folder:
            self._folders.append(folder)
            self._list.addItem(folder)

    def _remove_folder(self):
        current = self._list.currentRow()
        if current >= 0:
            self._list.takeItem(current)
            self._folders.pop(current)

    def get_folders(self):
        return self._folders
