"""Dark theme stylesheet."""

DARK_QSS = """
* {
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
    color: #e6e8ee;
}
QMainWindow, QWidget#central, QDialog {
    background: #0f1115;
}
QToolBar {
    background: #161922;
    border: none;
    border-bottom: 1px solid #232838;
    padding: 6px 8px;
    spacing: 8px;
}
QToolBar QLabel { color: #828aa0; font-size: 12px; }
QLabel#sourceLabel { color: #8b93a7; font-size: 12px; }
QLabel#sectionTitle {
    color: #8b93a7;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Buttons */
QPushButton {
    background: #232838;
    border: 1px solid #2e3447;
    border-radius: 8px;
    padding: 7px 14px;
    color: #e6e8ee;
}
QPushButton:hover { background: #2c3245; }
QPushButton:pressed { background: #202533; }
QPushButton:disabled { color: #5a6175; background: #1a1d27; }
QPushButton#primary {
    background: #5b6cff;
    border: 1px solid #6a79ff;
    font-weight: 600;
}
QPushButton#primary:hover { background: #6b7aff; }
QPushButton#primary:disabled { background: #2c3350; border-color: #2c3350; color: #7079a0; }

/* Inputs */
QComboBox, QSpinBox, QLineEdit, QPlainTextEdit, QListWidget {
    background: #161922;
    border: 1px solid #2e3447;
    border-radius: 7px;
    padding: 5px 8px;
    selection-background-color: #5b6cff;
}
QComboBox:hover, QSpinBox:hover, QLineEdit:hover { border-color: #3a4159; }
QComboBox::drop-down { border: none; width: 18px; }
QComboBox QAbstractItemView {
    background: #161922;
    border: 1px solid #2e3447;
    selection-background-color: #5b6cff;
    outline: none;
}
QCheckBox { spacing: 8px; }

/* Story cards */
QFrame#storyCard {
    background: #161922;
    border: 1px solid #232838;
    border-radius: 12px;
}
QFrame#storyCard:hover { border: 1px solid #3a4159; background: #1a1e29; }
QFrame#storyCard[selected="true"] {
    border: 1px solid #5b6cff;
    background: #1b2030;
}
QLabel#cardTitle { font-size: 14px; font-weight: 600; color: #f2f4fa; }
QLabel#cardPreview { color: #9aa2b6; font-size: 12px; }
QLabel#badge {
    background: #2a3550;
    color: #aeb9ff;
    border-radius: 6px;
    padding: 2px 7px;
    font-size: 11px;
    font-weight: 600;
}
QLabel#meta { color: #828aa0; font-size: 11px; }

/* Detail */
QTextBrowser, QTextEdit {
    background: #12151c;
    border: 1px solid #232838;
    border-radius: 10px;
    padding: 10px;
}
QLabel#detailTitle { font-size: 17px; font-weight: 700; color: #f2f4fa; }
QLabel#detailMeta { color: #828aa0; font-size: 12px; }
QLabel#placeholder { color: #5a6175; font-size: 14px; }

/* Scrollbars */
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #2e3447; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #3a4159; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
QScrollArea { border: none; }
QStatusBar { background: #161922; color: #828aa0; border-top: 1px solid #232838; }
QSplitter::handle { background: #232838; width: 2px; }
"""
