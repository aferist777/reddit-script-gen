"""Settings dialog: subreddits, model, filters."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from ..config import MODEL_SUGGESTIONS, SUBREDDIT_CATALOGUE


class SettingsDialog(QDialog):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(420)
        self._settings = settings

        root = QVBoxLayout(self)
        root.setSpacing(12)

        # --- Subreddits ---------------------------------------------------- #
        root.addWidget(self._section("Сабреддиты"))
        self.sub_list = QListWidget()
        self.sub_list.setMaximumHeight(220)
        selected = set(settings.get("subreddits", []))
        catalogue = list(dict.fromkeys(SUBREDDIT_CATALOGUE + list(selected)))
        for name in catalogue:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if name in selected else Qt.Unchecked)
            self.sub_list.addItem(item)
        root.addWidget(self.sub_list)

        add_row = QHBoxLayout()
        self.add_edit = QLineEdit()
        self.add_edit.setPlaceholderText("Добавить сабреддит (без r/)…")
        self.add_edit.returnPressed.connect(self._add_custom)
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self._add_custom)
        add_row.addWidget(self.add_edit)
        add_row.addWidget(add_btn)
        root.addLayout(add_row)

        # --- Model & filters ---------------------------------------------- #
        root.addWidget(self._section("Генерация и фильтры"))
        form = QFormLayout()
        form.setSpacing(8)

        self.model = QComboBox()
        self.model.setEditable(True)
        self.model.addItems(MODEL_SUGGESTIONS)
        self.model.setCurrentText(settings.get("model", MODEL_SUGGESTIONS[0]))
        form.addRow("Модель (OpenRouter)", self.model)

        self.limit = QSpinBox()
        self.limit.setRange(5, 100)
        self.limit.setValue(int(settings.get("limit", 50)))
        form.addRow("Сколько тянуть", self.limit)

        self.min_words = QSpinBox()
        self.min_words.setRange(0, 2000)
        self.min_words.setSingleStep(10)
        self.min_words.setValue(int(settings.get("min_words", 90)))
        form.addRow("Мин. слов в истории", self.min_words)

        self.max_words = QSpinBox()
        self.max_words.setRange(100, 10000)
        self.max_words.setSingleStep(100)
        self.max_words.setValue(int(settings.get("max_words", 1200)))
        form.addRow("Макс. слов в истории", self.max_words)

        self.hide_nsfw = QCheckBox("Скрывать NSFW (18+)")
        self.hide_nsfw.setChecked(bool(settings.get("hide_nsfw", True)))
        form.addRow("", self.hide_nsfw)

        root.addLayout(form)

        # --- Buttons ------------------------------------------------------- #
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    @staticmethod
    def _section(text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setObjectName("sectionTitle")
        return lbl

    def _add_custom(self) -> None:
        name = self.add_edit.text().strip().lstrip("/").removeprefix("r/").strip()
        if not name:
            return
        # Avoid duplicates.
        for i in range(self.sub_list.count()):
            if self.sub_list.item(i).text().lower() == name.lower():
                self.sub_list.item(i).setCheckState(Qt.Checked)
                self.add_edit.clear()
                return
        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        self.sub_list.insertItem(0, item)
        self.add_edit.clear()

    def updated_settings(self) -> dict:
        subs = [
            self.sub_list.item(i).text()
            for i in range(self.sub_list.count())
            if self.sub_list.item(i).checkState() == Qt.Checked
        ]
        result = dict(self._settings)
        result.update(
            {
                "subreddits": subs or self._settings.get("subreddits", []),
                "model": self.model.currentText().strip(),
                "limit": self.limit.value(),
                "min_words": self.min_words.value(),
                "max_words": self.max_words.value(),
                "hide_nsfw": self.hide_nsfw.isChecked(),
            }
        )
        return result
