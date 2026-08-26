"""Fetch stories from Reddit without API keys.

Two sources, tried as a cascade:

1. Reddit's official public JSON (``www.reddit.com/r/.../top.json``). Freshest
   data and real hot/top/new/rising sorting. Works from residential IPs but is
   blocked (403 HTML page) from many datacenter / cloud IPs.
2. pullpush.io — the free Pushshift-successor archive. Always reachable, no
   keys. One subreddit per request, sorted by score (proven top stories).

``fetch_feed`` returns the stories plus a short label saying which source served
them, so the UI can be honest about what the user is looking at.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import requests

from .models import Story

USER_AGENT = "desktop:reddit-script-gen:1.0 (by u/anonymous)"
REDDIT_BASE = "https://www.reddit.com"
PULLPUSH_URL = "https://api.pullpush.io/reddit/search/submission/"
REMOVED_MARKERS = {"[removed]", "[deleted]", ""}


class RedditError(Exception):
    pass


@dataclass
class FeedResult:
    stories: list[Story]
    source: str  # "Reddit (live)" or "pullpush.io (archive)"
    errors: list[str] = field(default_factory=list)


def _clean(stories: list[Story]) -> list[Story]:
    out = []
    for s in stories:
        if s.selftext in REMOVED_MARKERS:
            continue
        out.append(s)
    return out


# --------------------------------------------------------------------------- #
# Source 1: official Reddit JSON (multireddit, single request)
# --------------------------------------------------------------------------- #
def fetch_official(
    subreddits: list[str],
    sort: str = "top",
    time_filter: str = "week",
    limit: int = 50,
    timeout: int = 25,
) -> list[Story]:
    joined = "+".join(s.strip() for s in subreddits if s.strip())
    url = f"{REDDIT_BASE}/r/{joined}/{sort}.json"
    params = {"limit": max(1, min(int(limit), 100)), "raw_json": 1}
    if sort == "top":
        params["t"] = time_filter

    try:
        resp = requests.get(
            url,
            params=params,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise RedditError(f"network: {exc}") from exc

    if resp.status_code == 403:
        raise RedditError("blocked-403")
    if resp.status_code == 429:
        raise RedditError("rate-limited-429")
    try:
        resp.raise_for_status()
        payload = resp.json()
    except (requests.HTTPError, ValueError) as exc:
        raise RedditError(f"bad-response-{resp.status_code}") from exc

    stories = []
    for child in payload.get("data", {}).get("children", []):
        data = child.get("data", {})
        if child.get("kind") != "t3" or data.get("stickied"):
            continue
        stories.append(Story.from_json(data))
    return _clean(stories)


# --------------------------------------------------------------------------- #
# Source 2: pullpush.io archive (per-subreddit, sorted by score)
# --------------------------------------------------------------------------- #
def fetch_pullpush_sub(
    subreddit: str,
    sort: str = "top",
    size: int = 20,
    timeout: int = 30,
) -> list[Story]:
    sort_type = "created_utc" if sort == "new" else "score"
    params = {
        "subreddit": subreddit.strip(),
        "is_self": "true",
        "sort": "desc",
        "sort_type": sort_type,
        "size": max(1, min(int(size), 100)),
    }
    try:
        resp = requests.get(
            PULLPUSH_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise RedditError(f"pullpush {subreddit}: {exc}") from exc

    stories = []
    for data in payload.get("data", []):
        if data.get("stickied"):
            continue
        stories.append(Story.from_json(data))
    return _clean(stories)


def fetch_pullpush(
    subreddits: list[str],
    sort: str = "top",
    limit: int = 50,
    max_subs: int = 10,
) -> tuple[list[Story], list[str]]:
    subs = [s for s in subreddits if s.strip()][:max_subs]
    if not subs:
        return [], []
    per_sub = max(5, min(40, -(-limit // len(subs)) + 3))  # ceil-ish, a little extra
    stories: list[Story] = []
    errors: list[str] = []
    for sub in subs:
        try:
            stories.extend(fetch_pullpush_sub(sub, sort=sort, size=per_sub))
        except RedditError as exc:
            errors.append(str(exc))
    return stories, errors


# --------------------------------------------------------------------------- #
# Cascade entry point
# --------------------------------------------------------------------------- #
def fetch_feed(
    subreddits: list[str],
    sort: str = "top",
    time_filter: str = "week",
    limit: int = 50,
    prefer: str = "auto",  # "auto" | "official" | "pullpush"
) -> FeedResult:
    if not subreddits:
        return FeedResult([], "—")

    if prefer in ("auto", "official"):
        try:
            stories = fetch_official(subreddits, sort, time_filter, limit)
            return FeedResult(stories, "Reddit (live)")
        except RedditError as exc:
            if prefer == "official":
                raise
            # auto: fall through to pullpush
            fallback_note = str(exc)

    stories, errors = fetch_pullpush(subreddits, sort=sort, limit=limit)
    if not stories and prefer == "auto":
        errors.insert(0, f"Reddit live недоступен ({fallback_note}); pullpush тоже пуст.")
    return FeedResult(stories, "pullpush.io (archive)", errors)


def apply_filters(
    stories: list[Story],
    min_words: int = 0,
    max_words: int = 100000,
    hide_nsfw: bool = True,
    sort_by: str = "score",
) -> list[Story]:
    seen: set[str] = set()
    result: list[Story] = []
    for story in stories:
        if not story.id or story.id in seen:
            continue
        seen.add(story.id)
        if hide_nsfw and story.over_18:
            continue
        if not (min_words <= story.word_count <= max_words):
            continue
        result.append(story)

    key = {
        "score": lambda s: s.score,
        "comments": lambda s: s.num_comments,
        "new": lambda s: s.created_utc,
    }.get(sort_by)
    if key:
        result.sort(key=key, reverse=True)
    return result
