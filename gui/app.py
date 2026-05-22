import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QPushButton, QLabel, QProgressBar, QMessageBox,
    QApplication, QSplitter, QSizePolicy, QMenu,
)
from PySide6.QtCore import Qt, QThread, Slot, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QAction, QFont

from config import get_standard_folders, TYPE_FOLDER_MAP, TYPE_NAMES
from gui.widgets.title_bar import TitleBar
from gui.widgets.type_selector import TypeSelector
from gui.widgets.preview_table import PreviewTable
from gui.widgets.log_widget import LogWidget
from gui.widgets.statistics_panel import StatisticsPanel
from gui.workers.sorter_worker import SorterWorker
from gui.dialogs.about_dialog import AboutDialog
from gui.dialogs.folder_dialog import FolderDialog

STYLE_PATH = os.path.join(os.path.dirname(__file__), "resources", "style.qss")


class MainWindow(QMainWindow):
    def __init__(self, extensions):
        super().__init__()
        self.extensions = extensions
        self.folders = get_standard_folders()
        self._custom_folders = None
        self._worker = None
        self._thread = None
        self._is_dark_theme = True
        self._total_size = 0

        self.setWindowTitle("File Sorter")
        self.setMinimumSize(800, 520)
        self.resize(960, 640)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self._build_ui()
        self._load_style()

    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # TitleBar
        self._titlebar = TitleBar(self)
        self._titlebar.minimize_clicked.connect(self.showMinimized)
        self._titlebar.close_clicked.connect(self.close)
        root.addWidget(self._titlebar)

        # Menu bar (hidden, actions via TitleBar context menu)
        self._build_actions()

        # Three-column body
        body = QSplitter(Qt.Horizontal)
        body.setHandleWidth(1)
        body.setChildrenCollapsible(False)

        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_center())
        body.addWidget(self._build_right_panel())

        body.setSizes([200, 400, 240])
        body.setStretchFactor(0, 0)
        body.setStretchFactor(1, 1)
        body.setStretchFactor(2, 0)
        root.addWidget(body, stretch=1)

        # Bottom bar
        root.addWidget(self._build_bottom_bar())

        central = QWidget()
        central.setObjectName("centralWidget")
        central.setLayout(root)
        self.setCentralWidget(central)

    def _build_actions(self):
        self._dry_run_action = QAction("Сухой прогон (без перемещения)", self)
        self._dry_run_action.setCheckable(True)

        self._theme_action = QAction("Светлая тема", self)
        self._theme_action.setCheckable(True)
        self._theme_action.triggered.connect(self._toggle_theme)

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(4)

        # Type selector
        self._type_selector = TypeSelector()
        self._type_selector.type_changed.connect(self._on_type_changed)
        layout.addWidget(self._type_selector)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #2A2A32;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)
        layout.addSpacing(8)

        # Folders section
        folders_title = QLabel("ПАПКИ НАЗНАЧЕНИЯ")
        folders_title.setObjectName("sectionTitle")
        layout.addWidget(folders_title)

        self._folder_labels = {}
        for key in ("videos", "pictures", "documents", "music", "downloads"):
            lbl = QLabel(self._shorten_path(self.folders.get(key, "")))
            lbl.setObjectName("folderDest")
            lbl.setCursor(Qt.PointingHandCursor)
            lbl.setToolTip(self.folders.get(key, ""))
            self._folder_labels[key] = lbl
            layout.addWidget(lbl)

        layout.addSpacing(8)

        self._add_folders_btn = QPushButton("+ Свои папки")
        self._add_folders_btn.setObjectName("outlineBtn")
        self._add_folders_btn.clicked.connect(self._open_folder_dialog)
        layout.addWidget(self._add_folders_btn)

        layout.addStretch()
        return sidebar

    def _build_center(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 16, 0, 12)
        layout.setSpacing(0)

        self._preview = PreviewTable()
        self._preview.selection_changed.connect(self._on_selection_changed)
        layout.addWidget(self._preview, stretch=1)

        return container

    def _build_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)

        self._stats = StatisticsPanel()
        layout.addWidget(self._stats)

        self._log = LogWidget()
        layout.addWidget(self._log, stretch=1)

        return panel

    def _build_bottom_bar(self):
        bar = QFrame()
        bar.setObjectName("bottomBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        self._status_label = QLabel("Готов к работе")
        self._status_label.setObjectName("statusText")
        layout.addWidget(self._status_label)

        self._progress = QProgressBar()
        self._progress.setFixedHeight(4)
        self._progress.setFixedWidth(200)
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        layout.addStretch()

        self._scan_btn = QPushButton("Сканировать")
        self._scan_btn.setObjectName("scanBtn")
        self._scan_btn.clicked.connect(self._scan_files)
        layout.addWidget(self._scan_btn)

        self._sort_btn = QPushButton("Сортировать")
        self._sort_btn.setObjectName("sortBtn")
        self._sort_btn.clicked.connect(self._start_sort)
        self._sort_btn.setEnabled(False)
        layout.addWidget(self._sort_btn)

        self._cancel_btn = QPushButton("Отмена")
        self._cancel_btn.setObjectName("cancelBtn")
        self._cancel_btn.clicked.connect(self._cancel_sort)
        self._cancel_btn.setVisible(False)
        layout.addWidget(self._cancel_btn)

        return bar

    def _load_style(self):
        if os.path.exists(STYLE_PATH):
            with open(STYLE_PATH, encoding="utf-8") as f:
                qss = f.read()
            self.setStyleSheet(qss)

    def _toggle_theme(self):
        self._is_dark_theme = not self._is_dark_theme
        if self._is_dark_theme:
            self._theme_action.setText("Светлая тема")
            self.setProperty("theme", None)
        else:
            self._theme_action.setText("Тёмная тема")
            self.setProperty("theme", "light")
        self._load_style()

    def _shorten_path(self, path):
        home = os.path.expanduser("~")
        return path.replace(home, "~") if path.startswith(home) else path

    def _update_folder_labels(self, type_key):
        dest_key = TYPE_FOLDER_MAP.get(type_key)
        if not dest_key:
            return
        for key, lbl in self._folder_labels.items():
            path = self.folders.get(key, "")
            lbl.setText(self._shorten_path(path))
            if key == dest_key:
                lbl.setStyleSheet("color: #4F6EF7; font-size: 11px; padding: 2px 0;")
            else:
                lbl.setStyleSheet("color: #8888A0; font-size: 11px; padding: 2px 0;")

    # ── Slots ─────────────────────────────────

    @Slot(str)
    def _on_type_changed(self, type_key):
        self._preview.clear_data()
        self._sort_btn.setEnabled(False)
        self._status_label.setText("Готов к работе")
        self._stats.reset()
        self._update_folder_labels(type_key)

    @Slot(int)
    def _on_selection_changed(self, count):
        self._sort_btn.setEnabled(count > 0)

    @Slot()
    def _scan_files(self):
        type_key = self._type_selector.selected_key()
        self._preview.clear_data()
        self._stats.reset()
        self._status_label.setText("Сканирование...")
        self._log.log(f"Сканирование {TYPE_NAMES[type_key]}...", "info")
        self._total_size = 0

        extra = self._custom_folders

        worker = SorterWorker(self.extensions)
        worker.preview_ready.connect(self._on_preview_ready)
        worker.log_message.connect(self._log.log)
        worker.preview_ready.connect(lambda: thread.quit())

        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(lambda: worker.scan_for_preview(type_key, self.folders, extra))
        thread.finished.connect(thread.deleteLater)
        thread.start()

    @Slot(list)
    def _on_preview_ready(self, files):
        self._preview.set_files(files)
        self._sort_btn.setEnabled(len(files) > 0)

        total_size = sum(f.get("size", 0) for f in files)
        self._total_size = total_size
        self._stats.set_found(len(files), total_size)
        self._stats.set_selected(len(files))

        count = len(files)
        self._type_selector.set_count(
            self._type_selector.selected_key(), count
        )

        self._status_label.setText(
            f"Найдено {count} файлов" if files else "Файлы не найдены"
        )
        self._log.log(
            f"Сканирование завершено: найдено {count} файлов",
            "success" if files else "info",
        )

    @Slot()
    def _start_sort(self):
        type_key = self._type_selector.selected_key()
        checked = self._preview.checked_files()
        if not checked:
            QMessageBox.information(self, "Сортировка", "Нет выбранных файлов для сортировки.")
            return

        self._scan_btn.setEnabled(False)
        self._sort_btn.setVisible(False)
        self._cancel_btn.setVisible(True)
        self._progress.setVisible(True)
        self._progress.setValue(0)
        self._status_label.setText("Сортировка...")

        dry_run = self._dry_run_action.isChecked()
        extra = self._custom_folders

        self._thread = QThread()
        self._worker = SorterWorker(self.extensions, dry_run=dry_run)
        self._worker.moveToThread(self._thread)

        self._worker.progress.connect(self._on_sort_progress)
        self._worker.status.connect(self._status_label.setText)
        self._worker.log_message.connect(self._log.log)
        self._worker.finished.connect(self._on_sort_finished)

        self._thread.started.connect(
            lambda: self._worker.run_sort(type_key, checked, self.folders, extra)
        )
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    @Slot(int, int)
    def _on_sort_progress(self, current, total):
        self._progress.setMaximum(total)
        self._progress.setValue(current)

    @Slot(int, int, int)
    def _on_sort_finished(self, moved, errors, total):
        self._thread.quit()
        self._thread.wait()
        self._thread = None
        self._worker = None

        self._scan_btn.setEnabled(True)
        self._sort_btn.setVisible(True)
        self._cancel_btn.setVisible(False)
        self._progress.setVisible(False)

        self._stats.set_moved(moved)

        self._status_label.setStyleSheet(
            "color: #3DD68C; font-size: 12px;" if errors == 0
            else "color: #F75F5F; font-size: 12px;"
        )
        self._status_label.setText(f"Готово: перемещено {moved}, ошибок {errors}")

        self._log.log(f"{'='*40}", "info")
        self._log.log(
            f"Завершено: перемещено {moved}, ошибок {errors}",
            "success" if errors == 0 else "error",
        )

        # Animate sort button flash
        self._animate_sort_button(moved)

    def _animate_sort_button(self, moved):
        original_text = self._sort_btn.text()
        self._sort_btn.setText("✓ Готово")
        self._sort_btn.setStyleSheet(
            "background-color: #3DD68C; border: none; border-radius: 8px;"
            "color: #FFFFFF; font-size: 13px; font-weight: 600;"
            "min-width: 120px; min-height: 36px;"
        )
        QTimer.singleShot(2000, lambda: self._restore_sort_button(original_text))

    def _restore_sort_button(self, original_text):
        self._sort_btn.setText(original_text)
        self._sort_btn.setStyleSheet("")

    @Slot()
    def _cancel_sort(self):
        if self._worker:
            self._worker.stop()
            self._log.log("Отмена сортировки...", "warning")

    # ── Dialogs ───────────────────────────────

    def _open_folder_dialog(self):
        current = list(self.folders.values())
        dialog = FolderDialog(current, self)
        if dialog.exec():
            result = dialog.get_folders()
            extra = [p for p in result if p not in self.folders.values()]
            self._custom_folders = extra if extra else None
            if extra:
                self._status_label.setText(f"Добавлено папок: {len(extra)}")

    def _show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        dry = menu.addAction("Сухой прогон")
        dry.setCheckable(True)
        dry.setChecked(self._dry_run_action.isChecked())
        dry.triggered.connect(self._dry_run_action.setChecked)

        menu.addSeparator()
        theme = menu.addAction("Светлая тема")
        theme.setCheckable(True)
        theme.setChecked(not self._is_dark_theme)
        theme.triggered.connect(self._toggle_theme)

        menu.addSeparator()
        about = menu.addAction("О программе")
        about.triggered.connect(self._show_about)

        menu.addSeparator()
        exit_action = menu.addAction("Выход")
        exit_action.triggered.connect(self.close)

        menu.exec(event.globalPos())


def run_gui(extensions):
    app = QApplication.instance() or QApplication([])
    window = MainWindow(extensions)
    window.show()
    app.exec()
