"""Thin OpenRouter chat-completions client."""

from __future__ import annotations

import requests

from .config import get_api_key

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMError(Exception):
    pass


def chat(
    messages: list[dict],
    model: str,
    api_key: str | None = None,
    temperature: float = 0.8,
    max_tokens: int = 1800,
    timeout: int = 180,
) -> str:
    key = (api_key or get_api_key()).strip()
    if not key:
        raise LLMError(
            "Нет OPENROUTER_API_KEY. Создай файл .env и добавь ключ "
            "(см. .env.example)."
        )

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost/reddit-script-gen",
        "X-Title": "Reddit Script Gen",
    }
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=timeout)
    except requests.RequestException as exc:
        raise LLMError(f"Сеть недоступна: {exc}") from exc

    if resp.status_code == 401:
        raise LLMError("OpenRouter 401: неверный или просроченный API-ключ.")
    if resp.status_code == 402:
        raise LLMError("OpenRouter 402: недостаточно кредитов на счёте.")
    if resp.status_code == 429:
        raise LLMError("OpenRouter 429: слишком много запросов, подожди немного.")

    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        detail = _error_detail(resp)
        raise LLMError(f"OpenRouter {resp.status_code}: {detail}") from exc

    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError, AttributeError) as exc:
        raise LLMError(f"Неожиданный ответ OpenRouter: {resp.text[:400]}") from exc


def _error_detail(resp: requests.Response) -> str:
    try:
        return resp.json().get("error", {}).get("message", resp.text[:200])
    except ValueError:
        return resp.text[:200]
