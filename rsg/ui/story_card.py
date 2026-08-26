"""A single clickable story card in the feed."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ..models import Story


class StoryCard(QFrame):
    clicked = Signal(object)  # emits the Story

    def __init__(self, story: Story):
        super().__init__()
        self.story = story
        self.setObjectName("storyCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("selected", False)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(7)

        # Top row: subreddit badge + meta
        top = QHBoxLayout()
        top.setSpacing(8)
        badge = QLabel(f"r/{story.subreddit}")
        badge.setObjectName("badge")
        top.addWidget(badge)
        top.addStretch(1)
        meta = QLabel(
            f"▲ {self._k(story.score)}   💬 {self._k(story.num_comments)}"
            f"   ·   {story.word_count}w ~{story.read_seconds}s   ·   {story.age}"
        )
        meta.setObjectName("meta")
        top.addWidget(meta)
        root.addLayout(top)

        title = QLabel(story.title)
        title.setObjectName("cardTitle")
        title.setWordWrap(True)
        root.addWidget(title)

        preview = QLabel(story.preview(220))
        preview.setObjectName("cardPreview")
        preview.setWordWrap(True)
        root.addWidget(preview)

    @staticmethod
    def _k(n: int) -> str:
        if n >= 1000:
            return f"{n / 1000:.1f}k".replace(".0k", "k")
        return str(n)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        # Force a style refresh so the [selected="true"] rule applies.
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event) -> None:  # noqa: N802 - Qt override
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.story)
        super().mousePressEvent(event)
