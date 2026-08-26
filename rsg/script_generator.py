"""Generate and persist scripts from stories."""

from __future__ import annotations

import re
from pathlib import Path

from .config import OUTPUT_DIR
from .llm_client import chat
from .models import Story
from .prompts import build_messages


def generate_script(story: Story, settings: dict) -> str:
    messages = build_messages(
        story,
        language=settings.get("language", "English"),
        style=settings.get("script_style", ""),
        target_seconds=int(settings.get("target_seconds", 50)),
    )
    return chat(
        messages,
        model=settings.get("model", "anthropic/claude-3.5-sonnet"),
        temperature=0.8,
        max_tokens=2000,
    )


def _slug(text: str, limit: int = 50) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    text = re.sub(r"[\s_-]+", "-", text)
    return text[:limit].strip("-") or "story"


def save_script(story: Story, script: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{story.subreddit}_{_slug(story.title)}_{story.id}.md"
    path = OUTPUT_DIR / filename
    header = (
        f"# {story.title}\n\n"
        f"- Source: {story.url}\n"
        f"- Subreddit: r/{story.subreddit}\n"
        f"- Score: {story.score} | Comments: {story.num_comments}\n\n"
        f"---\n\n"
    )
    path.write_text(header + script + "\n", encoding="utf-8")
    return path
