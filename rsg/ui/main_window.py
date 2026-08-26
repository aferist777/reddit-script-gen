"""Main application window."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QToolBar,
    QWidget,
)

from .. import config
from ..config import SORT_OPTIONS, TIME_OPTIONS, load_settings, save_settings
from ..models import Story
from ..reddit_client import FeedResult
from .detail_panel import DetailPanel
from .feed_widget import FeedWidget
from .settings_dialog import SettingsDialog
from .workers import FetchWorker, GenerateWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reddit Script Gen — истории Reddit → сценарии")
        self.resize(1180, 760)

        self.settings = load_settings()
        self._fetch_worker: FetchWorker | None = None
        self._gen_worker: GenerateWorker | None = None

        self._build_toolbar()

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        self.splitter = QSplitter(Qt.Horizontal, central)
        self.feed = FeedWidget()
        self.detail = DetailPanel(self.settings)
        self.detail._status_cb = self.status
        self.splitter.addWidget(self.feed)
        self.splitter.addWidget(self.detail)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 4)
        self.splitter.setSizes([460, 720])

        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.splitter)

        self.feed.story_selected.connect(self.detail.set_story)
        self.detail.generate_requested.connect(self._on_generate)

        self.setStatusBar(self.statusBar())
        if not config.get_api_key():
            self.status("⚠ Нет OPENROUTER_API_KEY — лента работает, но генерация выключена. См. .env.example.")
        else:
            self.status("Готово.")

        self.refresh_feed()

    # ----- toolbar --------------------------------------------------------- #
    def _build_toolbar(self) -> None:
        bar = QToolBar()
        bar.setMovable(False)
        self.addToolBar(bar)

        bar.addWidget(QLabel("  Сортировка "))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(SORT_OPTIONS)
        self.sort_combo.setCurrentText(self.settings.get("sort", "top"))
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        bar.addWidget(self.sort_combo)

        bar.addWidget(QLabel("  Период "))
        self.time_combo = QComboBox()
        self.time_combo.addItems(TIME_OPTIONS)
        self.time_combo.setCurrentText(self.settings.get("time_filter", "week"))
        self.time_combo.currentTextChanged.connect(
            lambda v: self.settings.__setitem__("time_filter", v)
        )
        bar.addWidget(self.time_combo)
        self._sync_time_enabled()

        self.refresh_btn = QPushButton("⟳ Обновить")
        self.refresh_btn.clicked.connect(self.refresh_feed)
        bar.addWidget(self.refresh_btn)

        settings_btn = QPushButton("⚙ Настройки")
        settings_btn.clicked.connect(self._open_settings)
        bar.addWidget(settings_btn)

        from PySide6.QtWidgets import QSizePolicy
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bar.addWidget(spacer)

        self.source_label = QLabel("")
        self.source_label.setObjectName("sourceLabel")
        bar.addWidget(self.source_label)
        bar.addWidget(QLabel("  "))

    def _on_sort_changed(self, value: str) -> None:
        self.settings["sort"] = value
        self._sync_time_enabled()

    def _sync_time_enabled(self) -> None:
        self.time_combo.setEnabled(self.sort_combo.currentText() == "top")

    # ----- feed ------------------------------------------------------------ #
    def refresh_feed(self) -> None:
        if self._fetch_worker and self._fetch_worker.isRunning():
            return
        self.refresh_btn.setEnabled(False)
        self.feed.show_message("Загрузка ленты…")
        self.status("Тяну истории из Reddit…")
        self._fetch_worker = FetchWorker(self.settings)
        self._fetch_worker.done.connect(self._on_feed_done)
        self._fetch_worker.failed.connect(self._on_feed_failed)
        self._fetch_worker.start()

    def _on_feed_done(self, result: FeedResult) -> None:
        self.refresh_btn.setEnabled(True)
        self.feed.set_stories(result.stories)
        self.source_label.setText(f"Источник: {result.source}")
        note = f"  ({'; '.join(result.errors)})" if result.errors else ""
        self.status(f"Загружено историй: {len(result.stories)}{note}")

    def _on_feed_failed(self, message: str) -> None:
        self.refresh_btn.setEnabled(True)
        self.feed.show_message(f"Не удалось загрузить ленту:\n{message}")
        self.status(f"Ошибка загрузки: {message}")

    # ----- generation ------------------------------------------------------ #
    def _on_generate(self, story: Story) -> None:
        if not config.get_api_key():
            self.detail.set_script(
                "Нет OPENROUTER_API_KEY.\n\n"
                "1. Скопируй .env.example в .env\n"
                "2. Впиши свой ключ OpenRouter\n"
                "3. Перезапусти приложение."
            )
            self.status("Генерация недоступна: нет API-ключа.")
            return
        if self._gen_worker and self._gen_worker.isRunning():
            return
        self.detail.set_generating(True)
        self.status(f"Генерирую сценарий ({self.settings.get('model')})…")
        self._gen_worker = GenerateWorker(story, self.settings)
        self._gen_worker.done.connect(self._on_gen_done)
        self._gen_worker.failed.connect(self._on_gen_failed)
        self._gen_worker.start()

    def _on_gen_done(self, script: str) -> None:
        self.detail.set_generating(False)
        self.detail.set_script(script)
        self.status("Сценарий готов.")

    def _on_gen_failed(self, message: str) -> None:
        self.detail.set_generating(False)
        self.detail.set_script(f"Ошибка генерации:\n\n{message}")
        self.status(f"Ошибка генерации: {message}")

    # ----- settings -------------------------------------------------------- #
    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.settings.update(dialog.updated_settings())
            save_settings(self.settings)
            self.status("Настройки сохранены.")
            self.refresh_feed()

    def status(self, text: str) -> None:
        self.statusBar().showMessage(text)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
        save_settings(self.settings)
        for w in (self._fetch_worker, self._gen_worker):
            if w and w.isRunning():
                w.wait(1500)
        super().closeEvent(event)
