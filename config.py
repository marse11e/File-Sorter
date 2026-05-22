import json
import os
from pathlib import Path


def load_extensions(path="extensions.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_standard_folders():
    home = os.path.expanduser("~")
    return {
        "videos": os.path.join(home, "Videos"),
        "documents": os.path.join(home, "Documents"),
        "downloads": os.path.join(home, "Downloads"),
        "pictures": os.path.join(home, "Pictures"),
        "music": os.path.join(home, "Music"),
        "desktop": os.path.join(home, "Desktop"),
        "templates": os.path.join(home, "Templates"),
        "home": home,
    }


def get_search_folders(folders, exclude=None):
    return [v for k, v in folders.items() if v != exclude]


TYPE_FOLDER_MAP = {
    "photo": "pictures",
    "video": "videos",
    "document": "documents",
    "music": "music",
    "archive": "downloads",
}

TYPE_NAMES = {
    "photo": "Изображения",
    "video": "Видео",
    "document": "Документы",
    "music": "Музыка",
    "archive": "Архивы",
}
