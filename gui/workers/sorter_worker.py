import os
import shutil

from PySide6.QtCore import QObject, Signal, QThread

from config import get_standard_folders, get_search_folders, TYPE_FOLDER_MAP
from file_utils import check_extension_match

BATCH_SIZE = 500


class SorterWorker(QObject):
    progress = Signal(int, int)
    status = Signal(str)
    file_moved = Signal(str)
    file_error = Signal(str)
    log_message = Signal(str, str)
    preview_batch = Signal(list)
    preview_ready = Signal(list)
    finished = Signal(int, int, int)

    def __init__(self, extensions, dry_run=False):
        super().__init__()
        self.extensions = extensions
        self._is_running = True
        self.dry_run = dry_run
        self.folders = get_standard_folders()

    def stop(self):
        self._is_running = False

    def scan_for_preview(self, type_key, folders=None, extra_folders=None):
        folders = self.folders if folders is None else folders
        dest_key = TYPE_FOLDER_MAP[type_key]
        dest_folder = folders[dest_key]
        search_folders = get_search_folders(folders, dest_folder)
        if extra_folders:
            search_folders.extend(f for f in extra_folders if f != dest_folder and f not in search_folders)
        ext_set = {e.lower() for e in self.extensions[type_key]}

        results = []
        for folder in search_folders:
            if not os.path.exists(folder) or not os.path.isdir(folder):
                continue
            if folder == dest_folder:
                continue
            try:
                with os.scandir(folder) as entries:
                    for entry in entries:
                        if not entry.is_file() or entry.name.startswith("."):
                            continue
                        if check_extension_match(entry.name, ext_set):
                            results.append({
                                "name": entry.name,
                                "path": entry.path,
                                "size": entry.stat().st_size,
                                "folder": folder,
                            })
                            if len(results) % BATCH_SIZE == 0:
                                self.preview_batch.emit(results[-BATCH_SIZE:])
            except PermissionError:
                continue

        self.preview_ready.emit(results)

    def run_sort(self, type_key, checked_files, folders=None, extra_folders=None):
        self._is_running = True
        folders = self.folders if folders is None else folders
        dest_key = TYPE_FOLDER_MAP[type_key]
        dest_folder = folders[dest_key]

        total = len(checked_files)
        moved = 0
        errors = 0

        if total == 0:
            self.log_message.emit("Нет файлов для сортировки", "info")
            self.finished.emit(0, 0, 0)
            return

        os.makedirs(dest_folder, exist_ok=True)

        used_names = {f["name"] for f in checked_files}

        def resolve_dest(file_info):
            source_path = file_info["path"]
            filename = file_info["name"]
            dest = os.path.join(dest_folder, filename)
            if not os.path.exists(dest):
                return source_path, filename, dest
            base, ext = os.path.splitext(filename)
            counter = 1
            while True:
                name = f"{base} ({counter}){ext}"
                dest = os.path.join(dest_folder, name)
                if not os.path.exists(dest) and name not in used_names:
                    used_names.add(name)
                    break
                counter += 1
            return source_path, filename, dest

        def move_file(args):
            source_path, filename, dest_path = args
            if self.dry_run:
                self.log_message.emit(f"  → Будет перемещён: {filename}", "info")
                self.file_moved.emit(filename)
                QThread.msleep(50)
                return 1, 0
            try:
                shutil.move(source_path, dest_path)
                self.log_message.emit(f"  ✓ Перемещён: {filename}", "success")
                self.file_moved.emit(filename)
                return 1, 0
            except (OSError, shutil.Error) as e:
                self.log_message.emit(f"  ✗ Ошибка: {filename} — {e}", "error")
                self.file_error.emit(filename)
                return 0, 1

        resolved = [resolve_dest(f) for f in checked_files]
        total = len(resolved)

        if total == 1:
            moved, errors = move_file(resolved[0])
        else:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            with ThreadPoolExecutor(max_workers=min(os.cpu_count() or 4, 4)) as executor:
                futures = {executor.submit(move_file, args): args for args in resolved}
                for idx, future in enumerate(as_completed(futures)):
                    if not self._is_running:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    self.progress.emit(idx + 1, total)
                    dm, de = future.result()
                    moved += dm
                    errors += de

        self.progress.emit(total, total)
        self.finished.emit(moved, errors, total)
