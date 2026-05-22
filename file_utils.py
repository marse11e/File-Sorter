import os
import shutil


def get_file_extension(filename):
    if not filename or "." not in filename:
        return ""
    filename = filename.strip()
    _, ext = os.path.splitext(filename)
    ext = ext.lstrip(".").lower()
    return ext


def check_extension_match(filename, extensions_set):
    ext = get_file_extension(filename)
    return ext in extensions_set


def move_file_safely(source_path, destination_dir):
    try:
        if not os.path.exists(source_path) or not os.path.isfile(source_path):
            return False
        os.makedirs(destination_dir, exist_ok=True)
        filename = os.path.basename(source_path)
        destination_path = os.path.join(destination_dir, filename)

        if os.path.exists(destination_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(destination_path):
                new_filename = f"{base} ({counter}){ext}"
                destination_path = os.path.join(destination_dir, new_filename)
                counter += 1

        shutil.move(source_path, destination_path)
        return True
    except (OSError, shutil.Error) as e:
        print(f"Ошибка при перемещении {source_path}: {e}")
        return False


def find_and_move_files(source_folders, destination_folder, extensions, file_type_name, on_progress=None):
    moved_count = 0
    error_count = 0
    ext_set = {e.lower() for e in extensions}

    print(f"\nОбработка {file_type_name}...")

    for source_folder in source_folders:
        if source_folder == destination_folder:
            continue
        if not os.path.exists(source_folder) or not os.path.isdir(source_folder):
            continue

        try:
            with os.scandir(source_folder) as entries:
                for entry in entries:
                    if not entry.is_file() or entry.name.startswith("."):
                        continue
                    if check_extension_match(entry.name, ext_set):
                        source_path = entry.path
                        if move_file_safely(source_path, destination_folder):
                            moved_count += 1
                            msg = f"  ✓ Перемещен: {entry.name}"
                            print(msg)
                            if on_progress:
                                on_progress(msg)
                        else:
                            error_count += 1
                            msg = f"  ✗ Ошибка: {entry.name}"
                            print(msg)
                            if on_progress:
                                on_progress(msg)
        except PermissionError:
            msg = f"  ✗ Нет доступа к папке: {source_folder}"
            print(msg)
            error_count += 1
            if on_progress:
                on_progress(msg)
        except Exception as e:
            msg = f"  ✗ Ошибка при обработке {source_folder}: {e}"
            print(msg)
            error_count += 1
            if on_progress:
                on_progress(msg)

    print(f"\n{file_type_name}: перемещено {moved_count}, ошибок {error_count}")
    return moved_count, error_count
