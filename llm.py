# -*- coding: utf-8 -*-
"""
Тонкая обёртка над OpenAI API для вызовов LLM (можно заменить на другого провайдера).
"""

import os
from typing import Optional

# Используем openai пакет (работает и с OpenAI, и с совместимыми API)
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore


def get_client() -> Optional["OpenAI"]:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")  # для локальных/прокси
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url=base_url or None)


def complete(
    messages: list[dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> str:
    """Один запрос к модели. Возвращает текст ответа или пустую строку при ошибке."""
    client = get_client()
    if not client:
        return ""
    try:
        r = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        if r.choices and r.choices[0].message.content:
            return r.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM error] {e}")
    return ""
