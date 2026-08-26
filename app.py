"""Reddit Script Gen — entry point.

Run with:  python app.py
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from rsg.ui.main_window import MainWindow
from rsg.ui.theme import DARK_QSS


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Reddit Script Gen")
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_QSS)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
