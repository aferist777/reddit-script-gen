"""Configuration, defaults and settings persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = APP_DIR / "data"
SETTINGS_PATH = DATA_DIR / "settings.json"
OUTPUT_DIR = APP_DIR / "scripts"

load_dotenv(APP_DIR / ".env")

# Curated story subreddits — TIFU and friends.
DEFAULT_SUBREDDITS = [
    "tifu",
    "AmItheAsshole",
    "relationship_advice",
    "MaliciousCompliance",
    "pettyrevenge",
    "ProRevenge",
    "EntitledParents",
    "TrueOffMyChest",
    "confession",
    "TalesFromRetail",
]

# A broader catalogue the settings dialog offers as toggles.
SUBREDDIT_CATALOGUE = DEFAULT_SUBREDDITS + [
    "offmychest",
    "ChoosingBeggars",
    "IDontWorkHereLady",
    "nosleep",
    "AmITheDevil",
    "BestofRedditorUpdates",
    "JUSTNOMIL",
    "pettyrevenge",
    "Glitch_in_the_Matrix",
    "self",
]

SORT_OPTIONS = ["hot", "top", "new", "rising"]
TIME_OPTIONS = ["hour", "day", "week", "month", "year", "all"]
LANGUAGES = ["English", "Russian", "Spanish", "German", "French", "Portuguese"]

SCRIPT_STYLES = [
    "Short-form narration (Reels / Shorts / TikTok)",
    "Storytime with dramatic pacing",
    "Fast punchy hook-first",
    "Calm first-person retelling",
]

# Common OpenRouter text models offered in the dropdown.
MODEL_SUGGESTIONS = [
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3.7-sonnet",
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "google/gemini-2.0-flash-001",
    "meta-llama/llama-3.3-70b-instruct",
]

DEFAULT_MODEL = os.getenv("OPENROUTER_TEXT_MODEL") or MODEL_SUGGESTIONS[0]

DEFAULT_SETTINGS = {
    "subreddits": DEFAULT_SUBREDDITS,
    "sort": "top",
    "time_filter": "week",
    "limit": 50,
    "min_words": 90,
    "max_words": 1200,
    "hide_nsfw": True,
    "model": DEFAULT_MODEL,
    "language": "English",
    "script_style": SCRIPT_STYLES[0],
    "target_seconds": 50,
}


def get_api_key() -> str:
    return os.getenv("OPENROUTER_API_KEY", "").strip()


def load_settings() -> dict:
    settings = dict(DEFAULT_SETTINGS)
    if SETTINGS_PATH.exists():
        try:
            saved = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                settings.update(saved)
        except (json.JSONDecodeError, OSError):
            pass
    # Never trust a saved empty subreddit list.
    if not settings.get("subreddits"):
        settings["subreddits"] = list(DEFAULT_SUBREDDITS)
    return settings


def save_settings(settings: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
