"""Scrollable feed of story cards."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from ..models import Story
from .story_card import StoryCard


class FeedWidget(QScrollArea):
    story_selected = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.vbox = QVBoxLayout(self.container)
        self.vbox.setContentsMargins(12, 12, 12, 12)
        self.vbox.setSpacing(10)
        self.vbox.setAlignment(Qt.AlignTop)
        self.setWidget(self.container)

        self._cards: list[StoryCard] = []
        self._placeholder = QLabel("Загрузка ленты…")
        self._placeholder.setObjectName("placeholder")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setWordWrap(True)
        self.vbox.addWidget(self._placeholder)

    def _clear(self) -> None:
        while self.vbox.count():
            item = self.vbox.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        self._cards = []

    def show_message(self, text: str) -> None:
        self._clear()
        self._placeholder = QLabel(text)
        self._placeholder.setObjectName("placeholder")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setWordWrap(True)
        self.vbox.addWidget(self._placeholder)

    def set_stories(self, stories: list[Story]) -> None:
        self._clear()
        if not stories:
            self.show_message("Ничего не найдено. Попробуй другие сабреддиты\nили смягчи фильтры в настройках.")
            return
        for story in stories:
            card = StoryCard(story)
            card.clicked.connect(self._on_card_clicked)
            self.vbox.addWidget(card)
            self._cards.append(card)
        self.vbox.addStretch(1)
        self.verticalScrollBar().setValue(0)

    def _on_card_clicked(self, story: Story) -> None:
        for card in self._cards:
            card.set_selected(card.story is story)
        self.story_selected.emit(story)
