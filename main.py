#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа для сортировки файлов по типам
Автор: github.com/marse11e
"""

import os
import sys
from config import load_extensions

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 не установлен. Установите: pip install PySide6", file=sys.stderr)
    sys.exit(1)


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    extensions = load_extensions(os.path.join(base, "extensions.json"))
    from gui.app import run_gui
    run_gui(extensions)


if __name__ == "__main__":
    main()
