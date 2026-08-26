"""Background QThread workers so the UI never freezes on network calls."""

from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from .. import reddit_client as rc
from ..models import Story
from ..script_generator import generate_script


class FetchWorker(QThread):
    done = Signal(object)   # FeedResult (already filtered)
    failed = Signal(str)

    def __init__(self, settings: dict):
        super().__init__()
        self.settings = dict(settings)

    def run(self) -> None:
        try:
            s = self.settings
            result = rc.fetch_feed(
                s["subreddits"],
                sort=s["sort"],
                time_filter=s["time_filter"],
                limit=int(s["limit"]),
            )
            result.stories = rc.apply_filters(
                result.stories,
                min_words=int(s["min_words"]),
                max_words=int(s["max_words"]),
                hide_nsfw=bool(s["hide_nsfw"]),
                sort_by="score",
            )
            self.done.emit(result)
        except Exception as exc:  # noqa: BLE001 - surface any failure to the UI
            self.failed.emit(str(exc))


class GenerateWorker(QThread):
    done = Signal(str)
    failed = Signal(str)

    def __init__(self, story: Story, settings: dict):
        super().__init__()
        self.story = story
        self.settings = dict(settings)

    def run(self) -> None:
        try:
            self.done.emit(generate_script(self.story, self.settings))
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))
