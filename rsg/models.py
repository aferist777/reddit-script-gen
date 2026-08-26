"""Data models for Reddit stories."""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class Story:
    """A single self-post story pulled from Reddit."""

    id: str
    subreddit: str
    title: str
    selftext: str
    author: str
    score: int
    num_comments: int
    upvote_ratio: float
    created_utc: float
    permalink: str
    over_18: bool = False

    @property
    def url(self) -> str:
        return f"https://www.reddit.com{self.permalink}"

    @property
    def word_count(self) -> int:
        return len(self.selftext.split())

    @property
    def read_seconds(self) -> int:
        """Rough narration length at ~150 wpm."""
        return round(self.word_count / 150 * 60)

    @property
    def age(self) -> str:
        """Human-readable age, e.g. '3h', '2d'."""
        delta = max(0, time.time() - self.created_utc)
        if delta < 3600:
            return f"{int(delta // 60)}m"
        if delta < 86400:
            return f"{int(delta // 3600)}h"
        return f"{int(delta // 86400)}d"

    def preview(self, length: int = 280) -> str:
        text = " ".join(self.selftext.split())
        if len(text) <= length:
            return text
        return text[:length].rstrip() + "…"

    @classmethod
    def from_json(cls, data: dict) -> "Story":
        sub = data.get("subreddit", "") or ""
        post_id = data.get("id", "") or ""
        permalink = data.get("permalink", "") or ""
        if not permalink and sub and post_id:
            permalink = f"/r/{sub}/comments/{post_id}/"
        return cls(
            id=post_id,
            subreddit=sub,
            title=data.get("title", ""),
            selftext=(data.get("selftext") or "").strip(),
            author=data.get("author", "") or "[unknown]",
            score=int(data.get("score", 0) or 0),
            num_comments=int(data.get("num_comments", 0) or 0),
            upvote_ratio=float(data.get("upvote_ratio", 0.0) or 0.0),
            created_utc=float(data.get("created_utc", 0.0) or 0.0),
            permalink=permalink,
            over_18=bool(data.get("over_18", False)),
        )
