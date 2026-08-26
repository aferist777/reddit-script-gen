"""Prompt construction for turning a Reddit story into a short-form script."""

from __future__ import annotations

from .models import Story

SYSTEM_PROMPT = (
    "You are a professional short-form video scriptwriter who turns Reddit "
    "stories into viral vertical (9:16) voiceover scripts for Reels, Shorts "
    "and TikTok. You keep the original story's drama and twist, retell it "
    "tightly in the first person, and write narration that a text-to-speech "
    "voice will read over background footage. You never invent facts that "
    "contradict the source, but you may trim, reorder for tension, and sharpen "
    "the hook."
)

OUTPUT_FORMAT = """Return the result as Markdown with exactly these sections:

## Hook
One spoken line (max ~12 words) that makes the viewer stop scrolling. No emojis.

## Title
A punchy on-screen title / caption for the post (max ~70 chars).

## Script
The full narration, first person, broken into short beats — one short sentence
per line. Aim for {target_seconds} seconds at ~150 words per minute
(~{word_target} words). Conversational, build tension, land the twist near the end.

## Visual notes
3-6 bullet points: what b-roll / on-screen text / scene fits each part.

## Hashtags
6-10 relevant hashtags on one line.
"""


def build_messages(
    story: Story,
    language: str = "English",
    style: str = "Short-form narration (Reels / Shorts / TikTok)",
    target_seconds: int = 50,
) -> list[dict]:
    word_target = max(40, round(target_seconds / 60 * 150))
    output_format = OUTPUT_FORMAT.format(
        target_seconds=target_seconds, word_target=word_target
    )

    user = f"""Write a short-form video script from this Reddit story.

Style: {style}
Output language: {language}
Target length: about {target_seconds} seconds of narration.

SOURCE STORY (from r/{story.subreddit}):
Title: {story.title}

{story.selftext}

---
{output_format}
Write every section in {language}. Keep the voice authentic and human."""

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]
