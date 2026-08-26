"""Right-hand panel: full story + script generation + output."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..config import LANGUAGES
from ..models import Story
from ..script_generator import save_script


class DetailPanel(QWidget):
    generate_requested = Signal(object)  # emits the Story to generate from

    def __init__(self, settings: dict):
        super().__init__()
        self.settings = settings
        self.story: Story | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        # Header
        self.title = QLabel("Выбери историю слева")
        self.title.setObjectName("detailTitle")
        self.title.setWordWrap(True)
        root.addWidget(self.title)

        meta_row = QHBoxLayout()
        self.meta = QLabel("")
        self.meta.setObjectName("detailMeta")
        meta_row.addWidget(self.meta)
        meta_row.addStretch(1)
        self.open_link = QLabel("")
        self.open_link.setOpenExternalLinks(True)
        self.open_link.setObjectName("detailMeta")
        meta_row.addWidget(self.open_link)
        root.addLayout(meta_row)

        # Original story text
        lbl_story = QLabel("ОРИГИНАЛ ИСТОРИИ")
        lbl_story.setObjectName("sectionTitle")
        root.addWidget(lbl_story)
        self.story_text = QTextBrowser()
        self.story_text.setOpenExternalLinks(True)
        self.story_text.setMinimumHeight(120)
        root.addWidget(self.story_text, stretch=2)

        # Generation controls
        controls = QHBoxLayout()
        controls.setSpacing(8)
        controls.addWidget(QLabel("Язык"))
        self.lang = QComboBox()
        self.lang.addItems(LANGUAGES)
        self.lang.setCurrentText(settings.get("language", "English"))
        self.lang.currentTextChanged.connect(
            lambda v: self.settings.__setitem__("language", v)
        )
        controls.addWidget(self.lang)

        controls.addWidget(QLabel("Длина, сек"))
        self.seconds = QSpinBox()
        self.seconds.setRange(15, 180)
        self.seconds.setSingleStep(5)
        self.seconds.setValue(int(settings.get("target_seconds", 50)))
        self.seconds.valueChanged.connect(
            lambda v: self.settings.__setitem__("target_seconds", v)
        )
        controls.addWidget(self.seconds)
        controls.addStretch(1)

        self.gen_btn = QPushButton("✦ Сгенерировать сценарий")
        self.gen_btn.setObjectName("primary")
        self.gen_btn.setEnabled(False)
        self.gen_btn.clicked.connect(self._on_generate)
        controls.addWidget(self.gen_btn)
        root.addLayout(controls)

        # Output
        out_row = QHBoxLayout()
        lbl_out = QLabel("СЦЕНАРИЙ")
        lbl_out.setObjectName("sectionTitle")
        out_row.addWidget(lbl_out)
        out_row.addStretch(1)
        self.copy_btn = QPushButton("Копировать")
        self.copy_btn.setEnabled(False)
        self.copy_btn.clicked.connect(self._on_copy)
        self.save_btn = QPushButton("Сохранить .md")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._on_save)
        out_row.addWidget(self.copy_btn)
        out_row.addWidget(self.save_btn)
        root.addLayout(out_row)

        self.output = QTextEdit()
        self.output.setPlaceholderText(
            "Здесь появится сценарий: хук, заголовок, текст озвучки, визуальные пометки, хэштеги."
        )
        self.output.setMinimumHeight(140)
        root.addWidget(self.output, stretch=3)

        self._status_cb = None  # set by main window to report to status bar

    # ----- public API ----------------------------------------------------- #
    def set_story(self, story: Story) -> None:
        self.story = story
        self.title.setText(story.title)
        self.meta.setText(
            f"r/{story.subreddit}  ·  ▲ {story.score}  ·  💬 {story.num_comments}"
            f"  ·  {story.word_count} слов  ~{story.read_seconds}с"
        )
        self.open_link.setText(f'<a href="{story.url}" style="color:#7b89ff;">Открыть на Reddit ↗</a>')
        self.story_text.setPlainText(story.selftext)
        self.gen_btn.setEnabled(True)

    def set_generating(self, busy: bool) -> None:
        self.gen_btn.setEnabled(not busy and self.story is not None)
        self.gen_btn.setText("Генерирую…" if busy else "✦ Сгенерировать сценарий")

    def set_script(self, text: str) -> None:
        self.output.setPlainText(text)
        has = bool(text.strip())
        self.copy_btn.setEnabled(has)
        self.save_btn.setEnabled(has)

    # ----- internal -------------------------------------------------------- #
    def _on_generate(self) -> None:
        if self.story is not None:
            self.generate_requested.emit(self.story)

    def _on_copy(self) -> None:
        QGuiApplication.clipboard().setText(self.output.toPlainText())
        if self._status_cb:
            self._status_cb("Сценарий скопирован в буфер обмена.")

    def _on_save(self) -> None:
        if self.story is None:
            return
        path = save_script(self.story, self.output.toPlainText())
        if self._status_cb:
            self._status_cb(f"Сохранено: {path}")
